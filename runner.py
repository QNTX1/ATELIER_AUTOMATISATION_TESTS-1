"""
tester/runner.py
Exécute la suite de tests et calcule les métriques QoS :
latence moyenne, p95, taux d'erreur, disponibilité du run.
"""
import math
from datetime import datetime, timezone

from .client import APIClient
from .tests import ALL_TESTS

API_NAME = "Frankfurter"
BASE_URL = "https://api.frankfurter.app"


def _percentile(values, pct):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * (pct / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return round(values[f] + (values[c] - values[f]) * (k - f), 2)


def run_all_tests():
    """Exécute tous les tests définis dans tests.ALL_TESTS et renvoie un dict de run."""
    client = APIClient(BASE_URL, timeout=3, max_retries=1)

    results = []
    for test_fn in ALL_TESTS:
        results.append(test_fn(client))

    latencies = [t["latency_ms"] for t in results if t["latency_ms"] is not None]
    passed = sum(1 for t in results if t["status"] == "PASS")
    failed = sum(1 for t in results if t["status"] == "FAIL")
    total = len(results)
    error_rate = round(failed / total, 3) if total else 0.0

    run = {
        "api": API_NAME,
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "error_rate": error_rate,
            "availability": round(1 - error_rate, 3),
            "latency_ms_avg": round(sum(latencies) / len(latencies), 2) if latencies else 0,
            "latency_ms_p95": _percentile(latencies, 95),
        },
        "tests": results,
    }
    return run
