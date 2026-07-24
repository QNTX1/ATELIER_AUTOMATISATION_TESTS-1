"""
tester/client.py
Wrapper HTTP minimal : timeout, 1 retry en cas d'échec réseau ou 429/5xx,
et mesure de la latence de chaque appel.
"""
import time
import requests


class APIResponse:
    """Petit conteneur pour uniformiser le résultat d'un appel, même en cas d'échec."""

    def __init__(self, ok, status_code=None, json_data=None, latency_ms=None,
                 error=None, retried=False):
        self.ok = ok
        self.status_code = status_code
        self.json_data = json_data
        self.latency_ms = latency_ms
        self.error = error
        self.retried = retried


class APIClient:
    def __init__(self, base_url, timeout=3, max_retries=1, backoff_seconds=1.5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def get(self, path, params=None):
        """
        Effectue un GET sur base_url + path.
        Retry (max_retries fois) si : timeout, erreur réseau, 429, ou 5xx.
        Retourne toujours un APIResponse (jamais d'exception propagée).
        """
        url = f"{self.base_url}{path}"
        attempt = 0
        retried = False

        while True:
            start = time.perf_counter()
            try:
                resp = requests.get(url, params=params, timeout=self.timeout)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if resp.status_code == 429 or resp.status_code >= 500:
                    if attempt < self.max_retries:
                        attempt += 1
                        retried = True
                        time.sleep(self.backoff_seconds)
                        continue
                    return APIResponse(
                        ok=False, status_code=resp.status_code,
                        latency_ms=latency_ms,
                        error=f"HTTP {resp.status_code} après retry",
                        retried=retried,
                    )

                try:
                    data = resp.json()
                except ValueError:
                    data = None

                return APIResponse(
                    ok=True, status_code=resp.status_code,
                    json_data=data, latency_ms=latency_ms, retried=retried,
                )

            except requests.exceptions.Timeout:
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                if attempt < self.max_retries:
                    attempt += 1
                    retried = True
                    time.sleep(self.backoff_seconds)
                    continue
                return APIResponse(ok=False, latency_ms=latency_ms,
                                    error="Timeout après retry", retried=retried)

            except requests.exceptions.RequestException as exc:
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                if attempt < self.max_retries:
                    attempt += 1
                    retried = True
                    time.sleep(self.backoff_seconds)
                    continue
                return APIResponse(ok=False, latency_ms=latency_ms,
                                    error=f"Erreur réseau: {exc}", retried=retried)
