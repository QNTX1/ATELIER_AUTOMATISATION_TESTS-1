"""
tester/tests.py
Tests "as code" pour l'API Frankfurter (https://api.frankfurter.app).
Chaque fonction reçoit un APIClient, effectue un appel, et retourne un dict :
{"name": str, "status": "PASS" | "FAIL", "latency_ms": float, "details": str}
Aucun test n'écrit / ne supprime de données : Frankfurter est en lecture seule.
"""


def _result(name, passed, latency_ms, details=""):
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "latency_ms": latency_ms,
        "details": details,
    }


def test_latest_status(client):
    r = client.get("/latest")
    if not r.ok:
        return _result("GET /latest -> 200", False, r.latency_ms, r.error)
    return _result("GET /latest -> 200", r.status_code == 200, r.latency_ms,
                    f"status={r.status_code}")


def test_latest_schema(client):
    r = client.get("/latest")
    if not r.ok or r.json_data is None:
        return _result("schema /latest (amount/base/date/rates)", False,
                        r.latency_ms, r.error or "pas de JSON")
    data = r.json_data
    required = {"amount": (int, float), "base": str, "date": str, "rates": dict}
    missing = [k for k in required if k not in data]
    if missing:
        return _result("schema /latest (amount/base/date/rates)", False,
                        r.latency_ms, f"champs manquants: {missing}")
    bad_types = [k for k, t in required.items() if not isinstance(data[k], t)]
    if bad_types:
        return _result("schema /latest (amount/base/date/rates)", False,
                        r.latency_ms, f"types invalides: {bad_types}")
    return _result("schema /latest (amount/base/date/rates)", True, r.latency_ms)


def test_latest_from_eur(client):
    r = client.get("/latest", params={"from": "EUR"})
    if not r.ok or r.json_data is None:
        return _result("GET /latest?from=EUR -> base=EUR", False, r.latency_ms, r.error)
    ok = r.json_data.get("base") == "EUR" and isinstance(r.json_data.get("rates"), dict) \
        and len(r.json_data["rates"]) > 0
    return _result("GET /latest?from=EUR -> base=EUR", ok, r.latency_ms,
                    f"base={r.json_data.get('base')}")


def test_currencies_endpoint(client):
    r = client.get("/currencies")
    if not r.ok or r.json_data is None:
        return _result("GET /currencies -> dict code->nom", False, r.latency_ms, r.error)
    data = r.json_data
    ok = isinstance(data, dict) and "USD" in data and isinstance(data["USD"], str)
    return _result("GET /currencies -> dict code->nom", ok, r.latency_ms,
                    f"{len(data) if isinstance(data, dict) else 0} devises")


def test_historical_date(client):
    r = client.get("/2020-01-01")
    if not r.ok or r.json_data is None:
        return _result("GET /2020-01-01 -> date historique", False, r.latency_ms, r.error)
    ok = r.json_data.get("date") is not None and r.status_code == 200
    return _result("GET /2020-01-01 -> date historique", ok, r.latency_ms,
                    f"date={r.json_data.get('date')}")


def test_amount_conversion(client):
    r = client.get("/latest", params={"amount": 100, "from": "USD", "to": "EUR"})
    if not r.ok or r.json_data is None:
        return _result("GET /latest?amount=100&from=USD&to=EUR", False, r.latency_ms, r.error)
    rates = r.json_data.get("rates", {})
    ok = "EUR" in rates and isinstance(rates["EUR"], (int, float)) and rates["EUR"] > 0
    return _result("GET /latest?amount=100&from=USD&to=EUR", ok, r.latency_ms,
                    f"rates={rates}")


def test_invalid_currency(client):
    """Cas d'erreur attendu : devise inexistante -> code d'erreur (pas 200)."""
    r = client.get("/latest", params={"from": "XXX"})
    if not r.ok:
        # Une erreur réseau n'est pas le comportement testé ici
        return _result("GET /latest?from=XXX -> erreur attendue", False, r.latency_ms, r.error)
    ok = r.status_code in (400, 404, 422)
    return _result("GET /latest?from=XXX -> erreur attendue", ok, r.latency_ms,
                    f"status={r.status_code}")


def test_invalid_date(client):
    """Cas d'erreur attendu : date invalide -> code d'erreur (pas 200)."""
    r = client.get("/2020-13-45")
    if not r.ok:
        return _result("GET /2020-13-45 -> erreur attendue", False, r.latency_ms, r.error)
    ok = r.status_code in (400, 404, 422)
    return _result("GET /2020-13-45 -> erreur attendue", ok, r.latency_ms,
                    f"status={r.status_code}")


# Liste ordonnée des tests exécutés par le runner (8 tests >= 6 requis)
ALL_TESTS = [
    test_latest_status,
    test_latest_schema,
    test_latest_from_eur,
    test_currencies_endpoint,
    test_historical_date,
    test_amount_conversion,
    test_invalid_currency,
    test_invalid_date,
]
