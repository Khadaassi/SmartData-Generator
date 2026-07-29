# SmartData Generator

## Validation manuelle de l'interface Streamlit

**Version :** 1.0
**Statut :** À rejouer avant chaque soutenance (procédure manuelle, non automatisée)
**Projet de démonstration :** Pricing Control Tower (`pricing-control-tower-demo`)

---

# 1. Objectif

Documenter le scénario de test manuel permettant de vérifier que l'interface Streamlit
(`streamlit_app/`) fonctionne correctement de bout en bout comme client de l'API FastAPI
SmartData Generator, et que Pricing Control Tower peut être utilisé comme cas client de
démonstration sans introduire de logique métier spécifique dans le moteur générique.

Cette procédure complète les tests automatisés (`tests/test_streamlit_api_client.py`,
`tests/test_streamlit_payloads.py`, `tests/test_streamlit_error_mapping.py`), qui valident le
client API et la construction des payloads sans dépendre de Streamlit ni d'un service externe.

---

# 2. Prérequis

* Un service PostgreSQL accessible, exposant au moins une table simple d'un projet client
  (ex. `product` de Pricing Control Tower, ou toute table de test à contraintes maîtrisées).
* `.env` renseigné (cf. [.env.example](../../.env.example)), notamment `STREAMLIT_API_BASE_URL`.
* Dépendances installées : `uv sync`.

---

# 3. Procédure

## 3.1 Démarrage des services

```bash
uv run uvicorn api.app:app --host 0.0.0.0 --port 8000
uv run streamlit run streamlit_app/app.py
```

Ouvrir [http://localhost:8501](http://localhost:8501).

## 3.2 Étapes

| # | Étape | Résultat attendu |
|---|---|---|
| 1 | Vérifier l'indicateur de disponibilité dans la sidebar | `🟢 Disponible` avec la version du service |
| 2 | Page **Project** : saisir/valider `pricing-control-tower-demo` | Le projet actif est affiché, rappel de l'indexation RAG préalable |
| 3 | Page **Schema** : renseigner l'URL PostgreSQL de PCT (champ masqué) et analyser | Liste des tables, colonnes, types, clés primaires/étrangères, contraintes et ordre de génération affichés ; aucun mot de passe visible en clair |
| 4 | Page **Generation** : sélectionner l'entité `product` (ou équivalent simple) | Détail des champs, types et obligation affiché |
| 5 | Choisir un nombre d'enregistrements (ex. 5), mode **Preview**, lancer l'exécution | Message de succès, redirection implicite vers la page Result pour le détail |
| 6 | Page **Result** : vérifier les données | Tableau des données valides, `run_id`, statuts, compteurs (généré/valide/rejeté/erreurs/avertissements) |
| 7 | Vérifier le rapport de validation | Statut (`PASSED`/`PASSED_WITH_WARNINGS`/`PARTIAL`/`FAILED`), liste des problèmes avec champ, règle, sévérité |
| 8 | Retour page **Generation**, relancer en mode **Export JSON** (ou CSV) | Page Result : chemin d'export affiché, aucun faux succès si l'export échoue |
| 9 | Retour page **Generation**, relancer en mode **Insert PostgreSQL** sans cocher la confirmation | Bouton d'insertion désactivé : aucune insertion n'est possible |
| 10 | Cocher la confirmation, renseigner une cible explicite (base, schéma, table), lancer l'insertion | Page Result : nombre de lignes insérées, table cible, `run_id` |
| 11 | Vérifier dans Pricing Control Tower (ou la base cible) que les lignes ont bien été insérées | Les enregistrements générés sont présents en base |
| 12 | Arrêter l'API (`Ctrl+C`) puis recharger une page Streamlit | Indicateur `🔴 Indisponible`, actions d'analyse/génération désactivées, aucune erreur Streamlit non gérée |

---

# 4. Points de vigilance couverts

* Le mode par défaut proposé est bien **Preview** — aucune écriture n'a lieu sans passage explicite en Export ou Insert.
* Une erreur RAG non bloquante (ex. Ollama/`bge-m3` indisponible) apparaît comme avertissement sans masquer les données valides générées (comportement hérité de `agents/generation_agent.py`, cf. [service_validation_report.md](service_validation_report.md) section 2.1).
* Les données rejetées par la validation ne sont jamais proposées à l'export ou à l'insertion (l'API ne renvoie que les objets valides dans `generation.items`).
* Aucune URL PostgreSQL ni clé n'apparaît en clair dans l'interface ou dans les messages d'erreur (cf. `tests/test_streamlit_error_mapping.py`).

---

# 5. Résultat

À consigner lors de chaque rejeu (soutenance, démonstration client) : date, entité testée, statut de chaque étape, anomalies éventuelles. Le corpus documentaire de Pricing Control Tower est fourni comme documentation client au RAG ; aucune règle métier propre à PCT n'est codée dans `domain/rules.py` ou dans `streamlit_app/`.
