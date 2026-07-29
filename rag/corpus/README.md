# Corpus documentaire RAG

SmartData Generator est agnostique au domaine métier et réutilisable d'une entreprise à l'autre (cf. `docs/01_framing/functional_technical_scope.md`). **Aucune règle métier n'est codée dans le cœur du service** : la documentation métier est toujours fournie par le client, par projet.

Ce répertoire ne contient donc pas de corpus « officiel », mais :

* la **convention** que doit respecter tout document fourni par un client pour être exploitable par le pipeline d'ingestion (`rag/ingestion.py`) ;
* un **corpus d'exemple** générique ([examples/](examples/)), sur un domaine fictif (commandes e-commerce), utilisé uniquement pour tester et démontrer le pipeline (nettoyage, découpage, métadonnées). Il ne doit jamais être traité comme une source de vérité métier.

## Convention de document

* Format : Markdown (`.md`), encodage UTF-8.
* Chaque fichier représente un thème ou une entité (ex. `regles_commande.md`).
* Le fichier commence par un en-tête YAML (« front matter ») entre deux lignes `---` :

  ```markdown
  ---
  title: Règles de gestion des commandes
  category: rule
  entity: Commande
  ---
  ```

  * `title` (obligatoire) : titre lisible du document.
  * `category` (obligatoire) : une valeur parmi `definition`, `rule`, `constraint`, `example`, `relation`, `convention`, `limit`, `exception` (cf. `rag/schemas.py::DocumentCategory`, qui reprend la liste de la section 6.3 du cadrage).
  * `entity` (optionnel) : entité principale concernée (ex. `Commande`, `Client`), pour affiner la recherche RAG par entité.

* Le corps du document est découpé en sections avec des titres de niveau 2 (`## Titre de la section`). **Une section = une règle ou une information autonome**, compréhensible sans le reste du document : le pipeline découpe le texte par section avant de le re-découper par taille, donc une section trop dense ou trop dépendante du contexte voisin produira des chunks moins pertinents pour la recherche vectorielle.

## Pipeline d'ingestion

`rag/ingestion.py::ingest_document` applique, pour chaque fichier :

1. lecture du fichier et extraction du front matter (`rag/schemas.py::DocumentFrontMatter`) ;
2. nettoyage du contenu (`rag/cleaning.py::clean_text`) : normalisation Unicode, fins de ligne, espaces superflus ;
3. découpage (`rag/chunking.py::chunk_markdown`) : par section `##`, puis par taille (800 caractères, 100 de recouvrement) ;
4. production des métadonnées par chunk (`rag/schemas.py::ChunkMetadata`), prêtes à être passées à `rag/vectorstore.py::add_texts` pour indexation dans ChromaDB.

`rag/ingestion.py::ingest_corpus` applique ce traitement à tous les fichiers `.md` d'un répertoire (le répertoire de documents d'un projet donné, cf. `DOCUMENTS_STORAGE_DIR`).
