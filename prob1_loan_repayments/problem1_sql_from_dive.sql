UPDATE e
SET e.repayment_period = e.seq
FROM (
SELECT ROW_NUMBER() OVER (PARTITION BY zip_loan_id ORDER BY repayment_expected_time ASC) AS Seq
, repayment_period
FROM [repayments expected]
) e;
--row number is a serial number for number of rows in a dataset
--with this sql, created an extra metric COUNTING the sequence of repayments with an integer (repayment_period)

/*Create repayment periods by identifying repayment_period_start dates:
If repayment_period = 1 then use the original disbursement date
If repayment_period > 0 then use the previous repayment period's expected date
*/
WITH repay_periods AS (
SELECT e.zip_loan_id
, e.repayment_period
, CASE WHEN e.repayment_period = 1
THEN CAST(b.disbursed_time AS date)
ELSE CAST(e_prev.repayment_expected_time AS DATE)
END "repayment_period_start"
, CAST(e.repayment_expected_time AS DATE) "repayment_period_end"
, e.amount_due
, b.loan_amount_USD
, b.loan_status
, b.number_of_payments
, b.payment_frequency
FROM repayment_expected  e
LEFT JOIN repayment_expected e_prev
ON e.zip_loan_id = e_prev.zip_loan_id
AND e.repayment_period= e_prev.repayment_period + 1
LEFT JOIN full_borrower_info b
ON b.zip_loan_id = e.zip_loan_id
WHERE e.repayment_expected_time <= '11/02/2016' --Filter out future repayment scheudes since they won't have collected data
)
/*Join collected data by aligning collected_time with the expected repayment time periods*/
, collected_data AS (
SELECT p.zip_loan_id
, p.repayment_period
, p.repayment_period_start
, p.repayment_period_end
, p.amount_due
, ISNULL(round(sum(amount_collected),2),0) 'amount_collected'
, loan_amount_USD
, loan_status
, number_of_payments
, payment_frequency
FROM repay_periods p
LEFT JOIN repayment_collected c
ON c.zip_loan_id = p.zip_loan_id
AND c.repayment_collected_time > p.repayment_period_start
AND c.repayment_collected_time <= p.repayment_period_end
GROUP BY p.zip_loan_id
, p.repayment_period
, p.repayment_period_start
, p.repayment_period_end
, p.amount_due
, p.loan_amount_USD
, p.loan_status
, p.number_of_payments
, p.payment_frequency
)
/*Calculate cumulative amount due*/
, collected_data_cumm1 AS (
SELECT c1.zip_loan_id
, c1.repayment_period
, c1.repayment_period_start
, c1.repayment_period_end
, c1.amount_due
, round(sum(c2.amount_due),2) 'cum_amount_due'
, c1.amount_collected
, c1.loan_amount_USD
, c1.loan_status
, c1.number_of_payments
, c1.payment_frequency
FROM collected_data c1
INNER JOIN collected_data c2
ON c1.zip_loan_id = c2.zip_loan_id
AND c1.repayment_period >= c2.repayment_period
GROUP BY c1.zip_loan_id
, c1.repayment_period
, c1.repayment_period_start
, c1.repayment_period_end
, c1.amount_due
, c1.amount_collected
, c1.loan_amount_USD
, c1.loan_status
, c1.number_of_payments
, c1.payment_frequency
)
/*calculate cumulative amount collected*/
, collected_data_cumm2 AS (
SELECT c1.zip_loan_id
, c1.repayment_period
, c1.repayment_period_start
, c1.repayment_period_end
, c1.amount_due
, c1.cum_amount_due
, c1.amount_collected
, round(sum(c2.amount_collected),2) 'cum_amount_collected'
, c1.loan_amount_USD
, c1.loan_status
, c1.number_of_payments
, c1.payment_frequency
FROM collected_data_cumm1 c1
INNER JOIN collected_data_cumm1 c2
ON c1.zip_loan_id = c2.zip_loan_id
AND c1.repayment_period >= c2.repayment_period
GROUP BY c1.zip_loan_id
, c1.repayment_period
, c1.repayment_period_start
, c1.repayment_period_end
, c1.amount_due
, c1.cum_amount_due
, c1.amount_collected
, c1.loan_amount_USD
, c1.loan_status
, c1.number_of_payments
, c1.payment_frequency
)
/*Add delinquency metrics*/
, collected_data_dq AS (
SELECT *
, CASE WHEN cum_amount_due > cum_amount_Collected
THEN 1
ELSE 0
END 'Delinquent'
, CASE WHEN cum_amount_due > cum_amount_Collected  AND amount_collected = 0
THEN 1
ELSE 0
END 'MissedPayment'
, CASE WHEN amount_collected <> 0 AND round(amount_collected,0) < round(amount_due,0)
THEN 1
ELSE 0
END 'isPartialPayment'
, CASE WHEN amount_collected <> 0 AND round(amount_collected,0) < round(amount_due,0)
THEN amount_collected / amount_due
ELSE 0
END 'pct_PartialPayment'

--Use a proxy for delinquency days with ratio of outstanding debt/payment
--This is to mitigate impacts of variances in repayment timing
, CASE WHEN cum_amount_due > cum_amount_collected
THEN (cum_amount_due - cum_amount_collected) / amount_due
ELSE 0
END 'Calc_Payments_Delinquent'
FROM collected_data_cumm2
)

/*Select all data and create DQ Buckets*/
SELECT  *
, CASE WHEN Calc_Payments_Delinquent <1 THEN '0-30 days'
WHEN Calc_Payments_Delinquent < 2 THEN '31-60 days'
WHEN Calc_Payments_Delinquent < 3 THEN '61-90 days'
ELSE '91+ days'
END 'DQ Bucket'
FROM collected_data_dq
ORDER BY zip_loan_id
, repayment_period;
