# SmartData-Generator
AI-powered Business Data Generator

## Stack IA (local)

Copier [.env.example](.env.example) vers `.env` et renseigner `LLM_API_KEY` (clé [Groq](https://console.groq.com/keys)).

Deux services externes sont nécessaires en local :

* **ChromaDB** (base vectorielle du RAG) : `docker compose -f docker/docker-compose.yml up -d`, exposé sur `http://localhost:8020`.
* **Ollama** (embeddings, exécuté en local ou via un autre conteneur) : doit tourner sur `http://localhost:11434` avec le modèle `bge-m3` disponible (`ollama pull bge-m3`). Multilingue : testé et préféré à `mxbai-embed-large`, qui discrimine mal les phrases françaises proches sémantiquement (2 requêtes de test sur 4 mal classées).

> Le package complet `chromadb` ne s'installe pas sur macOS x86_64 + Python 3.12 (pas de wheel `onnxruntime` compatible). Le projet utilise donc `chromadb-client` (client HTTP léger, sans `onnxruntime`) pour se connecter à un serveur Chroma lancé via Docker plutôt qu'un client embarqué/persistant local.

Vérification (`uv run pytest`) :

* [tests/test_langgraph_smoke.py](tests/test_langgraph_smoke.py), [tests/test_rag_corpus.py](tests/test_rag_corpus.py) : toujours exécutés, ne dépendent d'aucun service externe.
* [tests/integration/test_indexing.py](tests/integration/test_indexing.py), [tests/integration/test_search_relevance.py](tests/integration/test_search_relevance.py) : exécutés si Chroma et Ollama sont accessibles, sinon *skip*.
* [tests/integration/test_groq.py](tests/integration/test_groq.py) : exécuté si `LLM_API_KEY` est renseignée dans `.env`, sinon *skip*.

### Indexation et recherche RAG

* `rag/ingestion.py` : lit un corpus de documents Markdown (cf. [rag/corpus/README.md](rag/corpus/README.md)), nettoie et découpe le contenu, produit les métadonnées par chunk.
* `rag/indexing.py::index_corpus(corpus_dir, project_id)` : ingère puis indexe (upsert, idempotent) un corpus dans ChromaDB.
* `rag/vectorstore.py::search(query, project_id, k, entity)` : recherche sémantique filtrée par projet (et éventuellement par entité), retourne texte + métadonnées + score de distance.

## Versioning

Le projet suit [Semantic Versioning](https://semver.org/lang/fr/) (`MAJOR.MINOR.PATCH`) et le versioning est **automatisé** via [python-semantic-release](https://python-semantic-release.readthedocs.io/) sur la branche `main`.

Les messages de commit doivent suivre [Conventional Commits](https://www.conventionalcommits.org/fr/) pour déterminer le bump de version :

* `fix:` → **PATCH** (correctif rétrocompatible) ;
* `feat:` → **MINOR** (fonctionnalité rétrocompatible) ;
* `feat!:`, `fix!:` ou pied de commit `BREAKING CHANGE:` → **MAJOR** (incompatible) ;
* `docs:`, `refactor:`, `test:`, `chore:`, `ci:`, `style:`, `perf:` → pas de release déclenchée par défaut (sauf `perf` qui compte comme `fix`).

Tant que le projet est en phase de POC, la version reste en `0.MINOR.PATCH` (`major_on_zero = false`) : un commit `!`/`BREAKING CHANGE` bump le **MINOR** au lieu du **MAJOR** tant que la version n'a pas été passée manuellement à `1.0.0`, qui marquera la première version stable du POC industrialisable.

### Fonctionnement

À chaque push sur `main`, une fois le job `lint-and-test` de la CI validé, le job `release` du workflow [ci.yml](.github/workflows/ci.yml) :

1. analyse les commits depuis le dernier tag ;
2. calcule la prochaine version et met à jour `project.version` dans [pyproject.toml](pyproject.toml) ;
3. génère/complète [CHANGELOG.md](CHANGELOG.md) ;
4. commite ce bump, crée le tag `vMAJOR.MINOR.PATCH` et une GitHub Release associée.

S'il n'y a aucun commit `fix`/`feat`/breaking depuis le dernier tag, aucune release n'est créée.

> **Prérequis dépôt** : si une règle de protection est activée sur `main` (revue obligatoire, statuts requis), il faut autoriser le `GITHUB_TOKEN` par défaut à pousser directement (ou fournir un token dédié), sinon le commit de bump du job `release` sera rejeté.
