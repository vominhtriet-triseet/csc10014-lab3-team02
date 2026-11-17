-- Lab 5 Homework H2 (vominhtriet-triseet)
-- Question: For each intent, what share of rated answers got a thumbs-up?
--           The intent with the lowest share is the first one to improve.
-- Data: python scripts/migrate.py assistant.db && python scripts/seed.py assistant.db 300

SELECT i.intent,
       COUNT(*) AS ratings,
       SUM(f.rating = 1) AS thumbs_up,
       SUM(f.rating = -1) AS thumbs_down,
       ROUND(100.0 * SUM(f.rating = 1) / COUNT(*), 1) AS satisfied_pct
FROM feedback f
JOIN interaction i ON i.request_id = f.request_id
GROUP BY i.intent
ORDER BY satisfied_pct, ratings DESC;

-- Result:
-- intent    ratings  thumbs_up  thumbs_down  satisfied_pct
-- --------  -------  ---------  -----------  -------------
-- unknown   8        0          8            0.0
-- rule      47       29         18           61.7
-- greeting  7        5          2            71.4
-- office    13       10         3            76.9
-- fee       21       17         4            81.0
--
-- Reading: "unknown" answers are never liked (the bot did not know), and
-- "rule" answers are the weakest real answers: 18 of the 35 thumbs-down.
-- Improving handbook rule answers would help the most students.
