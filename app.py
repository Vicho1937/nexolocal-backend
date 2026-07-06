import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # permite que el front-end (otro dominio) llame a esta API

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "NexoLocal API"})


@app.route("/health", methods=["GET"])
def health():
    """Endpoint para verificar que el backend y la base de datos responden."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"backend": "ok", "database": "ok"}), 200
    except Exception as e:
        return jsonify({"backend": "ok", "database": "error", "detail": str(e)}), 500


@app.route("/emprendimientos", methods=["GET"])
def listar_emprendimientos():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT id, nombre_negocio, comuna, rubro, correo_contacto, created_at "
            "FROM emprendimientos ORDER BY id DESC;"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/emprendimientos", methods=["POST"])
def crear_emprendimiento():
    data = request.get_json(silent=True) or {}

    nombre_negocio = data.get("nombre_negocio")
    comuna = data.get("comuna")
    rubro = data.get("rubro")
    correo_contacto = data.get("correo_contacto")

    if not all([nombre_negocio, comuna, rubro, correo_contacto]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO emprendimientos (nombre_negocio, comuna, rubro, correo_contacto) "
            "VALUES (%s, %s, %s, %s) RETURNING id;",
            (nombre_negocio, comuna, rubro, correo_contacto),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": new_id, "mensaje": "Emprendimiento registrado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
