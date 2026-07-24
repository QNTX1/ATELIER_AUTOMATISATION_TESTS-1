# API Choice

- Étudiant : Quentin LE Goc
- API choisie : Frankfurter
- URL base : https://api.frankfurter.app
- Documentation officielle / README : https://www.frankfurter.app/docs/
- Auth : None
- Endpoints testés :
  - GET /latest
  - GET /latest?from=EUR
  - GET /latest?amount=100&from=USD&to=EUR
  - GET /currencies
  - GET /{date} (ex: /2020-01-01)
- Hypothèses de contrat (champs attendus, types, codes) :
  - `/latest` renvoie 200 avec un JSON contenant `amount` (number), `base` (string),
    `date` (string, format YYYY-MM-DD) et `rates` (object de code devise -> nombre).
  - `/currencies` renvoie 200 avec un objet associant chaque code ISO (ex: "USD")
    à son nom complet (string).
  - Une devise inconnue en paramètre `from`/`to` (ex: "XXX") renvoie un code
    d'erreur (400/404/422) plutôt qu'un 200.
  - Une date invalide dans le chemin (ex: `/2020-13-45`) renvoie également une erreur.
- Limites / rate limiting connu :
  - Pas de clé requise. Pas de rate limit documenté publiquement, mais l'atelier
    impose une charge limitée (1 run / 5 min, ≤ 20 requêtes/run) — le run actuel
    n'effectue que 8 appels.
- Risques (instabilité, downtime, CORS, etc.) :
  - Service maintenu bénévolement (données de la Banque Centrale Européenne) :
    possibilité de downtime ponctuel, pas de SLA garanti.
  - Les taux ne sont mis à jour qu'un jour ouvré sur deux (pas de risque pour les
    tests de contrat, mais à noter pour l'interprétation des données).
