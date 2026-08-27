import os
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jDB:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE")
        self.driver = None

    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            self.uri, auth=(self.user, self.password)
        )

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def run_query(self, query, params=None):
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, params or {})
            return await result.data()

db = Neo4jDB()