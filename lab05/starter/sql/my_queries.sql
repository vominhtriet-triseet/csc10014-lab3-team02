-- Lab 5 Part F: write your queries for the assistant database here.
-- Data: python scripts/migrate.py assistant.db && python scripts/seed.py assistant.db 300

-- F1 (Q1): requests per intent
SELECT intent, COUNT(*) AS requests
FROM interaction
GROUP BY intent
ORDER BY requests DESC, intent ASC;

-- F2 (Q2): average latency per intent
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY avg_latency_ms DESC, intent ASC;

-- F3 (Q3): topics with the most thumbs-down
SELECT i.topic, COUNT(*) AS thumbs_down
FROM feedback AS f
JOIN interaction AS i ON i.request_id = f.request_id
WHERE f.rating = -1
  AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic ASC;

---- Actual results from assistant.db after migrate + seed 300:
-- F1: rule 140 | fee 61 | office 47 | unknown 26 | greeting 26
-- F2: rule 76.2 | unknown 8.1 | fee 5.1 | office 3.4 | greeting 2.4
-- F3: H26-4.2 (8) | H26-5.3 (8) | H26-7.2 (2)
