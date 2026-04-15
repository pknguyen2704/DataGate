import os
import subprocess
import sys

# 1. Ensure dependencies are present in the dbt container
def install_deps():
    try:
        import psycopg2
        import yaml
    except ImportError:
        print("📦 Installing missing dependencies (psycopg2-binary, PyYAML)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "PyYAML"])

install_deps()
import psycopg2
from psycopg2.extras import RealDictCursor
import yaml

# 2. Configuration (Using environment variables for Docker flexibility)
DB_HOST = os.getenv("DATAGATE_DB_HOST", "datagate_database")
DB_USER = os.getenv("DATAGATE_DB_USER", "admin")
DB_PASS = os.getenv("DATAGATE_DB_PASS", "datagatepassword")
DB_NAME = os.getenv("DATAGATE_DB_NAME", "datagate")
DB_PORT = os.getenv("DATAGATE_DB_PORT", "5432")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TARGET_SCHEMA_PATH = "./models/silver/schema.yml"

def translate_to_sql(expression, column_name):
    """Translates common profiling descriptors to valid SQL expressions."""
    import re
    if not expression: return "TRUE"
    # Clean up string: remove newlines and extra spaces
    expr = " ".join(expression.strip().split())
    
    # 1. Null/Completeness
    if "isComplete" in expr:
        return f"{column_name} IS NOT NULL"
    
    # 2. Positivity/Range
    if "isNonNegative" in expr:
        return f"TRY_CAST({column_name} AS DOUBLE) >= 0"
    
    if "hasMin" in expr or "hasMax" in expr:
        op = ">=" if "hasMin" in expr else "<="
        match = re.search(r"(?:hasMin|hasMax).*?(\d+\.?\d*)", expr)
        if match:
            return f"TRY_CAST({column_name} AS DOUBLE) {op} {match.group(1)}"
    
    # 3. List Membership / isContainedIn (Handles both Array_1_2 and Array("1","2"))
    if "isContainedIn" in expr:
        # Extract values inside Array(...) or after Array_
        array_match = re.search(r"Array\s*\((.*?)\)", expr, re.IGNORECASE)
        if array_match:
            content = array_match.group(1)
            raw_values = re.findall(r'"([^"]*)"|\'([^\']*)\'|(\d+\.?\d*)', content)
            values = [v[0] or v[1] or v[2] for v in raw_values if any(v)]
        else:
            # Fallback to the underscore format
            array_part = expr.split("Array_")[-1]
            values = [v for v in array_part.split("_") if v and v not in ["Some", "It"]]

        final_values = []
        for v in values:
            v_clean = v.strip()
            if v_clean.replace(".", "").replace("-", "").isdigit():
                final_values.append(v_clean)
            else:
                final_values.append(f"'{v_clean}'")
        
        if final_values:
            return f"{column_name} IN ({', '.join(final_values)})"

    # 4. Length
    if "Length" in expr:
        op = "<=" if "hasMaxLength" in expr else ">="
        match = re.search(r"Length.*?(\d+)", expr)
        if match:
            return f"LENGTH(CAST({column_name} AS VARCHAR)) {op} {match.group(1)}"
    
    # 5. Aggregate Rules
    if "hasMean" in expr:
        match = re.search(r"hasMean.*?(\d+\.?\d*)", expr)
        if match:
            target = match.group(1)
            avg_expr = f"AVG(TRY_CAST({column_name} AS DOUBLE))"
            return f"ABS({avg_expr} - {target}) < (ABS({target}) * 0.1 + 0.01)"

    if "hasStandardDeviation" in expr:
        match = re.search(r"hasStandardDeviation.*?(\d+\.?\d*)", expr)
        if match:
            target = match.group(1)
            std_expr = f"STDDEV_SAMP(TRY_CAST({column_name} AS DOUBLE))"
            return f"ABS({std_expr} - {target}) < (ABS({target}) * 0.2 + 0.01)"
    
    # 6. Metadata Placeholders
    if "hasCompleteness" in expr:
        match = re.search(r"(\d+\.?\d*)", expr.split("hasCompleteness")[-1])
        if match:
            target = match.group(1)
            return f"CAST(COUNT({column_name}) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE) >= {target}"

    # Fallback Logic: 
    # If it starts with common profiling prefixes, it's a descriptor that failed translation
    if expr.startswith(('is', 'has', 'Standard')):
        return f"TRUE -- Failed to translate descriptor: {expr}"

    # If it's already SQL-like, return as is.
    if any(op in expr for op in [' > ', ' < ', ' = ', ' IS ', ' IN ']):
        return expr
        
    return f"TRUE -- Unrecognized expression: {expr}"

def generate_dbt_test(rule_type, expression, column_name):
    """Maps rule types to standard or custom dbt tests with arguments."""
    if rule_type == 'not_null': return 'not_null'
    if rule_type == 'unique': return 'unique'
    
    # Translate the expression to SQL
    sql_expression = translate_to_sql(expression, column_name)
    
    if expression:
        return {rule_type: {'expression': sql_expression}}
        
    return rule_type

def main():
    print(f"🔗 Connecting to DataGate DB at {DB_HOST}...")
    try:
        conn = psycopg2.connect(DB_URL)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT table_name, column_name, rule_type, rule_expression FROM active_rules WHERE is_active = true")
            rules = cur.fetchall()
        
        if not rules:
            print("⚠️ No active rules found in database.")
            return

        # Build YAML structure with deduplication
        models_data = {}
        for rule in rules:
            table = rule['table_name'].split('.')[-1]
            col = rule['column_name']
            test = generate_dbt_test(rule['rule_type'], rule['rule_expression'], col)
            
            if table not in models_data: models_data[table] = {}
            if col not in models_data[table]: models_data[table][col] = []
            
            # Use a hashable representation to check for duplicates
            test_repr = yaml.dump(test, sort_keys=True)
            if not any(yaml.dump(existing, sort_keys=True) == test_repr for existing in models_data[table][col]):
                models_data[table][col].append(test)

        schema_yaml = {
            'version': 2,
            'models': [
                {'name': t, 'columns': [{'name': c, 'tests': ts} for c, ts in cols.items()]}
                for t, cols in models_data.items()
            ]
        }

        with open(TARGET_SCHEMA_PATH, 'w') as f:
            f.write("# AUTO-GENERATED by DataGate Rules Engine\n")
            yaml.dump(schema_yaml, f, sort_keys=False, indent=2)
        
        print(f"✅ Successfully updated {TARGET_SCHEMA_PATH}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
