{% test dbt_utils_positive_value(model, column_name) %}
/*
  Generic test: assert the column has no negative values.
  Usage in schema.yml:
      tests:
        - dbt_utils_positive_value:
            column_name: my_column
*/
SELECT
    {{ column_name }}
FROM {{ model }}
WHERE {{ column_name }} < 0

{% endtest %}
