# Fraud Detection POC

Graph-based fraud detection API on Neo4j AuraDB + FastAPI.

## Project structure

```
fraud-detection-poc/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + 5 endpoints
│   ├── database.py       # Async Neo4j driver wrapper
│   └── queries.py        # Cypher queries
├── import/                # Neo4j-ready CSVs (5 node files, 4 relationship files)
├── import_data.py         # One-shot importer for a fresh Aura instance
├── prepare_import.py      # Regenerates import/ from raw source CSVs (not needed
│                           #   right now — import/ already has current data)
├── requirements.txt
└── .env.example
```

## 1. Point everything at your new Aura instance

```bash
cp .env.example .env
```

Fill in the 4 values from the Aura Console's "Connect" panel. On Aura Free,
`NEO4J_USER` and `NEO4J_DATABASE` both equal the instance ID (not `neo4j`).

## 2. Install deps

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 3. Import the graph

```bash
python import_data.py
```

This uses the Neo4j driver directly with batched `UNWIND` writes (500 rows
at a time), not Aura's Data Importer or `LOAD CSV` — that's what silently
truncated the previous import to 2,365 of 6,763 nodes. Expect the run to
end with:

```
TOTAL NODES: 6763 (expected 6,763)
TOTAL RELATIONSHIPS: 9556 (expected 9,556)
```

## 4. Run the API locally

```bash
uvicorn app.main:app --reload
```

Test each endpoint:

```bash
curl http://localhost:8000/top-fraud-merchants
curl http://localhost:8000/top-fraud-cardholders
curl http://localhost:8000/fraud-by-type
curl http://localhost:8000/high-value-transactions
curl http://localhost:8000/merchant-risk
```

## 5. Deploy

Update the same 4 `NEO4J_*` variables in your Render service's environment
settings to point at the new instance, then redeploy. Render Free spins
down after 15 min idle — first request after a cold start takes 30-60s.

## Schema reference

| Node | Key property | Count |
|---|---|---|
| Cardholder | cardholder_id | 439 |
| Card | card_id | 593 |
| Merchant | merchant_id | 366 |
| Transaction | transaction_id | 4,398 |
| FraudCase | fraud_case_id | 967 |

| Relationship | Direction |
|---|---|
| OWNS | Cardholder → Card |
| MADE | Card → Transaction |
| AT_MERCHANT | Transaction → Merchant |
| HAS_FRAUD | Transaction → FraudCase |
