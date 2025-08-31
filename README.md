# Mini Flask + Postgres (Render)

## Local
1) Python 3.11+
2) `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
3) `pip install -r requirements.txt`
4) (Opcional) Crear `.env` copiando de `.env.example` y poner `DATABASE_URL` si quieres Postgres local.
5) Ejecuta: `FLASK_DEBUG=1 flask --app app run`  (o `python -m flask --app app run`)

## Despliegue en Render
1) Sube este repo a GitHub.
2) En Render: **New → Postgres** → crea la base (gratis). Copia el `External Database URL`.
3) En Render: **New → Web Service** → conecta tu repo.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
   - **Env Vars:**
     - `DATABASE_URL` = (pega el External Database URL de Postgres)
     - `INIT_TOKEN` = (elige un token)
4) Despliega. Luego ejecuta:
   - `POST https://TU-DOMINIO.onrender.com/init-db` con header `X-Init-Token: TU_TOKEN`
5) Prueba:
   - `GET /properties`
   - `POST /properties` con JSON `{ "title": "Piso demo", "address": "C/ Mayor 1", "status": "free" }`
****
