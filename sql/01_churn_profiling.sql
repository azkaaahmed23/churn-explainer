-- Churn profiling queries (SQLite). Run them all with: python src/sql_profile.py
-- Each query starts with a "-- name:" line. churn_rate_pct = % of customers with Churn = 'Yes'.
-- NOTE: Churn = 'Yes' means the customer ALREADY left, so these queries describe the past; they do not predict.

-- name: 01_overall_churn_rate
SELECT COUNT(*)                                        AS customers,
       SUM(churn_flag)                                 AS churned,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers;

-- name: 02_churn_by_contract
SELECT Contract,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- name: 03_churn_by_tenure_bucket
SELECT tenure_bucket,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers
GROUP BY tenure_bucket
ORDER BY tenure_bucket;

-- name: 04_churn_by_internet_service
SELECT InternetService,
       COUNT(*)                                        AS customers,
       ROUND(AVG(MonthlyCharges), 2)                   AS avg_monthly_charges,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

-- name: 05_churn_by_addon_count
-- Add-ons = OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies
SELECT addon_count                                     AS addons_subscribed,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers
WHERE InternetService <> 'No'
GROUP BY addon_count
ORDER BY addon_count;

-- name: 06_churn_by_internet_type_and_tech_support
-- Do fibre customers churn because of fibre, or because they lack tech support?
SELECT InternetService,
       TechSupport,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers
WHERE InternetService <> 'No'
GROUP BY InternetService, TechSupport
ORDER BY churn_rate_pct DESC;

-- name: 07_churn_by_payment_method
SELECT PaymentMethod,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;

-- name: 08_revenue_churned_vs_active
-- Monthly revenue from customers who already left (Yes) versus those still active (No).
SELECT Churn,
       COUNT(*)                                        AS customers,
       ROUND(AVG(MonthlyCharges), 2)                   AS avg_monthly_charges,
       ROUND(SUM(MonthlyCharges), 0)                   AS total_monthly_revenue,
       ROUND(100.0 * SUM(MonthlyCharges) / (SELECT SUM(MonthlyCharges) FROM customers), 1) AS pct_of_all_revenue
FROM customers
GROUP BY Churn;

-- name: 09_demographic_groups
-- The groups we audit later. gender is NOT a model input; SeniorCitizen is not either.
SELECT 'gender'                                        AS dimension,
       gender                                          AS grp,
       COUNT(*)                                        AS customers,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)    AS churn_rate_pct
FROM customers GROUP BY gender
UNION ALL
SELECT 'SeniorCitizen',
       CASE SeniorCitizen WHEN 1 THEN 'Senior' ELSE 'Non-senior' END,
       COUNT(*),
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 1)
FROM customers GROUP BY SeniorCitizen;
