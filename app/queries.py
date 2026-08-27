# 1. Top Fraud-Prone Merchants
TOP_FRAUD_MERCHANTS = """
MATCH (m:Merchant)<-[:AT_MERCHANT]-(t:Transaction)-[:HAS_FRAUD]->(f:FraudCase)
RETURN m.merchant_id, m.merchant_name, count(f) as fraud_count
ORDER BY fraud_count DESC LIMIT 10
"""

# 2. Cardholders with Highest Fraud Activity
TOP_FRAUD_CARDHOLDERS = """
MATCH (ch:Cardholder)-[:OWNS]->(c:Card)-[:MADE]->(t:Transaction)-[:HAS_FRAUD]->(f:FraudCase)
RETURN ch.cardholder_id, count(f) as fraud_count
ORDER BY fraud_count DESC LIMIT 10
"""

# 3. Fraud Cases by Type
FRAUD_BY_TYPE = """
MATCH (f:FraudCase)
RETURN f.fraudType as fraud_type, count(f) as count
ORDER BY count DESC
"""

# 4. High-Value Suspicious Transactions (> 7000)
HIGH_VALUE_TRANSACTIONS = """
MATCH (t:Transaction)
WHERE t.transaction_amount > 7000
RETURN t.transaction_id, t.transaction_amount, t.transaction_date
ORDER BY t.transaction_amount DESC LIMIT 20
"""

# 5. Merchant Risk Overview (high / elevated)
MERCHANT_RISK = """
MATCH (m:Merchant)
WHERE m.merchant_risk_band IN ['high', 'elevated']
RETURN m.merchant_id, m.merchant_name, m.merchant_risk_band, m.chargeback_ratio
ORDER BY m.chargeback_ratio DESC LIMIT 10
"""