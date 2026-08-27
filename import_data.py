"""
Fraud Detection POC — Graph Data Importer
------------------------------------------
Loads all 9 CSVs (5 node files + 4 relationship files) into a Neo4j AuraDB
instance using the Python driver with batched UNWIND writes.

Why not LOAD CSV?
Aura Free's LOAD CSV needs files hosted at a public URL (it can't read local
disk), and the Aura Console's GUI Data Importer is what silently truncated
the last import to ~2,365 of 6,763 nodes. Batched UNWIND from a local script
avoids both problems and gives real per-batch feedback if anything fails.

Usage:
    pip install neo4j python-dotenv
    # .env must define NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
    python prepare_import.py
"""

import csv
import os
import sys
import time
from pathlib import Path

from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_DATABASE = os.environ["NEO4J_DATABASE"]

DATA_DIR = Path(__file__).parent / "import"
BATCH_SIZE = 500


def read_csv(filename):
    path = DATA_DIR / filename
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def batched(rows, size=BATCH_SIZE):
    for i in range(0, len(rows), size):
        yield rows[i : i + size]


# ---------------------------------------------------------------------------
# Constraints (one per node label, on its key property)
# ---------------------------------------------------------------------------

CONSTRAINTS = [
    "CREATE CONSTRAINT cardholder_id IF NOT EXISTS FOR (n:Cardholder) REQUIRE n.cardholder_id IS UNIQUE",
    "CREATE CONSTRAINT card_id IF NOT EXISTS FOR (n:Card) REQUIRE n.card_id IS UNIQUE",
    "CREATE CONSTRAINT merchant_id IF NOT EXISTS FOR (n:Merchant) REQUIRE n.merchant_id IS UNIQUE",
    "CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (n:Transaction) REQUIRE n.transaction_id IS UNIQUE",
    "CREATE CONSTRAINT fraud_case_id IF NOT EXISTS FOR (n:FraudCase) REQUIRE n.fraud_case_id IS UNIQUE",
]

# ---------------------------------------------------------------------------
# Node imports — cast numeric fields explicitly so they don't land as strings
# ---------------------------------------------------------------------------


def import_cardholders(session):
    rows = read_csv("cardholders.csv")
    query = """
    UNWIND $rows AS row
    MERGE (n:Cardholder {cardholder_id: toInteger(row.cardholder_id)})
    """
    run_batches(session, query, rows, "Cardholder")


def import_cards(session):
    rows = read_csv("cards.csv")
    query = """
    UNWIND $rows AS row
    MERGE (n:Card {card_id: toInteger(row.card_id)})
    SET n.cardholder_id = toInteger(row.cardholder_id),
        n.status = row.status,
        n.card_product = row.card_product,
        n.network = row.network,
        n.credit_limit = toFloat(row.credit_limit),
        n.card_present_usage_ratio = toFloat(row.card_present_usage_ratio),
        n.digital_wallet_flag = toInteger(row.digital_wallet_flag)
    """
    run_batches(session, query, rows, "Card")


def import_merchants(session):
    rows = read_csv("merchants.csv")
    query = """
    UNWIND $rows AS row
    MERGE (n:Merchant {merchant_id: toInteger(row.merchant_id)})
    SET n.merchant_category = row.merchant_category,
        n.merchant_country = row.merchant_country,
        n.merchant_name = row.merchant_name,
        n.acquirer_region = row.acquirer_region,
        n.merchant_size = row.merchant_size,
        n.card_not_present_share = toFloat(row.card_not_present_share),
        n.chargeback_ratio = toFloat(row.chargeback_ratio),
        n.merchant_risk_band = row.merchant_risk_band
    """
    run_batches(session, query, rows, "Merchant")


def import_transactions(session):
    rows = read_csv("transactions.csv")
    query = """
    UNWIND $rows AS row
    MERGE (n:Transaction {transaction_id: toInteger(row.transaction_id)})
    SET n.card_id = toInteger(row.card_id),
        n.merchant_id = toInteger(row.merchant_id),
        n.transaction_date = date(row.transaction_date),
        n.merchant_category = row.merchant_category,
        n.transaction_amount = toFloat(row.transaction_amount),
        n.merchant_country = row.merchant_country,
        n.entry_mode = row.entry_mode,
        n.transaction_currency = row.transaction_currency
    """
    run_batches(session, query, rows, "Transaction")


def import_fraud_cases(session):
    rows = read_csv("fraud_cases.csv")
    query = """
    UNWIND $rows AS row
    MERGE (n:FraudCase {fraud_case_id: toInteger(row.fraud_case_id)})
    SET n.transaction_id = toInteger(row.transaction_id),
        n.alert_date = date(row.alert_date),
        n.fraudType = row.fraud_type,
        n.investigation_status = row.investigation_status,
        n.chargeback_amount = toFloat(row.chargeback_amount),
        n.loss_amount = toFloat(row.loss_amount),
        n.model_score = toFloat(row.model_score)
    """
    run_batches(session, query, rows, "FraudCase")


# ---------------------------------------------------------------------------
# Relationship imports — match on the already-imported node key properties
# ---------------------------------------------------------------------------


def import_owns(session):
    rows = read_csv("owns.csv")
    query = """
    UNWIND $rows AS row
    MATCH (ch:Cardholder {cardholder_id: toInteger(row.`:START_ID`)})
    MATCH (c:Card {card_id: toInteger(row.`:END_ID`)})
    MERGE (ch)-[:OWNS]->(c)
    """
    run_batches(session, query, rows, "OWNS")


def import_made(session):
    rows = read_csv("made.csv")
    query = """
    UNWIND $rows AS row
    MATCH (c:Card {card_id: toInteger(row.`:START_ID`)})
    MATCH (t:Transaction {transaction_id: toInteger(row.`:END_ID`)})
    MERGE (c)-[:MADE]->(t)
    """
    run_batches(session, query, rows, "MADE")


def import_at_merchant(session):
    rows = read_csv("at_merchant.csv")
    query = """
    UNWIND $rows AS row
    MATCH (t:Transaction {transaction_id: toInteger(row.`:START_ID`)})
    MATCH (m:Merchant {merchant_id: toInteger(row.`:END_ID`)})
    MERGE (t)-[:AT_MERCHANT]->(m)
    """
    run_batches(session, query, rows, "AT_MERCHANT")


def import_has_fraud(session):
    rows = read_csv("has_fraud.csv")
    query = """
    UNWIND $rows AS row
    MATCH (t:Transaction {transaction_id: toInteger(row.`:START_ID`)})
    MATCH (f:FraudCase {fraud_case_id: toInteger(row.`:END_ID`)})
    MERGE (t)-[:HAS_FRAUD]->(f)
    """
    run_batches(session, query, rows, "HAS_FRAUD")


# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------


def run_batches(session, query, rows, label):
    total = len(rows)
    done = 0
    start = time.time()
    for batch in batched(rows):
        session.run(query, rows=batch)
        done += len(batch)
        print(f"  {label}: {done}/{total}", end="\r")
    elapsed = time.time() - start
    print(f"  {label}: {done}/{total} done in {elapsed:.1f}s")


def verify(session):
    print("\nVerifying counts...")
    result = session.run(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label"
    )
    total_nodes = 0
    for record in result:
        print(f"  {record['label']}: {record['count']}")
        total_nodes += record["count"]
    print(f"  TOTAL NODES: {total_nodes} (expected 6,763)")

    result = session.run(
        "MATCH ()-[r]->() RETURN type(r) AS rel, count(r) AS count ORDER BY rel"
    )
    total_rels = 0
    for record in result:
        print(f"  {record['rel']}: {record['count']}")
        total_rels += record["count"]
    print(f"  TOTAL RELATIONSHIPS: {total_rels} (expected 9,556)")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        driver.verify_connectivity()
        print(f"Connected to {NEO4J_URI} (database: {NEO4J_DATABASE})\n")

        with driver.session(database=NEO4J_DATABASE) as session:
            print("Creating constraints...")
            for stmt in CONSTRAINTS:
                session.run(stmt)
            print("  done\n")

            print("Importing nodes...")
            import_cardholders(session)
            import_cards(session)
            import_merchants(session)
            import_transactions(session)
            import_fraud_cases(session)

            print("\nImporting relationships...")
            import_owns(session)
            import_made(session)
            import_at_merchant(session)
            import_has_fraud(session)

            verify(session)

        print("\nImport complete.")
    except Exception as e:
        print(f"\nImport failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()