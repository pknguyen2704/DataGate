{% test RowLevelConstraint(model, column_name, expression) %}
    {% set is_aggregate = "AVG(" in expression or "STDDEV" in expression or "COUNT(" in expression %}
    
    {% if is_aggregate %}
        select 1
        from (
            select {{ expression }} as actual_val
            from {{ model }}
        )
        where not ( actual_val )
    {% else %}
        select *
        from {{ model }}
        where not ( {{ expression }} )
    {% endif %}
{% endtest %}

{% test RowLevelAssertedConstraint(model, column_name, expression) %}
    {% set is_aggregate = "AVG(" in expression or "STDDEV" in expression or "COUNT(" in expression %}
    
    {% if is_aggregate %}
        select 1
        from (
            select {{ expression }} as actual_val
            from {{ model }}
        )
        where not ( actual_val )
    {% else %}
        select *
        from {{ model }}
        where not ( {{ expression }} )
    {% endif %}
{% endtest %}

{% test NamedConstraint(model, column_name, expression) %}
    {% set is_aggregate = "AVG(" in expression or "STDDEV" in expression or "COUNT(" in expression %}
    
    {% if is_aggregate %}
        select 1
        from (
            select {{ expression }} as actual_val
            from {{ model }}
        )
        where not ( actual_val )
    {% else %}
        select *
        from {{ model }}
        where not ( {{ expression }} )
    {% endif %}
{% endtest %}
