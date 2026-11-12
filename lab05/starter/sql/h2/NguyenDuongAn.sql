-- Question:
-- Which topics receive the highest number of requests?

-- Query:
SELECT
    topic,
    COUNT(*) AS request_count
FROM interaction
GROUP BY topic
ORDER BY request_count DESC, topic;

-- Result:
topic	    request_count
	        160
H26-5.3	    84
H26-4.2	    45
H26-7.2	    11


