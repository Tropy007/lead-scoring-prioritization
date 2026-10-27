-- KPI scorecard by lead source
SELECT
    lead_source,
    COUNT(*)                                                        AS leads,
    ROUND(AVG(lead_score), 1)                                       AS avg_score,
    SUM(CASE WHEN overall_rank <= 50 THEN 1 ELSE 0 END)             AS in_top_50,
    ROUND(100.0 * AVG(has_phone AND has_email AND decision_maker_identified), 1) AS pct_contact_ready
FROM scored_leads
GROUP BY lead_source
ORDER BY avg_score DESC;
