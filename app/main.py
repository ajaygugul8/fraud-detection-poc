from fastapi import FastAPI
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

@app.get("/")
async def root():
    return {
        "message": "Fraud Detection API",
        "endpoints": [
            "/top-fraud-merchants",
            "/top-fraud-cardholders",
            "/fraud-by-type",
            "/high-value-transactions",
            "/merchant-risk"
        ]
    }

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