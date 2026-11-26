-- Homework H2
-- Student: kq244466666-commits
--
-- Question:
-- How much slower is the backup path (degraded = 1)
-- compared to the normal path (degraded = 0)
-- for each resolved intent?

WITH path_stats AS (
    SELECT
        intent,
        AVG(CASE WHEN degraded = 0 THEN latency_ms END) AS normal_avg,
        AVG(CASE WHEN degraded = 1 THEN latency_ms END) AS backup_avg
    FROM interaction
    WHERE resolved = 1
    GROUP BY intent
)
SELECT
    intent,
    ROUND(normal_avg, 1) AS normal_avg_latency_ms,
    ROUND(backup_avg, 1) AS backup_avg_latency_ms,
    ROUND(backup_avg - normal_avg, 1) AS slower_by_ms,
    ROUND(backup_avg / normal_avg, 2) AS slower_times,
    ROUND((backup_avg / normal_avg - 1) * 100, 1) AS slower_percent
FROM path_stats
ORDER BY
    slower_times DESC,
    intent ASC;


    ```sql
-- Result on assistant.db (300 seeded interactions):
-- fee     | 4.8 | 21.2  | 16.4  | 4.42 | 341.8
-- rule    | 43.3 | 178.7 | 135.4 | 4.13 | 312.7
-- greeting| 1.9 | 7.8   | 5.9   | 4.04 | 304.3
-- office  | 3.2 | 12.1  | 8.9   | 3.77 | 277.4
```