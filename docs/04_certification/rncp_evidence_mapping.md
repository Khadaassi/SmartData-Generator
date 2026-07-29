# SmartData Generator

## Cartographie des preuves RNCP — Compétences mobilisées

**Version :** 2.0
**Statut :** Draft — support de préparation à la soutenance
**Projet :** SmartData Generator
**Certification :** RNCP Développeur en Intelligence Artificielle
**Date :** 2026-07-29

---

# 1. Objectif de ce document

Ce document consolide les éléments de preuve démontrant les compétences mobilisées dans le développement de SmartData Generator, pour préparer la soutenance RNCP. Il ne remplace pas le **rapport professionnel individuel** exigé par le bloc d'évaluation IA (§3) — il indexe et synthétise les preuves détaillées dans les documents dédiés du dossier, plus les preuves déjà présentes dans le dépôt (documentation, code, tests, historique Git).

Chaque preuve citée est vérifiable directement dans le dépôt : chemin de fichier, section de document ou identifiant de commit.

---

# 2. Périmètre de ce document

Le présent dossier est **volontairement centré sur les compétences C6, C7 et C8**, correspondant au cas pratique évalué pour ce bloc par un rapport professionnel individuel et une soutenance orale. Les autres compétences mobilisées par SmartData Generator (développement API, connecteurs, tests, traçabilité, etc.) sont présentées à titre transversal en §6, mais ne constituent pas le périmètre principal de ce rapport.

Le détail de chaque compétence C6/C7/C8 est traité dans un document dédié plutôt que dupliqué ici :

| Compétence | Document dédié |
|---|---|
| C6 — Veille technique et réglementaire | [`technical_regulatory_watch.md`](technical_regulatory_watch.md) |
| C7 — Benchmark de services IA et recommandation | [`ai_services_benchmark.md`](ai_services_benchmark.md) |
| C8 — Installation, paramétrage et intégration | [`ai_service_installation_configuration.md`](ai_service_installation_configuration.md) |

---

# 3. Synthèse C6 / C7 / C8

## 3.1 C6 — Veille technique et réglementaire

> *« Organiser et réaliser une veille technique et réglementaire en animant le travail collectif de sélection des sources, de collecte, de traitement et de partage des informations afin de formuler des recommandations pour le projet toujours en phase avec l'état de l'art. »*

Traité en détail dans [`technical_regulatory_watch.md`](technical_regulatory_watch.md) : objectifs, sujets et sources surveillés, méthode de collecte/synthèse, exemple de décision directement issue de la veille (remplacement de `mxbai-embed-large` par `bge-m3`, commit `c2b1843`), volet réglementaire (minimisation des données, confidentialité, secrets, licences), et mode de partage envisagé dans un contexte d'équipe.

**Point d'attention pour la soutenance** : le projet étant réalisé en solo, la dimension « animation du travail collectif » est présentée comme un dispositif transposable, pas comme un fait vécu — cette nuance est assumée explicitement dans le document dédié plutôt que dissimulée.

## 3.2 C7 — Identification de services IA préexistants (benchmark)

> *« Identifier des services d'intelligence artificielle préexistants en analysant l'expression d'un besoin en fonctionnalités d'intelligence artificielle, en réalisant un benchmark de services existants et en analysant leurs caractéristiques pour formaliser une recommandation. »*

Traité en détail dans [`ai_services_benchmark.md`](ai_services_benchmark.md) : expression du besoin, benchmark LLM (Groq / OpenAI / LLM local), embeddings (`bge-m3` / `mxbai-embed-large` / cloud) et base vectorielle (ChromaDB / Pinecone-Weaviate / pgvector), avec pour chaque alternative une **méthode d'évaluation explicite** (test comparatif réel, lecture de documentation, analyse de coût/faisabilité/confidentialité, ou non prototypé) — pour ne présenter comme "testé" que ce qui l'a réellement été.

**Point d'attention pour la soutenance** : seule la comparaison des fournisseurs d'embeddings repose sur un test comparatif chiffré. Les autres choix (LLM cloud, base vectorielle) sont défendables mais reposent sur une analyse documentaire et de faisabilité, pas sur un prototype comparatif — le document dédié le précise pour chaque ligne.

## 3.3 C8 — Paramétrage d'un service d'intelligence artificielle

> *« Paramétrer un service d'intelligence artificielle en suivant sa documentation technique et en respectant les spécifications du projet, afin de permettre l'intégration des connecteurs du service dans le système d'information. »*

Traité en détail dans [`ai_service_installation_configuration.md`](ai_service_installation_configuration.md) : procédure d'installation, fichiers de configuration par service, et **preuves capturées en conditions réelles le 2026-07-29** (conteneurs Docker actifs, suite de tests d'intégration passée contre les services réels — dont un appel Groq réel et un rollback PostgreSQL réel —, et une exécution `POST /executions` réelle de bout en bout avec réponse LLM effective). Une anomalie d'environnement découverte pendant cette capture (conflit de port Ollama empêchant l'accès à `bge-m3`) y est diagnostiquée et documentée plutôt que masquée.

---

# 4. Table de correspondance synthétique C6 / C7 / C8

| Compétence | Preuve la plus forte | Démonstration en soutenance |
|---|---|---|
| C6 | Commit `c2b1843` + `README.md` (décision de veille ayant changé un choix déjà pris) | Expliquer pourquoi le choix d'embeddings a changé en cours de projet, et ce qui a motivé le changement |
| C7 | Tableaux de benchmark avec méthode d'évaluation explicite (`ai_services_benchmark.md`) | Présenter la comparaison Groq/OpenAI/local et `bge-m3`/`mxbai-embed-large`, en distinguant ce qui a été testé de ce qui a été analysé sur dossier |
| C8 | Capture réelle du 2026-07-29 : tests d'intégration + exécution `POST /executions` réussie (`ai_service_installation_configuration.md` §3) | Démarrer les services (Docker, Ollama), exécuter une génération réelle de bout en bout (Preview → Export/Insert), montrer le rapport d'exécution produit |

---

# 5. Inventaire des démonstrations possibles en soutenance

Repris de [`user_cases.md`](../01_framing/user_cases.md) §16 ("Scénarios de démonstration retenus"), déjà exécutés et validés en conditions réelles (`docs/03_validation/service_validation_report.md` §4, complété par une nouvelle capture en §3.4 de `ai_service_installation_configuration.md`) :

1. **Preview PostgreSQL / fichier** — analyse de schéma, génération, validation, aperçu sans écriture.
2. **Export** — génération d'un fichier JSON et CSV à partir d'une exécution validée.
3. **Insert** — confirmation explicite, insertion transactionnelle, vérification en base.
4. **Erreur de validation** — injection d'une donnée invalide, blocage de l'écriture.
5. **Rollback** — violation de contrainte pendant l'insertion, absence de données partielles (`test_insert_records_rolls_back_entirely_on_constraint_violation`, revalidé le 2026-07-29).
6. **Réutilisabilité multi-domaines** — même moteur exécuté sur deux schémas métier distincts (`Produit`, `Client`) sans modification du code.

---

# 6. Autres compétences transverses mobilisées (hors bloc C6-C8)

Hors périmètre principal de ce rapport (§2). Basées sur les objectifs pédagogiques déclarés dans [`functional_technical_scope.md`](../01_framing/functional_technical_scope.md) §4.4, sans code RNCP officiel assigné (à recoder avec le référentiel de formation si ces compétences doivent être évaluées formellement dans un autre bloc).

| Objectif pédagogique déclaré | Preuve principale |
|---|---|
| Analyse d'un besoin intégrant un service IA | `functional_technical_scope.md` §2-4 |
| Définition des spécifications fonctionnelles | `user_cases.md` (UC-01 à UC-16, scénarios Preview/Export/Insert) |
| Conception du cadre technique d'une application IA | `technical_architecture.md` (v1.0 cible + v2.0 réelle, diagrammes Mermaid) |
| Intégration d'un service d'intelligence artificielle | `agents/generation_agent.py` (graphe LangGraph à 5 nœuds), `infrastructure/llm.py`, `infrastructure/embeddings.py` |
| Développement d'une API REST | `api/` (FastAPI, routers `executions`, `schema_analysis`, `health`), documentation OpenAPI automatique |
| Collecte et mise à disposition de données | `rag/ingestion.py`, `rag/indexing.py`, `domain/schema.py::build_entity_model` |
| Connexion à différentes sources de données | `connectors/input/` (CSV, JSON, REST), `connectors/postgres/schema_reader.py` |
| Développement de composants applicatifs | `application/execution_service.py`, `application/project_service.py`, `validation/engine.py` |
| Validation et tests automatisés | `tests/` — 111 tests unitaires + 26 tests d'intégration revalidés le 2026-07-29, CI `ruff` + `pytest` sur chaque push (`.github/workflows/ci.yml`) |
| Traçabilité des traitements | `run_id` de corrélation systématique, `reporting/report_builder.py`, `reporting/report_service.py`, table `execution_reports` |
| Documentation technique et fonctionnelle | `docs/01_framing/`, `docs/02_architecture/`, `docs/03_validation/`, `docs/04_certification/` |
| Industrialisation progressive d'un POC IA | CI/CD (`.github/workflows/ci.yml`), versioning sémantique automatisé (`python-semantic-release`), `docker-compose.yml`, gestion de dépendances verrouillée (`uv`) |

---

# 7. Limites et actions restantes avant la soutenance

* **C6** : dispositif de veille désormais formalisé (`technical_regulatory_watch.md`) ; reste à préparer une réponse orale claire sur la nuance solo/collectif si le jury interroge sur ce point.
* **C7** : benchmark reformulé avec méthode d'évaluation explicite par ligne ; reste, si le temps le permet avant la soutenance, à prototyper au moins un test réel supplémentaire (ex. un appel OpenAI comparatif) pour renforcer la preuve au-delà du seul cas des embeddings.
* **C8** : anomalie de port Ollama diagnostiquée le 2026-07-29 (`ai_service_installation_configuration.md` §4) — à corriger avant la soutenance pour pouvoir démontrer un scénario RAG complet (aujourd'hui les scénarios Preview/Export/Insert fonctionnent réellement, mais sans contexte RAG récupéré) ; capturer ensuite les scénarios Export et Insert de la même façon que le Preview (§5 du document C8).
* **Autres compétences (§6)** : à faire valider/recoder avec les codes exacts du référentiel RNCP complet (blocs hors C6-C8) pour un dossier de preuve définitif sur ce périmètre transversal.

---

# 8. Critères d'acceptation du ticket

- [x] Les preuves sont identifiées
- [x] C7 est couvert
- [x] C8 est couvert
- [x] C6 est couvert (dispositif de veille formalisé + volet réglementaire, `technical_regulatory_watch.md`)
- [x] Les démonstrations sont associées (§5)
- [x] Les preuves techniques sont localisées (chemins de fichiers, commits, captures datées)
- [x] Les résultats sont documentés
- [x] Le dispositif de veille est formalisé (`technical_regulatory_watch.md`)
- [x] La veille réglementaire est explicitement documentée (`technical_regulatory_watch.md` §7)
- [x] Le benchmark distingue tests réels et analyse documentaire (`ai_services_benchmark.md` §2)
- [x] Le dossier de preuve est complet pour le périmètre C6/C7/C8 — limites explicitement listées en §7 plutôt que masquées
