-- Fixed query: Type-compatible JOINs for ClickHouse
-- i.indicator_id: Nullable(Float64)
-- o.INDICATOR_ID: Nullable(String)
-- vdjc.INDICATOR_ID: Nullable(Float64)

SELECT 
    domain_id, domain, theme_id, theme, subtheme_id, subtheme, product_id, product,
    o.INDICATOR_ID, i.component_title, i.yAxisLabel, i.updated,
    o.VALUE, o.YEARLY_COMPARE_VALUE, o.YEARLY_CHANGE_VALUE,
    o.QUARTERLY_COMPARE_VALUE, o.QUARTERLY_CHANGE_VALUE,
    o.MONTHLY_COMPARE_VALUE, o.MONTHLY_CHANGE_VALUE,
    o.MONTHLY, o.QUARTERLY, o.YEARLY,
    m.categoryid
FROM SC_ENT_DWH_PRD.VW_DYNAMIC_OFFICIAL_INDICATORS i
INNER JOIN SC_ENT_DWH_PRD.VW_SCAD_IFP_DOMAIN_MAPPING m ON i.theme_id = m.themeid
INNER JOIN SC_ENT_DWH_PRD.VW_STATISTICAL_IND_OVERVIEW o ON toString(i.indicator_id) = o.INDICATOR_ID
INNER JOIN SC_ENT_DWH_PRD.VW_DYNAMIC_JSON_CONFIG vdjc ON vdjc.INDICATOR_ID = i.indicator_id;
