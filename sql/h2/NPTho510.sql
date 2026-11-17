-- Q4 percentage of answers used a backup path
SELECT
    COUNT(*) AS total_questions,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS fallback_answers,
    ROUND(
        100.0 * SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS fallback_percentage
FROM interaction;