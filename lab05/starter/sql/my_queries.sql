-- Lab 5 Part F: write your queries for the assistant database here.
-- Data: python scripts/migrate.py assistant.db && python scripts/seed.py assistant.db 300

-- Q1 requests per intent  (F1: How many questions per intent?)
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC, intent;
-- intent    requests
-- --------  --------
-- rule      140
-- fee       61
-- office    47
-- greeting  26
-- unknown   26

-- Q2 average latency per intent  (F2: Average time taken per intent?)
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC;
-- intent    avg_latency_ms
-- --------  --------------
-- rule      76.2
-- unknown   8.1
-- fee       5.1
-- office    3.4
-- greeting  2.4

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)  (F3)
SELECT i.topic, COUNT(*) AS thumbs_down
FROM interaction i
JOIN feedback f ON f.request_id = i.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic;
-- topic    thumbs_down
-- -------  -----------
-- H26-4.2  8
-- H26-5.3  8
-- H26-7.2  2
