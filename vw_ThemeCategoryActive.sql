-- SQL Server View: Returns specific theme/category records with active status
-- Columns: themeid, categoryid, active

CREATE VIEW vw_ThemeCategoryActive AS
SELECT themeid, categoryid, active
FROM (VALUES
    (7, 2593459, 1),
    (9, 2593509, 1),
    (8, 2593568, 1),
    (14, 2593953, 1),
    (13, 2594017, 1),
    (12, 2594081, 1),
    (17, 2593666, 1),
    (15, 2593702, 1),
    (16, 2593731, 1),
    (18, 2593767, 1),
    (19, 2593336, 1),
    (20, 2593379, 1),
    (22, 2593841, 1),
    (21, 2593901, 1)
) AS T(themeid, categoryid, active);

-- To run the view and see the records:
-- SELECT * FROM vw_ThemeCategoryActive;
