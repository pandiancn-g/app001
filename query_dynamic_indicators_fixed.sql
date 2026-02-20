-- Fixed query: Cast indicator_id types for ClickHouse JOIN compatibility
-- i.indicator_id is Nullable(Float64), o.INDICATOR_ID is Nullable(String)

SELECT *
FROM SC_ENT_DWH_PRD.VW_DYNAMIC_OFFICIAL_INDICATORS i
INNER JOIN SC_ENT_DWH_PRD.VW_SCAD_IFP_DOMAIN_MAPPING m ON i.theme_id = m.themeid
INNER JOIN SC_ENT_DWH_PRD.VW_STATISTICAL_IND_OVERVIEW o ON toString(i.indicator_id) = o.INDICATOR_ID;

-- Alternative: cast String to Float64 (use if INDICATOR_ID contains numeric values only)
-- ON i.indicator_id = toFloat64OrNull(o.INDICATOR_ID)
