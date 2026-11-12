-- Lab 5 Homework H2 (reiryuka)
-- Q4 intent with the highest average latency
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC
LIMIT 1;
-- intent  avg_latency_ms
-- ------  --------------
-- rule    76.2