-- Clean leads: remove duplicates, standardize text, fill unknowns
CREATE TABLE leads AS
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY lead_id ORDER BY days_since_last_activity) AS rn
    FROM raw_leads
)
SELECT
    lead_id,
    -- standardize inconsistent capitalization (e.g. 'HOSPITAL' -> 'Hospital')
    UPPER(SUBSTR(org_type, 1, 1)) || LOWER(SUBSTR(org_type, 2))  AS org_type,
    COALESCE(specialty, 'Unknown')                                AS specialty,
    COALESCE(region, 'Unknown')                                   AS region,
    lead_source,
    owner,
    employee_count,
    has_email,
    has_phone,
    decision_maker_identified,
    website_visits_90d,
    email_opens_90d,
    days_since_last_activity,
    research_complete
FROM ranked
WHERE rn = 1;
