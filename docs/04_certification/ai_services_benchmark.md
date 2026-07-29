# SmartData Generator

## Benchmark de services d'intelligence artificielle (C7)

**Version :** 1.1
**Statut :** Draft
**Projet :** SmartData Generator
**Compétence visée :** C7 — Identifier des services d'intelligence artificielle préexistants en analysant l'expression d'un besoin en fonctionnalités d'intelligence artificielle, en réalisant un benchmark de services existants et en analysant leurs caractéristiques pour formaliser une recommandation.
**Date :** 2026-07-29

---

# 1. Expression du besoin

Formalisée dans [`functional_technical_scope.md`](../01_framing/functional_technical_scope.md) §2-4 : générer des données métier synthétiques cohérentes à partir d'un schéma, de règles métier et d'une documentation métier, en combinant :

* une analyse déterministe du schéma cible ;
* un moteur d'intelligence artificielle pour la génération de contenu structuré ;
* un RAG pour exploiter la documentation métier ;
* un moteur de validation déterministe (le LLM ne valide jamais lui-même sa propre sortie).

Trois catégories de service IA en découlent : un **fournisseur LLM**, un **fournisseur d'embeddings**, et une **base vectorielle**.

---

# 2. Méthode de benchmark et niveau de preuve

Toutes les alternatives listées ci-dessous n'ont **pas** fait l'objet du même niveau d'évaluation. Pour rester honnête sur ce qui a été réellement mesuré, chaque ligne des tableaux suivants précise une colonne **Méthode d'évaluation**, avec les valeurs possibles :

| Méthode | Signification |
|---|---|
| Test comparatif réel | Le service a été exécuté dans l'environnement du projet et comparé sur un critère mesuré |
| Lecture de documentation officielle | Analyse des capacités déclarées par l'éditeur, sans exécution |
| Analyse de coût | Comparaison des grilles tarifaires publiques |
| Analyse de faisabilité | Contrainte technique constatée (compatibilité plateforme, dépendances) sans exécution complète du service |
| Analyse de confidentialité | Évaluation du traitement des données (où elles transitent, qui y a accès) à partir de la documentation |
| Non prototypé | Alternative identifiée et écartée sur dossier, sans test ni analyse approfondie — la décision reste défendable mais moins étayée que les autres |

---

# 3. Fournisseur LLM (génération de données structurées)

| Service évalué | Type | Méthode d'évaluation | Constat | Retenu |
|---|---|---|---|---|
| **Groq** (`llama-3.3-70b-versatile`) | API cloud, inférence LPU | Test comparatif réel | Latence d'inférence basse, tier gratuit compatible avec l'usage POC, `with_structured_output` (LangChain) fonctionne de façon fiable avec ce modèle dans l'environnement du projet — validé par des exécutions réelles (`docs/03_validation/service_validation_report.md` §4) | ✅ |
| OpenAI (GPT-4o / GPT-4o-mini) | API cloud | Analyse de coût + lecture de documentation officielle | Non prototypé dans ce POC. La documentation indique un support natif des sorties structurées compatible avec le besoin ; le coût par token en usage répété n'a pas été jugé justifié pour un POC face à Groq, sans qu'un gain de fiabilité ait été mesuré pour départager les deux | ❌ |
| LLM local via Ollama (ex. `llama3.2`, `mistral`) | Local, gratuit | Analyse de faisabilité (sur le matériel de développement utilisé pour ce projet) | Latence et qualité de sortie structurée jugées insuffisantes sur la machine de développement disponible, en comparaison de l'inférence Groq observée pendant les tests. Ce constat est lié à ce matériel précis et à ce périmètre ; il ne constitue pas une évaluation générale des LLM locaux | ❌ |

---

# 4. Fournisseur d'embeddings (RAG)

| Service évalué | Type | Méthode d'évaluation | Constat | Retenu |
|---|---|---|---|---|
| **Ollama / `bge-m3`** | Local, gratuit, multilingue | Test comparatif réel | Discrimination sémantique correcte sur des requêtes de test en français, dans le corpus RAG du projet | ✅ |
| Ollama / `mxbai-embed-large` | Local, gratuit | Test comparatif réel | Testé en premier (choix initial), puis écarté : 2 requêtes de test sur 4 mal classées en français (`README.md` §"Stack IA (local)", commit `c2b1843`) — seule comparaison du projet ayant produit une métrique chiffrée | ❌ |
| Fournisseur d'embeddings cloud (ex. OpenAI `text-embedding-3`) | API cloud | Analyse de confidentialité + analyse de coût | Non prototypé. Écarté sur dossier : la documentation métier envoyée pour indexation peut être sensible, un traitement local élimine son envoi à un tiers pour le seul calcul d'embeddings, et élimine un coût par appel | ❌ |

---

# 5. Base vectorielle (RAG)

| Service évalué | Type | Méthode d'évaluation | Constat | Retenu |
|---|---|---|---|---|
| **ChromaDB** | Local, HTTP, conteneurisé | Analyse de faisabilité + lecture de documentation officielle | Installation simple via `docker-compose`, intégration directe avec LangChain, adaptée au volume documentaire d'un POC. Contrainte technique constatée : le paquet `chromadb` complet ne s'installe pas sur macOS x86_64 + Python 3.12 (absence de wheel `onnxruntime` compatible) — le projet utilise donc `chromadb-client` (client HTTP léger) contre un serveur conteneurisé plutôt qu'un client embarqué | ✅ |
| Pinecone / Weaviate (SaaS managé) | Cloud managé | Non prototypé | Écarté sur dossier pour le POC : composant d'infrastructure externe supplémentaire à opérer et sécuriser, coût récurrent, sans bénéfice mesurable pour le volume documentaire visé | ❌ |
| pgvector (extension PostgreSQL) | Local, intégré à PostgreSQL existant | Non prototypé | Écarté sur dossier : aurait couplé le stockage vectoriel au moteur relationnel déjà utilisé pour un autre usage (persistance interne du service), contraire au principe de séparation des responsabilités (`functional_technical_scope.md` §12.2) | ❌ |

---

# 6. Recommandation formalisée

La combinaison retenue — **Groq (LLM) + Ollama/`bge-m3` (embeddings) + ChromaDB (vector store)**, chacune encapsulée derrière une interface d'un seul fichier (`infrastructure/llm.py`, `infrastructure/embeddings.py`, `rag/vectorstore.py`) — répond au besoin exprimé en combinant :

* un coût nul ou faible adapté à la phase POC ;
* une latence d'inférence compatible avec un modèle d'exécution synchrone (requête/réponse HTTP) ;
* la confidentialité de la documentation métier, en gardant le calcul d'embeddings local ;
* la remplaçabilité de chaque fournisseur (abstraction documentée, `functional_technical_scope.md` §12.8, vérifiée dans le code en §5.11/§8 de `technical_architecture.md`).

**Niveau de confiance de la recommandation** : élevé pour le choix d'embeddings (seule comparaison chiffrée du projet, §4) ; raisonnable mais non prototypé pour les alternatives LLM cloud et bases vectorielles managées (§3, §5) — à assumer clairement en soutenance plutôt que présenter ces choix comme le résultat d'un test comparatif qui n'a pas eu lieu.

---

# 7. Critères de validation de ce document

* chaque service comparé indique sa méthode d'évaluation réelle, sans confondre test et analyse documentaire ;
* la seule comparaison chiffrée du projet (embeddings) est identifiée comme telle et distinguée des autres ;
* la recommandation finale rappelle son propre niveau de confiance plutôt que de le laisser implicite.
