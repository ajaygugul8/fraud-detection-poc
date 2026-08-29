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
    txn_query = "MATCH (t:Transaction {transaction_id: $txn_id}) RETURN t"
    txn_result = await db.run_query(txn_query, {"txn_id": txn_id})
    if not txn_result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    related_query = """
    MATCH (t:Transaction {transaction_id: $txn_id})
    OPTIONAL MATCH (c:Card)-[:MADE]->(t)
    OPTIONAL MATCH (ch:Cardholder)-[:OWNS]->(c)
    OPTIONAL MATCH (t)-[:AT_MERCHANT]->(m:Merchant)
    OPTIONAL MATCH (t)-[:HAS_FRAUD]->(f:FraudCase)
    RETURN t, c, ch, m, f
    """
    result = await db.run_query(related_query, {"txn_id": txn_id})
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")

    nodes = []
    links = []
    seen = set()

    def add_node(node, label):
        if node is None:
            return None
        props = _node_properties(node)
        node_id = _node_id(node, label)
        if node_id is None:
            return None
        key = f"{label}:{node_id}"
        if key in seen:
            return node_id
        seen.add(key)
        nodes.append({
            "id": node_id,
            "label": label,
            "properties": props
        })
        return node_id

    row = result[0]
    txn_node_id = add_node(row.get("t"), "Transaction")
    card_node_id = add_node(row.get("c"), "Card")
    cardholder_node_id = add_node(row.get("ch"), "Cardholder")
    merchant_node_id = add_node(row.get("m"), "Merchant")
    fraud_node_id = add_node(row.get("f"), "FraudCase")

    if txn_node_id is not None and card_node_id is not None:
        links.append({"source": card_node_id, "target": txn_node_id, "type": "MADE"})
    if card_node_id is not None and cardholder_node_id is not None:
        links.append({"source": cardholder_node_id, "target": card_node_id, "type": "OWNS"})
    if txn_node_id is not None and merchant_node_id is not None:
        links.append({"source": txn_node_id, "target": merchant_node_id, "type": "AT_MERCHANT"})
    if txn_node_id is not None and fraud_node_id is not None:
        links.append({"source": txn_node_id, "target": fraud_node_id, "type": "HAS_FRAUD"})

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