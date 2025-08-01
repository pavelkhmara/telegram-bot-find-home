import asyncpg
import json
from dotenv import load_dotenv
import os

load_dotenv()
db = os.getenv("db")
db_user = os.getenv("db_user")
user_password = os.getenv("user_password")

DB_CONFIG = {
    "user": db_user,
    "password": user_password,
    "database": db,
    "host": "localhost",
    "port": 5432
}

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            **DB_CONFIG,
            server_settings={"search_path": "public"}
        )
    return _pool

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS filters (
            user_id BIGINT PRIMARY KEY,
            filter_data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now()
        );
        """)

async def save_filter(user_id: int, data: dict):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO filters (user_id, filter_data)
        VALUES ($1, $2)
        ON CONFLICT (user_id)
        DO UPDATE SET filter_data = $2, updated_at = now()
        """, user_id, json.dumps(data))

async def load_filter(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT filter_data FROM filters WHERE user_id = $1", user_id)
        if row:
            filter_data = row["filter_data"]
            if isinstance(filter_data, str):
                return json.loads(filter_data)
            return filter_data
        return None
