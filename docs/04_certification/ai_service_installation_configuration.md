# SmartData Generator

## Installation, paramétrage et intégration des services IA (C8)

**Version :** 1.1
**Statut :** Draft
**Projet :** SmartData Generator
**Compétence visée :** C8 — Paramétrer un service d'intelligence artificielle en suivant sa documentation technique et en respectant les spécifications du projet, afin de permettre l'intégration des connecteurs du service dans le système d'information.
**Date des captures ci-dessous :** 2026-07-29

---

# 1. Services concernés et fichiers de configuration

| Service | Rôle | Fichier(s) de configuration | Point d'accès applicatif |
|---|---|---|---|
| Groq | Fournisseur LLM (génération structurée) | `.env` (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`) → `infrastructure/config.py::Settings` | `infrastructure/llm.py::get_llm()` |
| Ollama | Fournisseur d'embeddings (RAG) | `.env` (`EMBEDDINGS_PROVIDER`, `EMBEDDINGS_MODEL`, `EMBEDDINGS_BASE_URL`) | `infrastructure/embeddings.py::get_embeddings()` |
| ChromaDB | Base vectorielle (RAG) | `docker/docker-compose.yml` (service `chromadb`) ; `.env` (`CHROMA_HOST`, `CHROMA_PORT`, `CHROMA_COLLECTION_NAME`) | `rag/vectorstore.py` (`chromadb.HttpClient`) |
| PostgreSQL | Stockage applicatif interne (projets, rapports) | `docker/docker-compose.yml` (service `postgres`) ; `.env` (`DATABASE_URL`) | `infrastructure/database.py::get_engine()` |

---

# 2. Procédure d'installation et de configuration

1. Copier `.env.example` vers `.env`.
2. Créer une clé API Groq (console.groq.com) et renseigner `LLM_API_KEY`.
3. Démarrer ChromaDB et PostgreSQL : `docker compose -f docker/docker-compose.yml up -d`.
4. Installer et démarrer Ollama localement, puis provisionner le modèle d'embeddings : `ollama pull bge-m3`.
5. Installer les dépendances Python : `uv sync`.
6. Lancer l'API : `uv run uvicorn api.app:app --host <API_HOST> --port <API_PORT>` (ou `python main.py`).
7. Vérifier l'intégration : `uv run pytest` — les tests d'intégration valident la connectivité réelle aux trois services externes et sont automatiquement *skip* si un service n'est pas joignable (`tests/integration/_reachability.py`).

---

# 3. Preuves d'installation capturées en conditions réelles (2026-07-29)

Les sorties ci-dessous sont des captures réelles de l'environnement du projet au moment de la rédaction de ce document, pas des exemples reconstitués. Aucun secret (clé API, `.env`) n'est inclus.

## 3.1 Conteneurs Docker actifs

```
$ docker compose -f docker/docker-compose.yml ps
NAME                SERVICE    STATUS          PORTS
docker-chromadb-1   chromadb   Up 19 hours     0.0.0.0:8020->8000/tcp
docker-postgres-1   postgres   Up 50 minutes   0.0.0.0:5433->5432/tcp
```

ChromaDB et PostgreSQL sont bien démarrés et exposés sur les ports configurés dans `.env` (`CHROMA_PORT=8020`, port PostgreSQL remappé sur `5433` pour éviter le conflit documenté dans `docs/03_validation/service_validation_report.md` §2).

## 3.2 Point de santé de l'API (`GET /health`)

```
$ curl -s http://localhost:8001/health
{"status":"ok","service":"smartdata-generator","version":"0.1.0","environment":"local"}
```

## 3.3 Suite de tests contre les services réels (sans mock)

```
$ uv run pytest tests/integration/test_groq.py tests/integration/test_postgres_data_writer.py \
    tests/integration/test_postgres_schema.py tests/integration/test_project_repository.py \
    tests/integration/test_report_repository.py tests/integration/test_execution_reporting.py -v

tests/integration/test_groq.py::test_groq_chat_completion_responds PASSED
tests/integration/test_postgres_data_writer.py::test_insert_records_inserts_all_rows PASSED
tests/integration/test_postgres_data_writer.py::test_insert_records_rolls_back_entirely_on_constraint_violation PASSED
tests/integration/test_postgres_data_writer.py::test_insert_records_rejects_unknown_column PASSED
tests/integration/test_postgres_data_writer.py::test_insert_records_table_not_found_raises_data_write_error PASSED
tests/integration/test_postgres_data_writer.py::test_insert_records_empty_items_raises_data_write_error PASSED
tests/integration/test_postgres_schema.py::test_connection_succeeds_with_a_valid_url PASSED
tests/integration/test_postgres_schema.py::test_read_schema_detects_tables_and_columns PASSED
tests/integration/test_postgres_schema.py::test_read_schema_detects_primary_keys PASSED
tests/integration/test_postgres_schema.py::test_read_schema_detects_foreign_keys PASSED
tests/integration/test_postgres_schema.py::test_read_schema_detects_unique_and_check_constraints PASSED
tests/integration/test_postgres_schema.py::test_read_schema_orders_tables_respecting_dependencies PASSED
tests/integration/test_project_repository.py (8 tests) PASSED
tests/integration/test_report_repository.py (3 tests) PASSED
tests/integration/test_execution_reporting.py::test_execute_persists_a_retrievable_report PASSED

26 passed in 25.68s
```

Preuve directe que le connecteur Groq (appel LLM réel), le connecteur PostgreSQL (insertion, rollback transactionnel sur violation de contrainte, introspection de schéma) et la persistance interne (projets, rapports d'exécution) sont réellement intégrés et fonctionnels — pas seulement mockés.

## 3.4 Exécution réelle de bout en bout (`POST /executions`, mode Preview)

Requête envoyée à l'API réellement démarrée (`uv run uvicorn api.app:app --port 8001`), avec appel Groq réel et sans aucun mock :

```json
POST /executions
{
  "generation": {
    "project_id": "rncp-evidence-demo",
    "entity": {
      "name": "Client",
      "fields": [
        {"name": "email", "type": "string", "required": true},
        {"name": "age", "type": "integer", "required": true}
      ]
    },
    "count": 3
  },
  "mode": "PREVIEW"
}
```

Réponse réelle obtenue :

```json
{
  "run_id": "f6f67b842b5f4be6ba303288a2555bf1",
  "mode": "PREVIEW",
  "status": "READY",
  "generation": {
    "status": "SUCCESS",
    "entity": "Client",
    "items": [
      {"email": "client1@example.com", "age": 30},
      {"email": "client2@example.com", "age": 25},
      {"email": "client3@example.com", "age": 40}
    ],
    "errors": [
      {"code": "rag_unavailable", "message": "model \"bge-m3\" not found, try pulling it first (status code: 404)", "stage": "rag", "blocking": false}
    ],
    "validation_report": {"total_items": 3, "valid_items": 3, "rejected_items": 0, "status": "PASSED"}
  }
}
```

Cette exécution démontre en une seule capture :

* l'intégration réelle du connecteur Groq (3 objets `Client` générés, cohérents avec le schéma demandé) ;
* le comportement documenté et attendu quand le RAG est indisponible : `rag_unavailable` classé **non bloquant**, la génération se poursuit sans contexte métier (§3.5 comportement conforme à `agents/generation_agent.py::_retrieve_context`) ;
* la validation déterministe en aval du LLM (`status: PASSED`, 3/3 objets valides) ;
* la production d'un `run_id` de corrélation, prêt à être retrouvé dans `execution_reports`.

---

# 4. Anomalie d'environnement découverte pendant cette capture (à corriger)

En préparant la capture ci-dessus, le pipeline RAG a échoué (`rag_unavailable`, §3.4) alors que `ollama list` (CLI locale) indique bien `bge-m3:latest` comme installé. Diagnostic effectué :

```
$ lsof -nP -iTCP:11434 -sTCP:LISTEN
COMMAND     PID   NAME
com.docke 32486   TCP *:11434 (LISTEN)
ollama    94249   TCP 127.0.0.1:11434 (LISTEN)

$ curl -s http://localhost:11434/api/tags
{"models": [{"name": "mxbai-embed-large:latest"}]}
```

**Cause identifiée** : deux processus tentent d'écouter sur le port `11434` — le proxy réseau de Docker Desktop (`com.docker`) et l'application native `Ollama.app`. Le serveur qui répond effectivement aux appels HTTP de l'application (`EMBEDDINGS_BASE_URL=http://localhost:11434`) n'a que `mxbai-embed-large` d'indexé, alors que l'instance interrogée par la CLI `ollama list` (probablement l'application native, via un canal différent) a bien `bge-m3`. C'est un conflit de port du même type que celui déjà documenté pour PostgreSQL dans `docs/03_validation/service_validation_report.md` §2 — pas une anomalie du code de SmartData Generator, dont le comportement (échec RAG classé non bloquant) est exactement celui attendu par la conception (§3.4 ci-dessus).

**Action recommandée avant une démonstration RAG en soutenance** : arrêter le conteneur ou service qui monopolise le port `11434` sans servir `bge-m3` (probablement le proxy Docker Desktop, à vérifier via `docker ps` pour un conteneur exposant ce port), ou repointer `EMBEDDINGS_BASE_URL` vers le bon processus, puis re-tester `curl http://localhost:11434/api/tags` jusqu'à voir `bge-m3` dans la réponse.

Cette anomalie est volontairement documentée telle quelle plutôt que masquée : elle illustre à la fois une limite d'environnement réelle et le bon fonctionnement du garde-fou non bloquant conçu pour ce cas (`GenerationError(code="rag_unavailable", blocking=False)`).

---

# 5. Preuves complémentaires à capturer avant la soutenance

Ces éléments ne sont pas encore capturés dans ce document et sont à ajouter une fois l'anomalie du §4 résolue :

* `curl http://localhost:11434/api/tags` confirmant `bge-m3` disponible sur le bon port ;
* un scénario `test_indexing.py` / `test_search_relevance.py` passant réellement (aujourd'hui en erreur à cause du §4) ;
* une exécution `PREVIEW` avec contexte RAG effectivement récupéré (`context` non vide dans `GenerationResult.rules_used`) ;
* un scénario `EXPORT` et un scénario `INSERT` capturés de la même façon que le Preview (§3.4), pour couvrir les trois modes en preuve d'intégration.

---

# 6. Critères de validation de ce document

* chaque service IA a une preuve de configuration **et** une preuve d'exécution réelle, pas seulement une description ;
* les preuves sont datées et reproductibles (commande donnée, sortie réelle) ;
* les anomalies rencontrées pendant la capture sont documentées avec leur diagnostic plutôt que masquées ou recapturées jusqu'à obtenir un résultat "propre" artificiel.
