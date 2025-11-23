{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}

        {{ default_schema }}

    {%- else -%}

        {#- In production, use custom schema without prefix -#}
        {#- This allows us to use 'schema: bronze_raw' in model config -#}
        {{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}
