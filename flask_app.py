"""
flask_app.py
Point d'entrée Flask pour l'atelier "Testing as Code & API Monitoring".

Routes :
  GET/POST /run        -> déclenche un run de tests, l'enregistre, renvoie le JSON du run
  GET      /dashboard   -> tableau de bord HTML (dernier run + historique)
  GET      /health      -> état de santé simple de l'app (bonus)
  GET      /api/runs    -> export JSON de l'historique (bonus)
  GET      /api/runs/<id> -> détail JSON d'un run précis
  GET      /            -> redirige vers /dashboard
"""
import json
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, redirect, url_for, abort

from storage import init_db, save_run, list_runs, get_connection
from tester.runner import run_all_tests, API_NAME

app = Flask(__name__)
init_db()

APP_START_TIME = datetime.now(timezone.utc)


@app.route("/")
def index():
    # Affiche la page d'accueil existante (consignes de l'atelier).
    return render_template("consignes.html")


@app.route("/run", methods=["GET", "POST"])
def run_tests():
    run = run_all_tests()
    save_run(run)
    return jsonify(run)


@app.route("/dashboard")
def dashboard():
    runs = list_runs(limit=50)
    last_run = runs[0] if runs else None
    last_run_tests = json.loads(last_run["payload"])["tests"] if last_run else []
    return render_template(
        "dashboard.html",
        api_name=API_NAME,
        last_run=last_run,
        last_run_tests=last_run_tests,
        runs=runs,
    )


@app.route("/health")
def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except Exception:
        db_ok = False

    uptime_s = (datetime.now(timezone.utc) - APP_START_TIME).total_seconds()
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "unreachable",
        "uptime_seconds": round(uptime_s, 1),
    }), (200 if db_ok else 503)


@app.route("/api/runs")
def api_runs():
    runs = list_runs(limit=50)
    return jsonify([json.loads(r["payload"]) for r in runs])


@app.route("/api/runs/<int:run_id>")
def api_run_detail(run_id):
    conn = get_connection()
    row = conn.execute("SELECT payload FROM runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    if not row:
        abort(404)
    return jsonify(json.loads(row["payload"]))


if __name__ == "__main__":
    app.run(debug=True)
