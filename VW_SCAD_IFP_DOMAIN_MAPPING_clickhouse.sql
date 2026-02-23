-- ClickHouse View: Returns specific theme/category records with active status
-- Columns: themeid, categoryid, active
-- Note: ClickHouse does not support SQL Server VALUES syntax; using UNION ALL instead

CREATE VIEW SC_ENT_DWH_PRD.VW_SCAD_IFP_DOMAIN_MAPPING AS
SELECT themeid, categoryid, active
FROM (
    SELECT 7 AS themeid, 2593459 AS categoryid, 1 AS active
    UNION ALL SELECT 9, 2593509, 1
    UNION ALL SELECT 8, 2593568, 1
    UNION ALL SELECT 14, 2593953, 1
    UNION ALL SELECT 13, 2594017, 1
    UNION ALL SELECT 12, 2594081, 1
    UNION ALL SELECT 17, 2593666, 1
    UNION ALL SELECT 15, 2593702, 1
    UNION ALL SELECT 16, 2593731, 1
    UNION ALL SELECT 18, 2593767, 1
    UNION ALL SELECT 19, 2593336, 1
    UNION ALL SELECT 20, 2593379, 1
    UNION ALL SELECT 22, 2593841, 1
    UNION ALL SELECT 21, 2593901, 1
);

-- To run the view and see the records:
-- SELECT * FROM SC_ENT_DWH_PRD.VW_SCAD_IFP_DOMAIN_MAPPING;
