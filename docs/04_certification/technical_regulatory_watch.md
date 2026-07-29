# SmartData Generator

## Dispositif de veille technique et réglementaire (C6)

**Version :** 1.0
**Statut :** Draft
**Projet :** SmartData Generator
**Compétence visée :** C6 — Organiser et réaliser une veille technique et réglementaire en animant le travail collectif de sélection des sources, de collecte, de traitement et de partage des informations afin de formuler des recommandations pour le projet toujours en phase avec l'état de l'art.
**Date :** 2026-07-29

---

# 1. Avertissement sur le contexte de production

SmartData Generator est développé en solo, dans le cadre d'une certification individuelle. Il n'y a donc pas de « travail collectif » réel à documenter. Ce document décrit :

* le dispositif de veille **effectivement pratiqué** en solo (sources, méthode, traces produites) ;
* comment ce dispositif **serait partagé** dans un contexte d'équipe, sans prétendre que cette animation collective a eu lieu.

Les traces réellement produites — documentation, décisions d'architecture, historique Git, README — sont citées à chaque section, conformément à l'esprit du reste de la documentation du projet (préférer une preuve vérifiable à une déclaration d'intention).

---

# 2. Objectifs de la veille

* rester en phase avec l'état de l'art des outils d'orchestration LLM (LangChain/LangGraph), des fournisseurs d'inférence et des bases vectorielles ;
* détecter les évolutions ou limitations d'un outil retenu avant qu'elles ne deviennent bloquantes en production ;
* arbitrer entre plusieurs services candidats sur des critères vérifiables (coût, latence, confidentialité, compatibilité) plutôt que sur une préférence a priori ;
* documenter chaque changement de décision avec sa cause, pour qu'il reste traçable après coup (cf. [`technical_architecture.md`](../02_architecture/technical_architecture.md), note de révision v2.0).

---

# 3. Sujets surveillés

| Sujet | Pourquoi il est surveillé |
|---|---|
| Fournisseurs d'inférence LLM (Groq, alternatives cloud, exécution locale) | Coût, latence, fiabilité de la sortie structurée (`with_structured_output`) |
| Modèles et fournisseurs d'embeddings | Qualité de discrimination sémantique en français, coût, confidentialité |
| Bases vectorielles locales/managées | Complexité d'exploitation pour un POC, compatibilité LangChain |
| LangChain / LangGraph | Évolutions d'API (le projet dépend de versions récentes, `langgraph>=1.2.9`, `langchain>=1.3.14`), bonnes pratiques d'orchestration |
| SQLAlchemy / psycopg | Recommandations des mainteneurs pour les nouveaux projets (psycopg3 vs psycopg2) |
| Outillage projet (uv, ruff, python-semantic-release) | Fiabilité de la chaîne CI/CD, cohérence environnement local ↔ CI |

---

# 4. Sources sélectionnées

| Source | Type | Critère de fiabilité retenu |
|---|---|---|
| Documentation officielle Groq (console, API reference) | Documentation éditeur | Source primaire du fournisseur retenu |
| Documentation officielle LangChain / LangGraph | Documentation éditeur | Source primaire des bibliothèques d'orchestration utilisées |
| Documentation officielle Ollama et fiches modèles (`bge-m3`, `mxbai-embed-large`) | Documentation éditeur / registre de modèles | Description des capacités (multilinguisme, dimension d'embedding) avant test |
| Documentation officielle ChromaDB, SQLAlchemy 2.x, psycopg | Documentation éditeur | Justifie les choix §20 de `technical_architecture.md` |
| Changelogs et notes de version des dépendances (`pyproject.toml`) | Changelog éditeur | Bornes de version fixées volontairement (`langgraph>=1.2.9`, etc.) plutôt que "latest" non contrôlé |
| Expérimentation directe dans l'environnement du projet | Source primaire (test local) | Preuve la plus fiable pour ce périmètre : un test réel prime sur une documentation générale (cf. §5) |

---

# 5. Méthode de collecte et de synthèse

1. **Identification du besoin** avant recherche d'outil — cf. `functional_technical_scope.md` §2-4, rédigé avant le choix des fournisseurs.
2. **Lecture de la documentation officielle** des candidats plausibles pour chaque brique (LLM, embeddings, vector store).
3. **Test dans l'environnement réel du projet** quand le critère décisif ne peut pas être tranché par la documentation seule — c'est le cas pour le choix d'embeddings (§6).
4. **Synthèse écrite dans la documentation d'architecture**, au plus près du code (`technical_architecture.md` §20 "Choix techniques justifiés"), plutôt que dans un document de veille séparé du reste du projet — pour qu'une décision et sa justification ne divergent jamais.
5. **Révision a posteriori** : la note de révision v2.0 de `technical_architecture.md` documente explicitement les écarts entre la cible du cadrage (T1) et l'implémentation réelle, avec leur cause.

---

# 6. Exemple de décision issue directement de la veille : embeddings français

C'est la preuve la plus forte de veille **appliquée** du projet, car elle a changé une décision déjà prise.

1. Choix initial documenté : `mxbai-embed-large` (modèle d'embeddings générique, reconnu pour l'anglais).
2. Test réel sur des requêtes en français dans le corpus RAG du projet (`rag/corpus/examples/`).
3. Constat : 2 requêtes de test sur 4 mal classées (résultats sémantiquement proches mal discriminés).
4. Recherche d'une alternative multilingue : `bge-m3`.
5. Nouveau test : discrimination correcte.
6. Décision tracée par un commit daté et documenté : `c2b1843` — *"Update .env.example to change embeddings model from mxbai-embed-large to bge-m3 for improved multilingual support"*.
7. Résultat publié dans `README.md` §"Stack IA (local)", pour que toute personne reprenant le projet comprenne pourquoi `bge-m3` est la valeur par défaut et ne revienne pas en arrière sans le même test.

C'est un exemple concret de veille → collecte (documentation des deux modèles) → traitement (test comparatif) → partage (commit + README) → recommandation (valeur par défaut de `EMBEDDINGS_MODEL`).

---

# 7. Volet réglementaire

Le projet manipule potentiellement de la documentation métier et des données destinées à un fournisseur LLM tiers (Groq). Les points suivants sont traités à un niveau proportionné à un POC, sans prétendre à une conformité RGPD complète :

| Sujet réglementaire | Traitement dans le projet | Preuve |
|---|---|---|
| Minimisation des données envoyées au LLM | Le service ne doit pas utiliser de données personnelles réelles dans les prompts ; les données produites sont synthétiques | `functional_technical_scope.md` §18 "Gestion des données sensibles" |
| Confidentialité de la documentation métier | Les embeddings sont calculés **localement** via Ollama plutôt qu'envoyés à un fournisseur cloud, précisément pour ne pas exposer une documentation métier potentiellement sensible à un tiers | `technical_architecture.md` §20.6 |
| Exposition au fournisseur LLM cloud (Groq) | Seules les données déjà generées/schéma (pas de données personnelles réelles) transitent vers Groq ; le LLM ne reçoit jamais un secret applicatif (clé, mot de passe) | `functional_technical_scope.md` §17 "Contraintes de sécurité" |
| Gestion des secrets | Aucune clé API ni mot de passe dans le dépôt ; chargement exclusif via variables d'environnement (`.env`, ignoré par Git) | `.env.example`, `.gitignore`, `infrastructure/config.py::Settings` |
| Traçabilité des traitements | Chaque exécution porte un `run_id` unique, journalisé et persisté (`ExecutionReport`), y compris en cas d'échec | `technical_architecture.md` §3.6, `reporting/` |
| Licences et conditions d'utilisation des modèles | `llama-3.3-70b-versatile` via Groq (API commerciale, conditions Groq) ; `bge-m3` via Ollama (modèle en licence ouverte, exécuté localement, aucune donnée envoyée à un tiers pour l'embedding) | `.env.example`, `infrastructure/llm.py`, `infrastructure/embeddings.py` |
| Conséquences d'un changement de fournisseur cloud | L'abstraction fournisseur (`infrastructure/llm.py`, un seul fichier) limite l'impact d'un changement de politique tarifaire ou de disponibilité d'un fournisseur LLM à un seul point du code | `technical_architecture.md` §8 |

**Limite assumée** : ce volet réglementaire couvre les risques directement liés à l'usage d'un LLM tiers dans ce POC (confidentialité, minimisation, secrets). Il ne constitue pas une analyse d'impact RGPD (AIPD) formelle, qui sortirait du périmètre d'un POC non mis en production avec des données personnelles réelles (cf. `functional_technical_scope.md` §18, "Le POC ne constitue pas un outil d'anonymisation").

---

# 8. Fréquence et mode de partage (dispositif, contexte projet réel vs solo)

En solo, la veille a été pratiquée **au moment de chaque décision structurante** (ajout d'une dépendance, choix d'un fournisseur, changement de modèle) plutôt que selon un calendrier fixe — cohérent avec le rythme d'un POC à itérations courtes plutôt qu'un produit en exploitation continue.

Dans un contexte d'équipe, ce dispositif serait animé ainsi :

* **partage** : les décisions techniques et leur justification vivent dans `docs/02_architecture/technical_architecture.md` §20, versionné avec le code — visible par toute l'équipe à chaque revue de pull request, plutôt que dans un outil de veille séparé et vite obsolète ;
* **collecte collective** : chaque proposition de changement d'outil (ex. changer de fournisseur LLM) passerait par une entrée supplémentaire dans ce même tableau, avec la même structure (choix, alternative écartée, critère décisif) ;
* **fréquence** : revue à chaque introduction d'une nouvelle dépendance structurante (`pyproject.toml`), et à chaque incident d'environnement (cf. `service_validation_report.md` §2, anomalies traitées comme des déclencheurs de veille technique, pas seulement des bugs) ;
* **critères de fiabilité communs** : documentation officielle de l'éditeur en priorité, test réel dans l'environnement du projet quand la documentation ne suffit pas à trancher (cf. §6).

---

# 9. Autres décisions révisées grâce à la veille (hors embeddings)

Ces exemples illustrent une veille appliquée en continu, au-delà du cas le plus visible (§6) :

| Décision initiale (cadrage T1) | Décision révisée (implémentation réelle) | Cause identifiée |
|---|---|---|
| Un orchestrateur LangGraph unique pour tout le workflow | LangGraph limité au micro-workflow de génération (RAG → LLM → validation) | Un dispatcher `if/elif` simple suffit pour Preview/Export/Insert ; un graphe aurait ajouté de la complexité sans bénéfice (`technical_architecture.md` §20.4) |
| Connector Registry avec interfaces abstraites | Connecteurs = fonctions simples, sélectionnées par import direct | Avec 4 connecteurs fixes, un registre dynamique n'a aucun bénéfice mesurable ; documenté comme dette délibérée (§20.7) |
| `chromadb` embarqué/persistant local | `chromadb-client` HTTP vers un ChromaDB conteneurisé | Constat technique : pas de wheel `onnxruntime` compatible sur macOS x86_64 + Python 3.12 (`README.md`) |

---

# 10. Critères de validation de ce document

Ce document est considéré comme suffisant lorsque :

* les sources et sujets de veille sont explicites plutôt qu'implicites ;
* au moins une décision est démontrée comme **issue directement** de la veille, avec preuve datée (commit, document) ;
* le volet réglementaire est traité de façon proportionnée au périmètre réel du projet (POC, données synthétiques) ;
* les limites (solo vs collectif, périmètre RGPD non couvert) sont explicites plutôt que masquées.
