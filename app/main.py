from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import db
from app.queries import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.close()

app = FastAPI(title="Fraud Detection API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _node_properties(node):
    if node is None:
        return {}
    if hasattr(node, "properties"):
        return dict(node.properties)
    if hasattr(node, "items"):
        return dict(node.items())
    if isinstance(node, dict):
        return dict(node)
    return {}


def _node_id(node, label):
    props = _node_properties(node)
    id_keys = {
        "Transaction": "transaction_id",
        "Card": "card_id",
        "Cardholder": "cardholder_id",
        "Merchant": "merchant_id",
        "FraudCase": "fraud_case_id",
    }
    key = id_keys.get(label)
    if key and key in props:
        return props[key]
    for candidate in props.values():
        if candidate is not None:
            return candidate
    return None


@app.get("/")
async def root():
    return {
        "message": "Fraud Detection API",
        "endpoints": [
            "/top-fraud-merchants",
            "/top-fraud-cardholders",
            "/fraud-by-type",
            "/high-value-transactions",
            "/merchant-risk",
            "/stats",
            "/graph/transaction/{txn_id}"
        ]
    }


@app.get("/stats")
async def get_stats():
    try:
        node_count = await db.run_query("MATCH (n) RETURN count(n) AS count")
        rel_count = await db.run_query("MATCH ()-[r]->() RETURN count(r) AS count")
        return {
            "nodes": int(node_count[0]["count"]),
            "relationships": int(rel_count[0]["count"])
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/graph/transaction/{txn_id}")
async def get_transaction_graph(txn_id: int):
    query = """
    MATCH (t:Transaction {transaction_id: $txn_id})
    OPTIONAL MATCH (c:Card)-[:MADE]->(t)
    OPTIONAL MATCH (ch:Cardholder)-[:OWNS]->(c)
    OPTIONAL MATCH (t)-[:AT_MERCHANT]->(m:Merchant)
    OPTIONAL MATCH (t)-[:HAS_FRAUD]->(f:FraudCase)
    RETURN t, c, ch, m, f
    """
    result = await db.run_query(query, {"txn_id": txn_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Extract nodes and relationships
    row = result[0]
    nodes = []
    links = []
    node_ids = set()

    def add_node(node_data, label, id_key, display_name=None):
        if node_data is None:
            return None
        node_id = node_data.get(id_key)
        if node_id is None:
            return None
        if node_id in node_ids:
            return node_id
        node_ids.add(node_id)
        nodes.append({
            "id": str(node_id),
            "label": label,
            "display_name": display_name or f"{label}_{node_id}",
            "properties": {k: v for k, v in node_data.items() if k != id_key}
        })
        return node_id

    # Add nodes
    txn_id_str = add_node(row.get("t"), "Transaction", "transaction_id", f"Txn {txn_id}")
    card_id = add_node(row.get("c"), "Card", "card_id", f"Card {row.get('c', {}).get('card_id', '')}")
    ch_id = add_node(row.get("ch"), "Cardholder", "cardholder_id", f"Holder {row.get('ch', {}).get('cardholder_id', '')}")
    merch_id = add_node(row.get("m"), "Merchant", "merchant_id", row.get('m', {}).get('merchant_name', 'Merchant'))
    fraud_id = add_node(row.get("f"), "FraudCase", "fraud_case_id", f"Fraud {row.get('f', {}).get('fraud_case_id', '')}")

    # Add relationships
    if card_id and txn_id_str:
        links.append({"source": card_id, "target": txn_id_str, "type": "MADE"})
    if ch_id and card_id:
        links.append({"source": ch_id, "target": card_id, "type": "OWNS"})
    if txn_id_str and merch_id:
        links.append({"source": txn_id_str, "target": merch_id, "type": "AT_MERCHANT"})
    if txn_id_str and fraud_id:
        links.append({"source": txn_id_str, "target": fraud_id, "type": "HAS_FRAUD"})

    return {"nodes": nodes, "links": links}

@app.get("/top-fraud-merchants")
async def get_top_fraud_merchants():
    return await db.run_query(TOP_FRAUD_MERCHANTS)

@app.get("/top-fraud-cardholders")
async def get_top_fraud_cardholders():
    return await db.run_query(TOP_FRAUD_CARDHOLDERS)

@app.get("/fraud-by-type")
async def get_fraud_by_type():
    return await db.run_query(FRAUD_BY_TYPE)

@app.get("/high-value-transactions")
async def get_high_value_transactions():
    return await db.run_query(HIGH_VALUE_TRANSACTIONS)

@app.get("/merchant-risk")
async def get_merchant_risk():
    return await db.run_query(MERCHANT_RISK)