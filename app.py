import os
from urllib.parse import urlparse
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

# --- DB URL (Render te da DATABASE_URL). Arreglamos prefijo postgres:// → postgresql+psycopg2://
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///local.db")
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(raw_db_url, pool_pre_ping=True)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS properties (
                id SERIAL PRIMARY KEY,
                title VARCHAR(120) NOT NULL,
                address VARCHAR(255),
                status VARCHAR(30) DEFAULT 'free'
            );
        """))

@app.get("/")
def health():
    # Comprobación rápida de conexión
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True, "message": "Flask + Postgres listos 👌"}, 200
    except OperationalError as e:
        return {"ok": False, "error": str(e)}, 500

@app.post("/init-db")
def route_init_db():
    # Pequeña protección con token opcional
    token = request.headers.get("X-Init-Token")
    expected = os.getenv("INIT_TOKEN")
    if expected and token != expected:
        return {"error": "bad token"}, 401
    init_db()
    return {"ok": True, "message": "Tablas creadas (idempotente)"}

@app.get("/properties")
def list_properties():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, title, address, status FROM properties ORDER BY id DESC")).mappings().all()
    return jsonify(list(rows))

@app.post("/properties")
def add_property():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    address = (data.get("address") or "").strip()
    status = (data.get("status") or "free").strip()
    if not title:
        return {"error": "title es obligatorio"}, 400
    with engine.begin() as conn:
        row = conn.execute(
            text("INSERT INTO properties (title, address, status) VALUES (:t,:a,:s) RETURNING id"),
            {"t": title, "a": address, "s": status}
        ).first()
    return {"ok": True, "id": row[0]}, 201
