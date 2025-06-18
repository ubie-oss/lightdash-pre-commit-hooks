# Lightdash Schemas

## Lightdash dbt 2.0

This is the official schema provided by Lightdash.
That doesn't support the new schema at dbt Core v1.10 yet at the time of writing.

<https://github.com/lightdash/lightdash/tree/main/packages/common/src/schemas/json>

## Lightdash dbt 2.5

I modified the schema of the official schema to catch up with the schema changes at dbt Core v1.10.
Specifically, the `meta` configs at the model level and the column level are updated to match the new schema.

<https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v1.10>
