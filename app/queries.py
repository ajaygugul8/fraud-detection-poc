# 1. Top Fraud-Prone Merchants
TOP_FRAUD_MERCHANTS = """
MATCH (m:Merchant)<-[:AT_MERCHANT]-(t:Transaction)-[:HAS_FRAUD]->(f:FraudCase)
RETURN m.merchant_id AS merchant_id, 
       m.merchant_name AS merchant_name, 
       count(f) AS fraud_count
ORDER BY fraud_count DESC LIMIT 10
"""

# 2. Cardholders with Highest Fraud Activity
TOP_FRAUD_CARDHOLDERS = """
MATCH (ch:Cardholder)-[:OWNS]->(c:Card)-[:MADE]->(t:Transaction)-[:HAS_FRAUD]->(f:FraudCase)
RETURN ch.cardholder_id AS cardholder_id, 
       count(f) AS fraud_count
ORDER BY fraud_count DESC LIMIT 10
"""

# 3. Fraud Cases by Type
FRAUD_BY_TYPE = """
MATCH (f:FraudCase)
RETURN f.fraudType AS fraud_type, 
       count(f) AS count
ORDER BY count DESC
"""

# 4. High-Value Suspicious Transactions
HIGH_VALUE_TRANSACTIONS = """
MATCH (t:Transaction)
WHERE t.transaction_amount > 7000
RETURN t.transaction_id AS transaction_id, 
       t.transaction_amount AS transaction_amount, 
       toString(t.transaction_date) AS transaction_date
ORDER BY t.transaction_amount DESC LIMIT 20
"""

# 5. Merchant Risk Overview
MERCHANT_RISK = """
MATCH (m:Merchant)
WHERE m.merchant_risk_band IN ['high', 'elevated']
RETURN m.merchant_id AS merchant_id, 
       m.merchant_name AS merchant_name, 
       m.merchant_risk_band AS merchant_risk_band, 
       m.chargeback_ratio AS chargeback_ratio
ORDER BY m.chargeback_ratio DESC LIMIT 10
"""