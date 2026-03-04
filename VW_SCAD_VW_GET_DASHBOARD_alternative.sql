-- ALTERNATIVE: Use VW_STATISTICAL_INDICATORS for INSERT_DATE
-- Use when VW_STATISTICAL_IND_OVERVIEW is built from VW_STATISTICAL_INDICATORS and shares the same
-- INDICATOR_ID + INSERT_DATE key. The "latest" subquery uses VW_STATISTICAL_INDICATORS (where you
-- confirmed INSERT_DATE exists).

CREATE OR REPLACE VIEW SC_ENT_DWH_PRD.VW_SCAD_VW_GET_DASHBOARD
(
    `domain_id` Nullable(String),
    `domain` Nullable(String),
    `domain_ar` Nullable(String),
    `theme_id` Nullable(String),
    `theme` Nullable(String),
    `theme_ar` Nullable(String),
    `subtheme_id` Nullable(String),
    `subtheme` Nullable(String),
    `subtheme_ar` Nullable(String),
    `product_id` Nullable(String),
    `product` Nullable(String),
    `product_ar` Nullable(String),
    `INDICATOR_ID` Nullable(String),
    `component_title` Nullable(String),
    `component_title_ar` Nullable(String),
    `yAxisLabel` Nullable(String),
    `updated` Nullable(String),
    `VALUE` Nullable(Float64),
    `YEARLY_COMPARE_VALUE` Nullable(Float64),
    `YEARLY_CHANGE_VALUE` Nullable(Float64),
    `QUARTERLY_COMPARE_VALUE` Nullable(Float64),
    `QUARTERLY_CHANGE_VALUE` Nullable(Float64),
    `MONTHLY_COMPARE_VALUE` Nullable(Float64),
    `MONTHLY_CHANGE_VALUE` Nullable(Float64),
    `MONTHLY` Nullable(Float64),
    `QUARTERLY` Nullable(Float64),
    `YEARLY` Nullable(Float64),
    `categoryid` UInt32,
    `OBS_DT` Nullable(String),
    `CONFIGURATION` Nullable(String)
)
AS SELECT
    domain_id,
    domain,
    domain_ar,
    theme_id,
    theme,
    theme_ar,
    subtheme_id,
    subtheme,
    subtheme_ar,
    product_id,
    product,
    product_ar,
    o.INDICATOR_ID AS INDICATOR_ID,
    i.component_title,
    i.component_title_ar,
    i.yAxisLabel,
    i.updated,
    o.VALUE,
    o.YEARLY_COMPARE_VALUE,
    o.YEARLY_CHANGE_VALUE,
    o.QUARTERLY_COMPARE_VALUE,
    o.QUARTERLY_CHANGE_VALUE,
    o.MONTHLY_COMPARE_VALUE,
    o.MONTHLY_CHANGE_VALUE,
    o.MONTHLY,
    o.QUARTERLY,
    o.YEARLY,
    m.categoryid,
    o.OBS_DT,
    vdjc.CONFIGURATION
FROM SC_ENT_DWH_PRD.VW_DYNAMIC_OFFICIAL_INDICATORS AS i
INNER JOIN SC_ENT_DWH_PRD.VW_SCAD_IFP_DOMAIN_MAPPING AS m ON i.theme_id = m.themeid
INNER JOIN SC_ENT_DWH_PRD.VW_STATISTICAL_IND_OVERVIEW AS o ON toString(i.indicator_id) = o.INDICATOR_ID
INNER JOIN (
    SELECT INDICATOR_ID, max(INSERT_DATE) AS latest_insert_date
    FROM SC_ENT_DWH_PRD.VW_STATISTICAL_INDICATORS
    GROUP BY INDICATOR_ID
) AS latest ON o.INDICATOR_ID = latest.INDICATOR_ID AND o.INSERT_DATE = latest.latest_insert_date
INNER JOIN SC_ENT_DWH_PRD.VW_DYNAMIC_JSON_CONFIG AS vdjc ON vdjc.INDICATOR_ID = i.indicator_id
WHERE i.approved = 1;
