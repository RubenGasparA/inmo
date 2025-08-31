import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text

app = Flask(__name__)

# --- Render da DATABASE_URL en formato postgres://, aquí lo arreglamos
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///local.db")
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(raw_db_url, pool_pre_ping=True)

# Crear tabla si no existe
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
def home():
    return {"ok": True, "message": "Flask + Postgres listos 👌"}

@app.post("/init-db")
def route_init_db():
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
