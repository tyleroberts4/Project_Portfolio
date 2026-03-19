USE `GSB_520_Project_DB`;

-- Identify which states hold the largest share of our approved loan exposure and how risky that portfolio is on average. 
-- This helps management focus on high risk or high volume regions.

SELECT
    pc.state,
    COUNT(*) AS loan_count,
    SUM(l.loan_amount) AS total_loan_amount,
    AVG(l.risk_score) AS avg_risk_score
FROM LOAN l
JOIN CUSTOMER_has_LOAN chl
    ON l.loan_id = chl.loan_id
JOIN CUSTOMER c
    ON c.customer_id = chl.CUSTOMER_customer_id
JOIN POSTAL_CODE pc
    ON pc.postal_code = c.POSTAL_Postal_Code
WHERE
    l.status = 'Approved'
GROUP BY
    pc.state
ORDER BY
    avg_risk_score DESC,
    total_loan_amount DESC;

-- Rank customers by accident involvement and driving behavior so risk teams can 
-- flag the riskiest drivers for closer monitoring or policy review.

SELECT
	c.customer_id,
	c.full_name,
	dr.driving_years,
	dr.speeding_count,
	dr.dui_count,
	COUNT(ar.accident_id) AS accidents_in_system
FROM CUSTOMER c
JOIN DRIVING_RECORD dr
	ON dr.driving_record_id = c.DRIVING_RECORD_driving_record_id
LEFT JOIN ACCIDENT_RECORD ar
	ON ar.CUSTOMER_customer_id = c.customer_id
GROUP BY
	c.customer_id,
	c.full_name,
	dr.driving_years,
	dr.speeding_count,
	dr.dui_count
ORDER BY
    accidents_in_system DESC,
	dr.dui_count DESC,
    dr.speeding_count DESC;
    
    
-- Find customers whose total loan balance is above the portfolio average. 
-- High exposure accounts that are important for credit review

SELECT c.customer_id, c.full_name, SUM(l.loan_amount) AS total_loan_amount
FROM CUSTOMER c
JOIN CUSTOMER_has_LOAN chl ON chl.CUSTOMER_customer_id = c.customer_id
JOIN LOAN l ON l.loan_id = chl.loan_id
GROUP BY c.customer_id, c.full_name
HAVING
SUM(l.loan_amount) > (
SELECT AVG(customer_total)
FROM (SELECT SUM(l2.loan_amount) AS customer_total
		FROM CUSTOMER_has_LOAN chl2
		JOIN LOAN l2
		ON l2.loan_id = chl2.loan_id
		GROUP BY chl2.CUSTOMER_customer_id
    	) AS t
	)
ORDER BY
	total_loan_amount DESC;
    
-- Identify locations that have more accidents than the average location. 
-- This supports decisions about pricing, risk zoning, and potential safety or mitigation efforts in specific areas.

SELECT l.location_id, l.area_type, l.local_authority, COUNT(ar.accident_id) AS accident_count
FROM LOCATION l
JOIN ACCIDENT_RECORD ar ON ar.location_id = l.location_id
GROUP BY
l.location_id,
l.area_type,
l.local_authority
HAVING COUNT(ar.accident_id) > (
    	SELECT AVG(accidents_per_location)
    	FROM (SELECT COUNT(*) AS accidents_per_location
		FROM ACCIDENT_RECORD
		GROUP BY location_id) AS x)
ORDER BY
accident_count DESC;
    
--  Find low risk customers with clean driving records and no recorded accidents who also have loans. 
-- This group is ideal for loyalty discounts, cross selling, or targeted marketing offers.

SELECT c.customer_id, c.full_name, pc.state, dr.driving_years, dr.speeding_count, dr.dui_count,dr.accident_count, SUM(l.loan_amount) AS total_loan_amount
FROM CUSTOMER c
JOIN POSTAL_CODE pc ON pc.postal_code = c.POSTAL_Postal_Code
JOIN DRIVING_RECORD dr ON dr.driving_record_id = c.DRIVING_RECORD_driving_record_id
JOIN CUSTOMER_has_LOAN chl ON chl.CUSTOMER_customer_id = c.customer_id
JOIN LOAN l ON l.loan_id = chl.loan_id
LEFT JOIN ACCIDENT_RECORD ar ON ar.CUSTOMER_customer_id = c.customer_id
GROUP BY
c.customer_id, c.full_name, pc.state, dr.driving_years, dr.speeding_count, dr.dui_count, dr.accident_count
HAVING
COUNT(ar.accident_id) = 0
AND dr.dui_count = 0
AND dr.speeding_count <= 1
ORDER BY
total_loan_amount DESC;
    
-- nAmong customers with approved loans, highlight those who both have accidents and significant loan exposure. 
-- This gives a prioritized list for risk review, collections strategy, or adjusted terms.
SELECT
    c.customer_id,
    c.full_name,
    COUNT(DISTINCT ar.accident_id) AS accident_count,
    SUM(l.loan_amount) AS total_loan_amount,
    AVG(l.risk_score) AS avg_risk_score
FROM CUSTOMER c
JOIN CUSTOMER_has_LOAN chl
    ON chl.CUSTOMER_customer_id = c.customer_id
JOIN LOAN l
    ON l.loan_id = chl.loan_id
LEFT JOIN ACCIDENT_RECORD ar
    ON ar.CUSTOMER_customer_id = c.customer_id
WHERE l.status = 'Approved'      -- only approved loans
GROUP BY
    c.customer_id,
    c.full_name
HAVING
    COUNT(DISTINCT ar.accident_id) >= 1
ORDER BY
    accident_count DESC,
    total_loan_amount DESC;