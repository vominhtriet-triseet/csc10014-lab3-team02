-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent
SELECT
    intent,
    COUNT(*) AS request_count
FROM interaction
GROUP BY intent
ORDER BY intent;
-- Q2 average latency per intent
SELECT
    intent,
    ROUND(AVG(latency_ms), 1) AS average_latency_ms
FROM interaction
GROUP BY intent
ORDER BY intent;
-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT
    i.topic,
    COUNT(*) AS thumbs_down_count
FROM feedback AS f
JOIN interaction AS i
    ON f.request_id = i.request_id
WHERE f.rating = -1
GROUP BY i.topic
ORDER BY thumbs_down_count DESC, i.topic;