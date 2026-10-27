-- Data quality report: completeness of key fields and duplicate leads
SELECT
    COUNT(*)                                                   AS total_rows,
    COUNT(DISTINCT lead_id)                                    AS unique_leads,
    COUNT(*) - COUNT(DISTINCT lead_id)                         AS duplicate_rows,
    ROUND(100.0 * SUM(CASE WHEN has_phone = 0 THEN 1 ELSE 0 END) / COUNT(*), 1)  AS pct_missing_phone,
    ROUND(100.0 * SUM(CASE WHEN has_email = 0 THEN 1 ELSE 0 END) / COUNT(*), 1)  AS pct_missing_email,
    ROUND(100.0 * SUM(CASE WHEN specialty IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_specialty,
    ROUND(100.0 * SUM(CASE WHEN employee_count IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_size
FROM raw_leads;
