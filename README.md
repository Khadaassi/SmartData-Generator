# SmartData-Generator
AI-powered Business Data Generator

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
