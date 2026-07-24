# Planification de l'exécution (PythonAnywhere Scheduled Task)

L'atelier demande un run automatique régulier (recommandé : toutes les 5 minutes).
PythonAnywhere (compte gratuit) permet de planifier une tâche **quotidienne**
minimum ; pour un rythme de 5 minutes il faut soit un compte payant (tâches
"Always-on" ou intervalle personnalisé), soit déclencher `/run` via un service
externe gratuit (ex. cron-job.org, UptimeRobot en mode "monitor") qui appelle
l'URL toutes les 5 minutes.

## Option A — Scheduled Task PythonAnywhere (si disponible sur votre plan)

1. Onglet **Tasks** sur PythonAnywhere.
2. Ajouter une nouvelle tâche avec la commande :
   ```bash
   curl -s https://VOTRE_SITE.pythonanywhere.com/run > /dev/null
   ```
3. Choisir l'heure (ou l'intervalle si votre plan le permet).

## Option B — Déclencheur externe gratuit (recommandé en compte gratuit)

1. Créer un compte sur https://cron-job.org (ou équivalent).
2. Créer un job qui fait un `GET` (ou `POST`) toutes les 5 minutes sur :
   ```
   https://VOTRE_SITE.pythonanywhere.com/run
   ```
3. Vérifier ensuite l'historique dans `/dashboard`.

## Respect des contraintes de charge

Chaque run effectue **8 requêtes** vers l'API testée (< 20 requêtes/run imposées
par l'atelier). À raison d'un run toutes les 5 minutes, la charge reste très
raisonnable et respecte la contrainte "tests non destructifs, charge limitée".
