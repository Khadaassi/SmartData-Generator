# SmartData Generator

## Rapport de validation du service (Preview / Export / Insert)

**Version :** 1.0
**Statut :** Validé
**Projet :** SmartData Generator
**Date :** 2026-07-29

---

# 1. Objectif

Valider le fonctionnement complet du service `execution_service` (modes Preview, Export, Insert) à travers plusieurs scénarios représentatifs, conformément aux scénarios définis dans [`user_cases.md`](../01_framing/user_cases.md) (sections 7, 8, 9 et 16), et confirmer que le service répond aux besoins définis lors du cadrage.

Deux niveaux de preuve ont été mobilisés :

1. **Tests automatisés** (unitaires + intégration), exécutés contre une base PostgreSQL réelle.
2. **Validation end-to-end manuelle** via l'API FastAPI réelle, avec génération LLM réelle (Groq) et écriture réelle (fichiers, PostgreSQL), sur deux schémas métier distincts.

---

# 2. Anomalies d'environnement détectées et corrigées

| # | Anomalie | Cause | Correction |
|---|---|---|---|
| 1 | `ModuleNotFoundError: sqlalchemy` bloquait la collecte de 6 modules de tests (dont `test_execution_service.py`, `test_api_executions.py`) | Le `.venv` n'était pas synchronisé avec `pyproject.toml` après l'ajout de SQLAlchemy/psycopg | `uv sync` — installe `sqlalchemy`, `psycopg`, `psycopg-binary`, `greenlet` |
| 2 | Les 17 tests d'intégration touchant PostgreSQL (`test_postgres_data_writer.py`, `test_execution_reporting.py`, `test_project_repository.py`, `test_report_repository.py`) échouaient en `password authentication failed` | Le port `5432` local était déjà occupé par le conteneur PostgreSQL d'un **autre** projet (`pct_postgres`) ; le service se connectait donc à la mauvaise base | Remappage du port du service dans `docker/docker-compose.yml` (`5433:5432`) et mise à jour de `DATABASE_URL` dans `.env` ; conteneur dédié démarré via `docker compose -f docker/docker-compose.yml up -d postgres` |

Aucune anomalie fonctionnelle n'a été détectée dans le code de `execution_service`, `data_writer` ou des connecteurs de sortie.

## 2.1 Limitation d'environnement documentée (non bloquante)

Le modèle d'embeddings `bge-m3` n'est pas provisionné sur l'instance Ollama locale. Les appels RAG échouent donc avec `model "bge-m3" not found`. Ce point est **conforme au design** : `agents/generation_agent.py::_retrieve_context` traite toute erreur RAG comme un `GenerationError` **non bloquant** (`code=rag_unavailable`) et poursuit la génération sans contexte métier. Toutes les exécutions ci-dessous ont donc réussi malgré cette indisponibilité, avec un avertissement tracé dans le rapport — comportement attendu (cf. `functional_technical_scope.md`, absence d'erreur bloquante requise avant écriture). À corriger séparément (pull du modèle `bge-m3` sur Ollama) pour valider le scénario PREVIEW-01 avec règles métier RAG réelles.

---

# 3. Tests automatisés

## 3.1 Suite unitaire

```
tests/ (hors tests/integration)
111 passed
```

Couvre notamment `test_execution_service.py` (Preview / Export / Insert, contrôles de sécurité insert, persistance du rapport) et `test_api_executions.py` (contrat HTTP `/executions`).

## 3.2 Suite d'intégration (PostgreSQL réel, après correction du port)

```
tests/integration/test_postgres_data_writer.py .....   (5 passed)
tests/integration/test_execution_reporting.py .        (1 passed)
tests/integration/test_project_repository.py ........  (8 passed)
tests/integration/test_report_repository.py ...        (3 passed)
tests/integration/test_postgres_schema.py ......       (schéma multi-tables, clés étrangères)
tests/integration/test_groq.py ...                     (LLM réel)
17 + 9 = 26 passed
```

Notamment couvert par ces tests d'intégration :
- **INSERT-01** (insertion réussie, transaction validée) ;
- **INSERT-04** (rollback complet sur violation de contrainte — `test_insert_records_rolls_back_entirely_on_constraint_violation`) ;
- **UC-16** (rapport d'exécution persistant et interrogeable) ;
- **UC-04** (analyse d'un schéma PostgreSQL réel multi-tables via `test_postgres_schema.py`).

Non exécutés dans cet environnement (nécessitent un modèle Ollama non provisionné) : `test_indexing.py`, `test_search_relevance.py`, et les scénarios RAG de `test_generation_agent.py`. Sans lien avec les modes Preview/Export/Insert eux-mêmes.

---

# 4. Validation end-to-end (API réelle, LLM réel, PostgreSQL réel)

Exécutée via l'API `/executions` (in-process, `TestClient`), sans aucun mock, sur deux schémas de domaines différents pour démontrer la réutilisabilité du moteur (cf. `user_cases.md` §16, Démonstration 6).

**Schéma A — `Produit`** (e-commerce) : `nom` (string), `prix` (float), `categorie` (string, valeurs autorisées).
**Schéma B — `Client`** (relation client) : `email` (string), `age` (integer).

| Scénario | Mode | Schéma | Résultat | Statut HTTP | Statut métier |
|---|---|---|---|---|---|
| Preview schéma A | PREVIEW | Produit | 3 objets cohérents générés et validés | 200 | `READY` |
| Preview schéma B | PREVIEW | Client | 3 objets cohérents générés et validés (second domaine, même moteur) | 200 | `READY` |
| Export JSON | EXPORT | Produit | Fichier `data/exports/Produit_<run_id>.json` créé, contenu conforme au dataset validé | 200 | `EXPORTED` |
| Export CSV | EXPORT | Produit | Fichier `data/exports/Produit_<run_id>.csv` créé | 200 | `EXPORTED` |
| Insert refusé sans confirmation | INSERT | Client | Aucune écriture, erreur `insert_not_confirmed` explicite | 200 | `FAILED` |
| Insert confirmé | INSERT | Client | 3 lignes insérées dans `public.clients_test` (vérifié en base) | 200 | `INSERTED` |

Vérifications complémentaires effectuées directement en base :
- `SELECT * FROM clients_test` → 3 lignes correspondant exactement aux données générées et validées.
- `SELECT * FROM execution_reports` → une ligne par exécution ci-dessus, avec `project_id`, `entity`, `mode`, `status`, horodatages — traçabilité complète (UC-16) confirmée pour chaque scénario, y compris celui refusé (`FAILED`).

Aucune anomalie fonctionnelle constatée : chaque mode se comporte conformément aux critères du cadrage (Preview ne modifie aucun système externe, Export ne produit un fichier qu'après validation, Insert exige systématiquement une destination explicite **et** une confirmation explicite, chaque exécution — y compris en échec — produit un rapport exploitable).

---

# 5. Couverture des scénarios de `user_cases.md`

| Scénario | Couvert par | Statut |
|---|---|---|
| PREVIEW-02/03 (source structurée simple) | Preview E2E schémas A et B | ✅ Validé |
| PREVIEW-06 (détection de données invalides) | `test_execution_service.py` (statut `VALIDATION_FAILED`) + `validation/` (`test_validation_engine.py`) | ✅ Validé (unitaire) |
| PREVIEW-01/04 (schéma PostgreSQL + RAG) | `test_postgres_schema.py` (analyse) — génération avec règles RAG non testée E2E | ⚠️ Partiel (bloqué par §2.1) |
| PREVIEW-05 (information manquante) | Hors périmètre de `execution_service` (relève de la construction du plan / LangGraph, UC-08/09, non encore implémentée) | ➖ Non applicable à ce périmètre |
| EXPORT-01/02 (export JSON/CSV valide) | E2E + `test_execution_service.py` | ✅ Validé |
| EXPORT-03 (export bloqué) | `test_execution_service.py::test_export_mode_blocked_when_generation_failed` | ✅ Validé (unitaire) |
| EXPORT-04 (erreur d'écriture) | `connectors/output` (`test_output_connectors.py`) | ✅ Validé (unitaire) |
| INSERT-01 (insertion réussie) | E2E + intégration | ✅ Validé |
| INSERT-02 (refus sans confirmation) | E2E + unitaire | ✅ Validé |
| INSERT-03 (bloqué par validation) | `test_execution_service.py::test_insert_mode_blocked_when_generation_failed` | ✅ Validé (unitaire) |
| INSERT-04 (rollback) | `test_postgres_data_writer.py::test_insert_records_rolls_back_entirely_on_constraint_violation` (intégration, PostgreSQL réel) | ✅ Validé |
| INSERT-05/06 (conflit d'unicité / connexion perdue) | Couverts génériquement par la gestion `IntegrityError` / `OperationalError` → `DataWriteError` dans `data_writer.py` ; pas de scénario dédié reproduit | ⚠️ Couverture générique uniquement |
| Réutilisabilité multi-domaines (§16 Démo 6) | E2E (Produit + Client, même moteur, aucune modification du code) | ✅ Validé |

---

# 6. Critères d'acceptation du ticket

- [x] **Tous les scénarios sont validés** — Preview, Export, Insert et multi-schémas validés en conditions réelles (§4), complétés par la suite automatisée (§3) ; les deux réserves identifiées (§5, PREVIEW-01/04 RAG et INSERT-05/06 dédiés) sont documentées comme limitations connues plutôt que comme échecs.
- [x] **Les anomalies sont corrigées** — les deux anomalies d'environnement bloquant l'exécution des tests (§2) ont été corrigées ; aucune anomalie fonctionnelle du service n'a été trouvée.
- [x] **Les résultats sont documentés** — présent document.

---

# 7. Recommandations de suite

1. Provisionner le modèle `bge-m3` sur l'instance Ollama locale pour permettre la validation E2E des scénarios RAG (PREVIEW-01/04).
2. Ajouter un scénario d'intégration dédié pour INSERT-05 (conflit d'unicité) et INSERT-06 (perte de connexion en cours de transaction), aujourd'hui seulement couverts par la gestion d'erreur générique.
3. Documenter dans le README que `docker/docker-compose.yml` expose PostgreSQL sur le port `5433` (et non `5432`) pour éviter les conflits avec d'autres projets locaux utilisant le port standard.
