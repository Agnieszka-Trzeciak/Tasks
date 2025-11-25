# Main transformation
CREATE TABLE task1_summary
SELECT year AS publication_year, 
		COUNT(ID) AS number_of_titles,
        CAST(AVG(dollar_price) AS DECIMAL(10,2)) as average_price
FROM # Temporary table
	(SELECT ID,year,
	CASE
		WHEN price LIKE '€%' THEN CAST(REPLACE(price, '€', '') AS DECIMAL(6, 2))*1.2 # If Euro, multiply by 1.2
		ELSE CAST(REPLACE(price, '$', '') AS DECIMAL(6, 2))
	END AS dollar_price # Price as number in dollars
	FROM task1_d_processed) AS temp
GROUP BY publication_year
ORDER BY publication_year;

# Row count of output
SELECT count(publication_year)
FROM task1_summary;

# Summary of output
SELECT *
FROM task1_summary;
