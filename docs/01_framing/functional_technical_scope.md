# SmartData Generator

## Cadrage fonctionnel et technique

**Version :** 1.0
**Statut :** Draft
**Projet :** SmartData Generator
**Type de projet :** Proof of Concept industrialisable
**Contexte :** Certification RNCP Développeur en Intelligence Artificielle

---

# 1. Présentation du projet

SmartData Generator est un service d’intelligence artificielle conçu pour générer des données métier synthétiques, cohérentes et exploitables à partir d’un contexte fourni par l’utilisateur.

Le service s’appuie principalement sur :

* un schéma de données cible ;
* des règles métier explicites ;
* une documentation métier ;
* des paramètres de génération ;
* un système de validation ;
* des connecteurs permettant de lire et d’écrire les données.

SmartData Generator est conçu comme un produit indépendant et réutilisable.

Il ne doit contenir aucune logique métier spécifique à une application cliente ou à un domaine fonctionnel particulier.

Pricing Control Tower sera utilisé comme démonstrateur du service, mais aucune règle propre au pricing, aux produits, aux magasins ou aux promotions ne doit être directement implémentée dans le cœur de SmartData Generator.

Les spécificités d’un projet doivent être fournies au service au moyen de configurations, de schémas, de règles et de documents externes.

---

# 2. Contexte et problématique

Les équipes de développement, de data et de test ont régulièrement besoin de données fictives pour :

* développer une application ;
* tester une API ;
* valider un pipeline de données ;
* alimenter un environnement de démonstration ;
* reproduire un incident ;
* effectuer des tests fonctionnels ou d’intégration ;
* tester des règles métier ;
* préparer une présentation.

Dans de nombreux projets, ces données sont produites à l’aide de scripts spécifiques.

Ces scripts sont souvent :

* fortement couplés à une base ou à un domaine métier ;
* difficiles à maintenir ;
* peu documentés ;
* peu réutilisables ;
* limités à un format précis ;
* incapables de prendre en compte une documentation métier complexe ;
* insuffisamment contrôlés avant l’insertion des données.

La génération aléatoire classique ne garantit pas la cohérence fonctionnelle.

Un outil peut, par exemple, produire des valeurs conformes aux types SQL mais incohérentes du point de vue métier.

À l’inverse, un modèle de langage peut comprendre des règles métier, mais il ne doit pas être considéré comme une source fiable pour l’analyse technique d’un schéma ou pour l’exécution directe d’opérations sensibles.

SmartData Generator vise donc à combiner :

* une analyse déterministe du schéma cible ;
* un moteur d’intelligence artificielle pour la compréhension et la planification ;
* un RAG pour exploiter la documentation métier ;
* des sorties structurées ;
* un moteur de validation déterministe ;
* une confirmation explicite avant toute insertion.

---

# 3. Vision du produit

La vision de SmartData Generator est de proposer un composant générique capable de comprendre le contexte d’un projet de données et d’accompagner la génération d’un jeu de données cohérent de bout en bout.

Le service doit être capable de :

1. analyser une source ou une destination ;
2. comprendre la structure technique du schéma ;
3. récupérer les règles métier pertinentes ;
4. construire un plan de génération ;
5. identifier les informations manquantes ;
6. générer des données structurées ;
7. valider les données générées ;
8. présenter un aperçu ;
9. exporter ou insérer les données ;
10. produire un rapport d’exécution.

SmartData Generator est conçu comme un POC industrialisable.

Le POC doit démontrer la faisabilité technique, la valeur du produit et la qualité de l’architecture, sans chercher à couvrir tous les formats et tous les systèmes existants.

---

# 4. Objectifs du projet

## 4.1 Objectif principal

L’objectif principal est de développer un service IA réutilisable capable de générer des données métier synthétiques conformes à un schéma cible et aux règles fonctionnelles fournies.

Les données produites doivent être :

* techniquement valides ;
* cohérentes entre elles ;
* conformes aux contraintes du schéma ;
* conformes aux règles métier ;
* vérifiables avant écriture ;
* accompagnées d’un rapport d’exécution.

---

## 4.2 Objectifs fonctionnels

SmartData Generator doit permettre de :

* créer et configurer un projet de génération ;
* connecter différentes sources et destinations ;
* analyser un schéma cible ;
* charger une documentation métier ;
* indexer les documents dans une base vectorielle ;
* rechercher les règles utiles grâce au RAG ;
* définir les paramètres de génération ;
* construire un plan de génération ;
* générer des données structurées ;
* détecter les erreurs et incohérences ;
* présenter un aperçu avant insertion ;
* exporter les données ;
* insérer les données après validation explicite ;
* consulter un rapport détaillé de l’exécution.

---

## 4.3 Objectifs techniques

Les objectifs techniques sont les suivants :

* mettre en place une architecture modulaire ;
* découpler les connecteurs du moteur IA ;
* abstraire le fournisseur LLM ;
* abstraire le fournisseur d’embeddings ;
* utiliser des contrats de données stricts ;
* orchestrer le workflow avec LangGraph ;
* exploiter LangChain pour l’intégration du LLM et du RAG ;
* utiliser ChromaDB comme base vectorielle ;
* exposer les fonctionnalités avec une API FastAPI ;
* supporter PostgreSQL comme base relationnelle ;
* permettre l’export CSV et JSON ;
* produire des logs structurés ;
* rendre les exécutions traçables ;
* automatiser les tests des composants critiques.

---

## 4.4 Objectifs pédagogiques et RNCP

Dans le cadre de la certification RNCP Développeur en Intelligence Artificielle, le projet doit permettre de produire des preuves liées notamment aux compétences suivantes :

* analyse d’un besoin intégrant un service d’intelligence artificielle ;
* définition des spécifications fonctionnelles ;
* conception du cadre technique d’une application IA ;
* intégration d’un service d’intelligence artificielle ;
* développement d’une API REST ;
* collecte et mise à disposition de données ;
* connexion à différentes sources de données ;
* développement de composants applicatifs ;
* validation et tests automatisés ;
* traçabilité des traitements ;
* documentation technique et fonctionnelle ;
* industrialisation progressive d’un POC IA.

Le document de cadrage constitue une preuve de l’analyse du besoin et de la définition du cadre fonctionnel et technique.

---

# 5. Utilisateurs cibles

## 5.1 Data Engineer

Le Data Engineer utilise SmartData Generator pour :

* analyser un schéma ;
* produire des données de test ;
* alimenter une base de développement ;
* tester un pipeline ;
* générer des données compatibles avec plusieurs tables ;
* vérifier les relations et contraintes.

---

## 5.2 AI Engineer

L’AI Engineer configure :

* le fournisseur LLM ;
* les prompts ;
* les outils accessibles à l’agent ;
* le workflow LangGraph ;
* le RAG ;
* le modèle d’embeddings ;
* les règles de génération ;
* les garde-fous.

---

## 5.3 Backend Developer

Le Backend Developer utilise l’API afin de :

* créer un projet ;
* transmettre une configuration ;
* lancer une génération ;
* récupérer un aperçu ;
* exporter les données ;
* consulter les résultats de validation ;
* intégrer SmartData Generator dans une autre application.

---

## 5.4 QA ou Test Engineer

Le QA Engineer peut utiliser le service pour :

* produire des jeux de données fonctionnels ;
* couvrir différents scénarios de test ;
* générer des cas limites ;
* alimenter un environnement de recette ;
* reproduire un scénario précis ;
* vérifier le comportement de l’application avec des données invalides ou inhabituelles.

---

## 5.5 Administrateur technique

L’administrateur technique configure les projets, les connexions, les documents métier et les paramètres d’exécution.

Dans le cadre du POC, l’administration pourra être réalisée principalement par API.

Une interface utilisateur complète ne fait pas partie du périmètre prioritaire du sprint.

---

# 6. Périmètre fonctionnel

## 6.1 Gestion des projets

SmartData Generator doit permettre de créer une configuration de projet indépendante.

Un projet représente un contexte de génération et peut contenir :

* un nom ;
* une description ;
* une source ou une destination ;
* des paramètres techniques ;
* des documents métier ;
* des règles de génération ;
* des préférences de modèle ;
* un historique d’exécution.

Le projet ne doit pas contenir de code spécifique à un domaine métier.

---

## 6.2 Analyse du schéma

Le service doit être capable d’analyser un schéma cible à partir d’une source compatible.

L’analyse doit permettre d’identifier, selon les capacités du connecteur :

* les entités ou tables ;
* les colonnes ou propriétés ;
* les types de données ;
* les champs obligatoires ;
* les valeurs par défaut ;
* les clés primaires ;
* les clés étrangères ;
* les relations ;
* les contraintes d’unicité ;
* les contraintes de validation ;
* l’ordre logique de génération et d’insertion.

L’analyse du schéma est une opération technique et déterministe.

Le LLM ne doit jamais inventer le schéma cible.

---

## 6.3 Gestion de la documentation métier

L’utilisateur doit pouvoir fournir une documentation métier contenant notamment :

* des définitions ;
* des règles ;
* des contraintes ;
* des exemples ;
* des relations fonctionnelles ;
* des conventions ;
* des limites ;
* des exceptions.

La documentation doit être :

* chargée ;
* découpée ;
* enrichie avec des métadonnées ;
* vectorisée ;
* indexée ;
* recherchable par le moteur IA.

---

## 6.4 Construction d’un plan de génération

Avant de générer les données, le service doit produire un plan structuré.

Le plan doit notamment préciser :

* les entités concernées ;
* l’ordre de génération ;
* le volume demandé ;
* les dépendances ;
* les champs à produire ;
* les données de référence à réutiliser ;
* les règles métier applicables ;
* les stratégies de génération ;
* les validations prévues ;
* les éventuelles ambiguïtés.

Le plan doit être validable avant le lancement de la génération lorsque le contexte est incomplet ou sensible.

---

## 6.5 Génération des données

Le service doit produire des données structurées.

La génération doit s’appuyer sur :

* le schéma normalisé ;
* les paramètres utilisateur ;
* les règles métier récupérées ;
* les documents RAG pertinents ;
* le plan de génération ;
* les données existantes lorsque leur lecture est autorisée.

Les sorties du LLM ne doivent pas être utilisées directement sans validation.

---

## 6.6 Validation des données

Les données générées doivent être contrôlées avant tout export ou insertion.

La validation doit inclure plusieurs niveaux :

* validation du format ;
* validation des types ;
* validation des champs obligatoires ;
* validation des valeurs autorisées ;
* validation des contraintes d’unicité ;
* validation des relations ;
* validation des clés étrangères ;
* validation des règles métier ;
* validation des dépendances entre entités ;
* validation de la compatibilité avec la destination.

Les validations déterministes doivent être privilégiées.

Le LLM peut contribuer à interpréter ou expliquer une règle, mais il ne doit pas être l’unique mécanisme de validation.

---

## 6.7 Aperçu des résultats

L’utilisateur doit pouvoir consulter le résultat avant toute opération d’écriture.

L’aperçu doit présenter :

* un échantillon des données ;
* le nombre de lignes générées ;
* les entités concernées ;
* les résultats de validation ;
* les erreurs bloquantes ;
* les avertissements ;
* les règles utilisées ;
* les documents consultés ;
* les principales décisions prises par le moteur ;
* les statistiques de génération.

---

## 6.8 Export des données

Le service doit permettre d’exporter les données validées.

Les formats prévus pour le POC sont :

* JSON ;
* CSV.

L’export ne doit pas modifier la source ni la destination.

---

## 6.9 Insertion des données

Le service doit permettre l’insertion des données dans PostgreSQL.

L’insertion doit respecter les principes suivants :

* elle n’est jamais déclenchée automatiquement après la génération ;
* elle nécessite une demande explicite ;
* elle est interdite si des erreurs bloquantes sont présentes ;
* elle respecte l’ordre des dépendances ;
* elle utilise des requêtes paramétrées ;
* elle doit être transactionnelle lorsque cela est possible ;
* un échec doit entraîner un rollback ;
* elle produit un rapport détaillé.

---

## 6.10 Rapports d’exécution

Chaque génération doit produire un rapport.

Le rapport doit permettre de comprendre :

* quand l’exécution a eu lieu ;
* quel projet a été utilisé ;
* quelle configuration a été appliquée ;
* quel mode a été lancé ;
* quelles entités ont été générées ;
* quels volumes ont été produits ;
* quelles règles ont été utilisées ;
* quels documents ont été récupérés par le RAG ;
* quelles erreurs ont été détectées ;
* quelles données ont été exportées ou insérées ;
* quel est le statut final de l’exécution.

---

# 7. Cas d’usage principaux

Les cas d’usage détaillés seront formalisés dans un document dédié.

Les principaux cas identifiés à ce stade sont les suivants.

## 7.1 Générer des données pour une base vide

L’utilisateur fournit une base contenant un schéma mais aucune donnée.

SmartData Generator analyse le schéma, récupère les règles métier, construit un plan et génère les données dans l’ordre nécessaire.

---

## 7.2 Compléter une base existante

L’utilisateur souhaite ajouter de nouvelles données dans une base déjà alimentée.

Le service doit pouvoir lire les données de référence utiles et éviter les conflits avec les données existantes.

---

## 7.3 Générer un dataset de démonstration

L’utilisateur souhaite produire un dataset réaliste pour présenter une application.

Le service génère un volume cohérent, varié et suffisamment explicite pour permettre une démonstration fonctionnelle.

---

## 7.4 Générer des données de test

L’utilisateur souhaite produire des données pour tester une API, une interface ou un pipeline.

Le service peut générer :

* des cas standards ;
* des cas limites ;
* des volumes importants ;
* des combinaisons spécifiques ;
* des scénarios valides ;
* des scénarios volontairement invalides lorsque cela est explicitement demandé.

---

## 7.5 Prévisualiser avant insertion

L’utilisateur souhaite vérifier les données avant leur écriture.

Le service exécute le workflow en mode Preview et retourne les données ainsi que les résultats de validation.

---

## 7.6 Exporter un dataset synthétique

L’utilisateur souhaite récupérer un fichier JSON ou CSV sans modifier la base cible.

---

## 7.7 Insérer des données validées

Après consultation du Preview, l’utilisateur demande explicitement l’insertion.

Le service effectue une dernière validation puis insère les données dans une transaction.

---

## 7.8 Produire un rapport d’exécution

L’utilisateur souhaite conserver une preuve de la génération et de ses contrôles.

Le service produit un rapport structuré et consultable.

---

# 8. Modes de fonctionnement

## 8.1 Mode Preview

Le mode Preview est le mode par défaut.

Il permet de :

* analyser le contexte ;
* construire le plan ;
* générer les données ;
* effectuer les validations ;
* consulter un aperçu ;
* identifier les erreurs ;
* valider la cohérence générale.

Aucune donnée n’est écrite dans une destination.

Le résultat du Preview doit contenir au minimum :

* le statut de l’exécution ;
* le plan de génération ;
* les données générées ou un échantillon ;
* les résultats de validation ;
* les erreurs ;
* les avertissements ;
* les statistiques ;
* les sources documentaires utilisées.

---

## 8.2 Mode Export

Le mode Export exécute les mêmes étapes que le mode Preview, puis génère un fichier.

Le format d’export est choisi explicitement.

Les formats du POC sont :

* JSON ;
* CSV.

L’export ne doit avoir lieu que si les données respectent les validations bloquantes.

---

## 8.3 Mode Insert

Le mode Insert permet d’écrire les données dans PostgreSQL.

Il est soumis à plusieurs conditions :

* la destination est configurée ;
* la connexion est valide ;
* le schéma a été analysé ;
* les données ont été générées ;
* les données ont été validées ;
* aucune erreur bloquante n’est présente ;
* l’utilisateur a explicitement demandé l’insertion.

Le mode Insert doit produire :

* le nombre de lignes prévues ;
* le nombre de lignes insérées ;
* le nombre d’échecs ;
* les erreurs rencontrées ;
* le statut de la transaction ;
* le résultat du commit ou du rollback.

---

# 9. Limites fonctionnelles

SmartData Generator ne doit pas être considéré comme une solution universelle de génération de données.

Les limites suivantes sont définies pour le POC.

Le service :

* ne crée pas automatiquement un schéma cible ;
* ne devine pas les règles métier absentes ;
* ne garantit pas une représentation parfaite de la réalité ;
* ne remplace pas les contraintes de la base ;
* ne remplace pas les validations applicatives ;
* ne remplace pas une analyse fonctionnelle humaine ;
* ne modifie pas une base sans demande explicite ;
* n’exécute pas librement du SQL produit par le LLM ;
* ne migre pas des données entre deux systèmes ;
* n’anonymise pas automatiquement des données personnelles ;
* ne doit pas utiliser des données sensibles réelles dans les prompts ;
* ne prend pas en charge tous les types de bases ;
* ne gère pas tous les formats de fichiers ;
* ne propose pas d’interface graphique complète dans la première version ;
* ne garantit pas une performance adaptée aux très gros volumes.

---

# 10. Limites du périmètre technique

Le POC supportera initialement :

* les fichiers CSV ;
* les fichiers JSON ;
* les API REST ;
* PostgreSQL ;
* ChromaDB ;
* un fournisseur LLM configurable ;
* un fournisseur d’embeddings configurable.

Les éléments suivants sont hors périmètre initial :

* les bases NoSQL ;
* les data warehouses cloud ;
* les systèmes Big Data ;
* les fichiers Parquet ;
* les flux temps réel ;
* les connecteurs propriétaires ;
* la génération distribuée ;
* le traitement de plusieurs millions de lignes ;
* une gestion avancée des utilisateurs ;
* une interface web complète ;
* le fine-tuning d’un modèle ;
* l’entraînement d’un modèle propriétaire.

Ces fonctionnalités pourront être ajoutées dans une évolution ultérieure.

---

# 11. Responsabilités des composants

## 11.1 API REST

L’API REST constitue le point d’entrée du service.

Elle doit permettre de :

* gérer les projets ;
* enregistrer des configurations ;
* charger des documents ;
* lancer une indexation ;
* lancer une génération ;
* demander un Preview ;
* demander un Export ;
* demander un Insert ;
* récupérer un rapport ;
* consulter le statut d’une exécution.

L’API ne doit pas contenir directement la logique de génération.

---

## 11.2 Schema Analyzer

Le Schema Analyzer analyse la structure de la source ou de la destination.

Il est responsable de la production d’une représentation normalisée du schéma.

Il peut identifier :

* les entités ;
* les propriétés ;
* les types ;
* les relations ;
* les contraintes ;
* les dépendances ;
* les champs obligatoires ;
* les clés.

Le Schema Analyzer constitue la source de vérité technique concernant le schéma.

Le RAG et le LLM ne doivent pas remplacer cette analyse.

---

## 11.3 RAG

Le RAG est responsable de l’accès à la documentation métier.

Il permet de récupérer les passages pertinents en fonction :

* de l’entité ;
* de la demande ;
* du champ ;
* du cas d’usage ;
* du plan de génération.

Le corpus RAG doit contenir uniquement les informations utiles à la génération, notamment :

* les règles métier ;
* les définitions ;
* les contraintes ;
* les relations fonctionnelles ;
* les conventions ;
* les exemples ;
* les exceptions.

Le RAG ne doit pas être utilisé pour inventer ou reconstruire le schéma technique.

---

## 11.4 Agent IA

L’agent IA orchestre les différentes étapes.

Il doit être capable de :

* analyser la demande ;
* déterminer les outils nécessaires ;
* demander l’analyse du schéma ;
* interroger le RAG ;
* identifier les informations manquantes ;
* construire un plan ;
* demander une clarification ;
* lancer la génération ;
* lancer la validation ;
* préparer le résultat ;
* produire un rapport.

L’agent ne doit pas écrire directement dans la base.

Toute écriture doit passer par le service d’insertion et le connecteur concerné.

---

## 11.5 Generation Planner

Le Generation Planner produit un plan structuré.

Il détermine notamment :

* l’ordre des entités ;
* les dépendances ;
* les volumes ;
* les règles applicables ;
* les champs à générer ;
* les données existantes à réutiliser ;
* la stratégie de génération ;
* les validations à effectuer.

Le plan doit respecter un contrat de données strict.

---

## 11.6 Generation Engine

Le Generation Engine est responsable de la production des données.

Il utilise :

* le schéma ;
* le plan ;
* les paramètres ;
* les règles ;
* le contexte RAG ;
* les données existantes autorisées.

Le Generation Engine ne doit pas dépendre directement d’un connecteur concret.

---

## 11.7 Validation Engine

Le Validation Engine vérifie la conformité des données.

Il doit produire une liste structurée contenant :

* les validations effectuées ;
* les erreurs bloquantes ;
* les avertissements ;
* les champs concernés ;
* les règles concernées ;
* les suggestions de correction éventuelles.

Le moteur de validation doit privilégier des règles codées et déterministes.

---

## 11.8 Connecteurs

Les connecteurs sont responsables des échanges avec les systèmes externes.

Ils permettent de :

* tester une connexion ;
* lire les métadonnées ;
* analyser un schéma ;
* lire des données ;
* écrire des données ;
* exporter des données.

Les connecteurs ne doivent contenir :

* aucune logique métier ;
* aucun prompt ;
* aucune orchestration IA ;
* aucune règle spécifique à un projet.

---

## 11.9 Execution Reporter

Le composant Execution Reporter centralise les informations d’une exécution.

Il produit un rapport contenant :

* les métadonnées ;
* les étapes exécutées ;
* les durées ;
* les décisions ;
* les erreurs ;
* les résultats de validation ;
* les volumes ;
* le résultat de l’export ou de l’insertion.

---

# 12. Principes d’architecture

## 12.1 Architecture modulaire

Chaque responsabilité doit être isolée dans un module dédié.

Les composants doivent pouvoir évoluer indépendamment.

---

## 12.2 Séparation des responsabilités

L’architecture doit séparer :

* l’API ;
* l’orchestration ;
* le moteur IA ;
* le RAG ;
* la validation ;
* les connecteurs ;
* le stockage des projets ;
* les rapports.

---

## 12.3 Dependency Inversion

Les services métier doivent dépendre d’interfaces abstraites et non d’implémentations concrètes.

Par exemple, le moteur de génération ne doit pas dépendre directement d’un connecteur PostgreSQL.

Il doit dépendre d’une interface commune de lecture ou d’écriture.

---

## 12.4 Configuration plutôt que spécialisation

Les spécificités métier doivent être fournies par :

* des documents ;
* des règles ;
* des schémas ;
* des paramètres ;
* des configurations.

Elles ne doivent pas être codées dans le cœur de l’application.

---

## 12.5 Human Validation Before Write

La validation technique et l’autorisation d’écriture sont deux étapes distinctes.

Même si les données sont valides, leur insertion doit faire l’objet d’une demande explicite.

---

## 12.6 Structured Outputs

Les sorties critiques du LLM doivent respecter des modèles structurés.

Cela concerne notamment :

* le plan de génération ;
* les demandes de clarification ;
* les résultats de génération ;
* les erreurs ;
* les résultats de validation ;
* les rapports.

Les réponses textuelles libres doivent être limitées aux explications destinées à l’utilisateur.

---

## 12.7 Validation déterministe

Le LLM peut comprendre, expliquer ou proposer.

La validation finale doit être réalisée autant que possible par du code déterministe.

Cette séparation permet de limiter :

* les hallucinations ;
* les résultats non reproductibles ;
* les erreurs silencieuses ;
* les insertions incohérentes.

---

## 12.8 Abstraction des fournisseurs

Le fournisseur LLM doit être encapsulé derrière une interface.

Le fournisseur d’embeddings doit également être abstrait.

Cette approche doit permettre de changer de fournisseur sans modifier le cœur de SmartData Generator.

---

## 12.9 Traçabilité

Chaque exécution doit posséder un identifiant unique.

Les étapes principales doivent être enregistrées :

* début de l’exécution ;
* analyse du schéma ;
* recherche RAG ;
* création du plan ;
* génération ;
* validation ;
* export ;
* insertion ;
* fin de l’exécution.

---

# 13. Architecture logique cible

L’architecture logique cible est organisée en plusieurs couches.

```text
API Layer
    |
    v
Application Services
    |
    v
LangGraph Orchestrator
    |
    +-- Schema Analyzer
    |
    +-- RAG Retriever
    |
    +-- Generation Planner
    |
    +-- Generation Engine
    |
    +-- Validation Engine
    |
    +-- Execution Reporter
    |
    v
Connector Interfaces
    |
    +-- CSV Connector
    |
    +-- JSON Connector
    |
    +-- REST Connector
    |
    +-- PostgreSQL Connector
```

L’architecture détaillée, les composants et leurs interactions seront précisés dans le ticket d’architecture technique.

---

# 14. Plans fonctionnels de l’application

L’architecture peut être présentée à travers trois plans.

## 14.1 Control Plane

Le Control Plane gère :

* les projets ;
* les configurations ;
* les documents ;
* les connexions ;
* les demandes de génération ;
* les statuts ;
* les rapports.

---

## 14.2 Generation Plane

Le Generation Plane gère :

* l’analyse du contexte ;
* la construction du plan ;
* la récupération documentaire ;
* la génération ;
* la validation ;
* les clarifications.

---

## 14.3 Integration Plane

L’Integration Plane gère :

* la lecture des fichiers ;
* les appels REST ;
* l’analyse PostgreSQL ;
* l’export ;
* l’insertion ;
* les transactions.

---

# 15. Contraintes techniques

Le projet doit respecter les contraintes suivantes :

* le langage principal est Python ;
* l’API repose sur FastAPI ;
* les modèles de données reposent sur Pydantic ;
* l’orchestration repose sur LangGraph ;
* l’intégration LLM et RAG repose sur LangChain ;
* la base vectorielle du POC est ChromaDB ;
* PostgreSQL est utilisé comme destination relationnelle principale ;
* les dépendances sont gérées avec `uv` ;
* les tests sont développés avec `pytest` ;
* la qualité du code est vérifiée avec `Ruff` ;
* les services doivent pouvoir être exécutés avec Docker ;
* la configuration repose sur des variables d’environnement ;
* aucun secret ne doit être stocké dans le dépôt ;
* les sorties IA critiques doivent être structurées ;
* les erreurs doivent être explicitement remontées ;
* toute donnée doit être validée avant insertion ;
* les connecteurs doivent être indépendants du moteur IA ;
* les fournisseurs IA doivent être remplaçables ;
* les logs doivent être structurés ;
* les exécutions doivent être traçables.

---

# 16. Technologies retenues

## 16.1 Python

Python est retenu comme langage principal en raison de son écosystème adapté :

* à l’intelligence artificielle ;
* au traitement de données ;
* aux API ;
* à PostgreSQL ;
* à LangChain ;
* à LangGraph ;
* aux tests automatisés.

---

## 16.2 FastAPI

FastAPI est retenu pour exposer l’application sous forme d’API REST.

Ses principaux avantages sont :

* le typage Python ;
* la validation avec Pydantic ;
* la documentation OpenAPI automatique ;
* la simplicité de développement ;
* les performances ;
* la gestion des dépendances ;
* la facilité de test.

---

## 16.3 Pydantic

Pydantic est utilisé pour définir les contrats de données.

Il permet de :

* valider les entrées ;
* valider les sorties ;
* structurer les réponses du LLM ;
* détecter les erreurs de format ;
* documenter les objets échangés.

---

## 16.4 LangChain

LangChain est utilisé pour faciliter :

* l’intégration des modèles ;
* la gestion des prompts ;
* l’utilisation des outils ;
* la manipulation des documents ;
* la création du retriever ;
* l’intégration avec ChromaDB.

La logique métier principale ne doit toutefois pas dépendre excessivement de LangChain.

---

## 16.5 LangGraph

LangGraph est utilisé pour orchestrer le workflow agentique.

Il permet de représenter les étapes sous forme de graphe contrôlé :

* analyse ;
* récupération du contexte ;
* planification ;
* clarification ;
* génération ;
* validation ;
* correction ;
* finalisation.

LangGraph est retenu afin d’éviter une boucle agentique entièrement libre et difficile à tester.

---

## 16.6 ChromaDB

ChromaDB est retenu comme base vectorielle pour le POC.

Ses avantages sont :

* simplicité d’installation ;
* fonctionnement local ;
* persistance possible ;
* intégration avec LangChain ;
* utilisation adaptée à un corpus limité.

---

## 16.7 PostgreSQL

PostgreSQL est retenu pour :

* le stockage technique du service ;
* la gestion des projets ;
* l’historique des exécutions ;
* la démonstration d’analyse de schéma ;
* la démonstration d’insertion ;
* les transactions.

---

## 16.8 SQLAlchemy

SQLAlchemy est utilisé pour :

* gérer les connexions PostgreSQL ;
* inspecter les schémas ;
* exécuter des requêtes paramétrées ;
* gérer les transactions ;
* découpler l’accès aux données.

---

## 16.9 pytest

pytest est retenu pour développer :

* les tests unitaires ;
* les tests d’intégration ;
* les tests de validation ;
* les tests des connecteurs ;
* les tests du workflow LangGraph ;
* les tests de l’API.

---

## 16.10 Ruff

Ruff est utilisé pour :

* vérifier la qualité du code ;
* détecter les erreurs fréquentes ;
* appliquer les conventions ;
* formater le code.

---

## 16.11 Docker

Docker doit permettre de lancer de manière reproductible :

* l’API ;
* PostgreSQL ;
* ChromaDB si nécessaire ;
* les services annexes du POC.

---

## 16.12 uv

`uv` est retenu pour :

* la gestion des dépendances ;
* la création de l’environnement Python ;
* le verrouillage des versions ;
* l’exécution des commandes du projet.

---

# 17. Contraintes de sécurité

Le projet doit intégrer les principes suivants :

* aucune clé API dans le dépôt ;
* aucun mot de passe dans le code ;
* utilisation de variables d’environnement ;
* masquage des secrets dans les logs ;
* limitation des données envoyées au LLM ;
* absence de données personnelles réelles dans les prompts ;
* validation des chemins de fichiers ;
* validation des URLs ;
* validation des paramètres de connexion ;
* utilisation de requêtes SQL paramétrées ;
* interdiction d’exécuter librement du SQL généré par le LLM ;
* validation avant insertion ;
* insertion transactionnelle ;
* journalisation des opérations d’écriture ;
* contrôle explicite du mode Insert.

---

# 18. Gestion des données sensibles

SmartData Generator a pour objectif de produire des données synthétiques.

Il ne doit pas nécessiter l’utilisation de données personnelles réelles.

Lorsqu’une source contient des données existantes, le connecteur doit limiter la lecture aux informations strictement nécessaires à la génération.

Les données sensibles ne doivent pas être envoyées au fournisseur LLM sans mécanisme de protection adapté.

Le POC ne constitue pas un outil d’anonymisation.

L’utilisateur reste responsable des données et documents fournis au service.

---

# 19. Gestion des erreurs

Les erreurs doivent être classées au minimum en plusieurs catégories :

* erreur de configuration ;
* erreur de connexion ;
* erreur d’analyse du schéma ;
* erreur d’indexation ;
* erreur du fournisseur LLM ;
* erreur de parsing ;
* erreur de validation ;
* erreur d’export ;
* erreur d’insertion ;
* erreur de transaction ;
* erreur interne.

Chaque erreur doit contenir :

* un code ;
* un message lisible ;
* une catégorie ;
* une étape ;
* un niveau de sévérité ;
* un caractère bloquant ou non bloquant.

---

# 20. Observabilité et traçabilité

Même si le monitoring complet pourra être développé dans un sprint ultérieur, l’architecture doit être compatible avec :

* des logs structurés ;
* un identifiant de corrélation ;
* un identifiant d’exécution ;
* des métriques ;
* une mesure des durées ;
* un suivi des erreurs ;
* un suivi des appels LLM ;
* un suivi des tokens lorsque le fournisseur le permet ;
* un suivi du nombre de lignes générées ;
* un suivi du nombre d’erreurs de validation ;
* un suivi des exports et insertions.

Les données métier complètes ne doivent pas être enregistrées en clair dans les logs.

---

# 21. Livrables du projet

Les livrables prévus sont les suivants :

* document de cadrage fonctionnel et technique ;
* document d’architecture ;
* catalogue de cas d’usage ;
* dépôt Git indépendant ;
* structure FastAPI ;
* configuration LangChain ;
* workflow LangGraph ;
* configuration ChromaDB ;
* base documentaire RAG ;
* pipeline d’indexation ;
* moteur agentique ;
* moteur de validation ;
* connecteur CSV ;
* connecteur JSON ;
* connecteur REST ;
* connecteur PostgreSQL ;
* mode Preview ;
* mode Export ;
* mode Insert ;
* API REST documentée ;
* gestion des projets ;
* rapports d’exécution ;
* tests unitaires ;
* tests d’intégration ;
* validation fonctionnelle ;
* documentation d’installation ;
* documentation d’utilisation ;
* démonstration avec Pricing Control Tower ;
* cartographie des preuves RNCP.

---

# 22. Critères de réussite du POC

Le POC sera considéré comme fonctionnel lorsqu’il sera capable de :

1. créer un projet de génération ;
2. recevoir une configuration de source ou de destination ;
3. analyser un schéma réel sans inventer sa structure ;
4. charger une documentation métier ;
5. indexer cette documentation ;
6. récupérer les règles pertinentes ;
7. construire un plan structuré ;
8. demander une clarification lorsque des informations essentielles manquent ;
9. générer un dataset structuré ;
10. valider les données générées ;
11. présenter un aperçu ;
12. exporter les données en JSON ou CSV ;
13. insérer les données dans PostgreSQL après demande explicite ;
14. produire un rapport d’exécution ;
15. tracer les erreurs et les décisions ;
16. être utilisé sur au moins deux contextes fonctionnels sans modifier le cœur du moteur.

Le dernier critère permet de démontrer que SmartData Generator est réellement réutilisable et qu’il ne dépend pas uniquement de Pricing Control Tower.

---

# 23. Hypothèses retenues

Pour le POC, les hypothèses suivantes sont retenues :

* les utilisateurs sont principalement techniques ;
* les règles métier sont fournies sous forme documentaire ;
* les schémas sont accessibles par les connecteurs ;
* les volumes restent compatibles avec une exécution locale ;
* l’utilisateur valide explicitement toute insertion ;
* le fournisseur LLM est accessible par API ou localement ;
* les réponses critiques du LLM peuvent être contraintes par un schéma Pydantic ;
* les données générées sont synthétiques ;
* les documents fournis sont suffisamment précis pour permettre la génération.

---

# 24. Risques identifiés

## 24.1 Hallucination du LLM

Le LLM peut produire des valeurs ou des règles non présentes dans le contexte.

Mesures prévues :

* sorties structurées ;
* contexte RAG limité ;
* interdiction d’inventer le schéma ;
* validation déterministe ;
* rapport des sources utilisées.

---

## 24.2 Documentation métier incomplète

Le service peut manquer d’informations pour générer des données cohérentes.

Mesures prévues :

* détection des informations manquantes ;
* demande de clarification ;
* avertissements ;
* blocage de l’insertion lorsque nécessaire.

---

## 24.3 Couplage à un domaine métier

Le projet pourrait devenir dépendant de Pricing Control Tower.

Mesures prévues :

* aucune règle spécifique dans le cœur ;
* interfaces génériques ;
* configuration externe ;
* test sur un second domaine.

---

## 24.4 Génération de données techniquement invalides

Le LLM peut produire des types ou des relations incompatibles.

Mesures prévues :

* contrats Pydantic ;
* validation du schéma ;
* validation des types ;
* validation des relations ;
* validation PostgreSQL avant commit.

---

## 24.5 Insertion accidentelle

Une génération pourrait être insérée sans contrôle suffisant.

Mesures prévues :

* Preview par défaut ;
* mode Insert explicite ;
* validation obligatoire ;
* transaction ;
* rollback ;
* rapport d’insertion.

---

## 24.6 Complexité excessive du POC

Le nombre de technologies pourrait entraîner une architecture trop complexe.

Mesures prévues :

* implémentation progressive ;
* modules simples ;
* interfaces limitées ;
* priorité aux cas d’usage démontrables ;
* absence d’interface graphique complète ;
* périmètre de connecteurs limité.

---

# 25. Hors périmètre

Les éléments suivants sont explicitement hors périmètre de la première version :

* génération massive distribuée ;
* interface web complète ;
* authentification avancée ;
* gestion multi-tenant ;
* facturation ;
* marketplace de connecteurs ;
* support de toutes les bases de données ;
* anonymisation automatique ;
* entraînement d’un modèle IA ;
* fine-tuning ;
* synchronisation temps réel ;
* ingestion de flux streaming ;
* gestion avancée des droits ;
* déploiement multi-cloud ;
* production automatique sans validation humaine.

---

# 26. Validation du cadrage

Le document doit être considéré comme validé lorsque :

* les objectifs sont compris ;
* le périmètre est accepté ;
* les limites sont explicites ;
* les utilisateurs sont identifiés ;
* les principaux cas d’usage sont couverts ;
* les responsabilités des composants sont claires ;
* les technologies sont justifiées ;
* la séparation entre schéma, RAG et moteur IA est comprise ;
* la séparation entre connecteurs et moteur IA est comprise ;
* le mode Preview est défini comme mode par défaut ;
* l’insertion nécessite une action explicite ;
* aucune dépendance métier à Pricing Control Tower n’est présente ;
* les livrables sont validés.

---

# 27. Conclusion

SmartData Generator vise à démontrer qu’un service d’intelligence artificielle peut assister la génération de données métier sans remplacer les mécanismes techniques de contrôle.

Le schéma cible reste la source de vérité technique.

La documentation métier apporte le contexte fonctionnel grâce au RAG.

L’agent IA analyse la demande, sélectionne les outils et construit un plan.

Le moteur de génération produit des données structurées.

Le moteur de validation contrôle les résultats.

Les connecteurs assurent les échanges avec les systèmes externes.

Aucune insertion n’est réalisée sans validation et demande explicite.

Cette séparation des responsabilités doit permettre de construire un POC compréhensible, testable, traçable et réutilisable dans différents projets.
