-- Transparent lead score (0-100) and Top-50 queue
-- Weights: completeness 30, engagement 35, readiness 35
CREATE TABLE scored_leads AS
WITH components AS (
    SELECT *,
        -- Contact completeness (0-30)
        (10 * has_email) + (10 * has_phone) + (10 * decision_maker_identified)          AS completeness_pts,
        -- Engagement (0-35): visits and opens capped, recency decays
        MIN(website_visits_90d, 8) * 2
          + MIN(email_opens_90d, 6) * 2
          + CASE WHEN days_since_last_activity <= 14 THEN 7
                 WHEN days_since_last_activity <= 45 THEN 4
                 ELSE 0 END                                                             AS engagement_pts,
        -- Outreach readiness (0-35)
        (15 * research_complete)
          + CASE WHEN lead_source IN ('Referral', 'Webinar', 'Website form') THEN 12 ELSE 4 END
          + CASE WHEN org_type IN ('Hospital', 'Medical school', 'Pharmaceutical company') THEN 8 ELSE 3 END AS readiness_pts
    FROM leads
)
SELECT *,
       completeness_pts + engagement_pts + readiness_pts                                 AS lead_score,
       RANK() OVER (ORDER BY completeness_pts + engagement_pts + readiness_pts DESC,
                             days_since_last_activity ASC)                                AS overall_rank,
       RANK() OVER (PARTITION BY owner
                    ORDER BY completeness_pts + engagement_pts + readiness_pts DESC)      AS rank_within_owner
FROM components;
