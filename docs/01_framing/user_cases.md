# SmartData Generator

## Cas d’usage et scénarios fonctionnels du MVP

**Version :** 1.0
**Statut :** Draft
**Projet :** SmartData Generator
**Type de projet :** Proof of Concept industrialisable
**Contexte :** Certification RNCP Développeur en Intelligence Artificielle

---

# 1. Introduction

Ce document définit les cas d’usage couverts par le MVP de SmartData Generator.

Il précise les fonctionnalités qui seront réellement développées et démontrées dans le Proof of Concept.

SmartData Generator est un service indépendant permettant de générer des données métier synthétiques à partir :

* d’un schéma cible ;
* de règles métier ;
* d’une documentation métier ;
* de paramètres de génération ;
* de données existantes lorsque leur lecture est nécessaire et autorisée.

Le service doit pouvoir être appliqué à différents domaines fonctionnels sans modification de son cœur.

Pricing Control Tower pourra être utilisé comme démonstrateur, mais aucun cas d’usage ne doit dépendre exclusivement de ce projet.

---

# 2. Objectif du MVP

L’objectif du MVP est de démontrer qu’un service IA peut :

1. analyser une structure de données réelle ;
2. récupérer des règles métier depuis une documentation ;
3. construire un plan de génération ;
4. générer des données structurées ;
5. valider les données produites ;
6. présenter les résultats avant écriture ;
7. exporter les données ;
8. insérer les données dans une base PostgreSQL après confirmation explicite ;
9. produire un rapport d’exécution.

Le MVP ne cherche pas à prendre en charge tous les systèmes de données existants.

Il doit avant tout démontrer :

* la cohérence de l’architecture ;
* la séparation des responsabilités ;
* la réutilisabilité ;
* la fiabilité des validations ;
* la sécurité des opérations d’écriture ;
* la traçabilité.

---

# 3. Acteurs concernés

## 3.1 Utilisateur technique

L’utilisateur technique configure le projet et lance les opérations.

Il peut être :

* Data Engineer ;
* Backend Developer ;
* AI Engineer ;
* QA Engineer ;
* administrateur technique.

Il doit pouvoir :

* déclarer une source ;
* déclarer une destination ;
* fournir des documents métier ;
* demander une analyse du schéma ;
* configurer une génération ;
* lancer un Preview ;
* demander un Export ;
* confirmer un Insert ;
* consulter un rapport.

---

## 3.2 Application cliente

Une application cliente peut utiliser l’API REST de SmartData Generator.

Elle peut :

* transmettre les configurations ;
* déclencher les opérations ;
* récupérer le statut d’une exécution ;
* récupérer un résultat ;
* télécharger ou référencer un export ;
* demander une insertion.

---

## 3.3 Fournisseur LLM

Le fournisseur LLM assiste :

* l’interprétation de la demande ;
* la construction du plan ;
* l’identification des informations manquantes ;
* la génération de certains contenus ;
* l’explication des résultats.

Il ne constitue pas un acteur autorisé à déclencher une insertion.

---

# 4. Sources de données supportées

Le MVP supporte quatre types de sources.

---

## 4.1 Source CSV

SmartData Generator doit pouvoir lire un fichier CSV fourni par l’utilisateur.

Le connecteur CSV doit permettre de :

* vérifier que le fichier existe ;
* lire les colonnes ;
* lire les lignes ;
* prendre en compte un séparateur configuré ;
* prendre en compte un encodage configuré ;
* analyser les valeurs présentes ;
* produire une représentation technique des données ;
* signaler les erreurs de lecture.

Lorsque certaines informations ne peuvent pas être déduites avec certitude, elles doivent être fournies par configuration.

Le service ne doit pas inventer :

* le séparateur ;
* l’encodage ;
* la signification métier des colonnes ;
* les relations avec d’autres fichiers ;
* les règles de validation.

---

## 4.2 Source JSON

SmartData Generator doit pouvoir lire un fichier JSON fourni par l’utilisateur.

Le connecteur JSON doit permettre de :

* vérifier la syntaxe ;
* lire les propriétés ;
* analyser la structure ;
* lire les valeurs ;
* détecter les champs présents ;
* signaler les structures incohérentes ;
* produire une représentation normalisée.

Le MVP cible principalement :

* les objets simples ;
* les listes d’objets homogènes ;
* les structures imbriquées de complexité limitée.

Les structures très profondes ou fortement variables sont hors périmètre initial.

---

## 4.3 Source REST

SmartData Generator doit pouvoir lire des données depuis une API REST générique.

Le connecteur REST doit utiliser une configuration explicitement fournie.

Cette configuration devra préciser, selon le besoin :

* l’URL ;
* la méthode HTTP ;
* les en-têtes ;
* les paramètres ;
* le mécanisme d’authentification ;
* la pagination ;
* le chemin d’accès aux données dans la réponse ;
* les limites de lecture.

Le service ne doit supposer :

* aucun endpoint ;
* aucune méthode ;
* aucun format de réponse ;
* aucune pagination ;
* aucune authentification.

Pour le MVP, le connecteur REST est uniquement utilisé en lecture.

L’écriture vers une API distante est hors périmètre.

---

## 4.4 Source PostgreSQL

SmartData Generator doit pouvoir se connecter à une base PostgreSQL.

Le connecteur PostgreSQL doit permettre de :

* tester la connexion ;
* inspecter les schémas autorisés ;
* identifier les tables ;
* identifier les colonnes ;
* identifier les types ;
* identifier les contraintes ;
* identifier les clés primaires ;
* identifier les clés étrangères ;
* identifier les relations ;
* lire des données existantes lorsque cela est autorisé ;
* préparer l’ordre logique de génération.

PostgreSQL constitue la source la plus complète pour démontrer l’analyse automatique d’un schéma relationnel.

---

# 5. Destinations supportées

Le MVP supporte trois destinations principales.

---

## 5.1 Réponse Preview

La première destination est la réponse de prévisualisation.

Elle contient :

* les métadonnées de l’exécution ;
* le plan de génération ;
* un échantillon ou l’ensemble des données selon le volume ;
* les résultats de validation ;
* les erreurs ;
* les avertissements ;
* les règles utilisées ;
* les sources documentaires ;
* les statistiques de génération.

Aucune écriture externe n’est réalisée.

---

## 5.2 Fichier CSV ou JSON

Le service doit pouvoir exporter les données validées.

Formats supportés :

* CSV ;
* JSON.

L’export doit être réalisé uniquement après les contrôles de validation prévus.

---

## 5.3 Base PostgreSQL

Le service doit pouvoir insérer des données validées dans une base PostgreSQL.

L’insertion doit respecter :

* une demande explicite ;
* une validation préalable ;
* un ordre d’insertion cohérent ;
* les contraintes relationnelles ;
* l’utilisation de requêtes paramétrées ;
* une transaction ;
* un rollback en cas d’échec ;
* un rapport final.

---

# 6. Cas d’usage principaux

# UC-01 — Créer un projet de génération

## Acteur principal

Utilisateur technique.

## Objectif

Créer un contexte indépendant regroupant les configurations, documents et exécutions.

## Préconditions

Aucune.

## Scénario nominal

1. L’utilisateur fournit un nom de projet.
2. Il fournit éventuellement une description.
3. Le service valide les données.
4. Le projet est créé.
5. Un identifiant unique est retourné.

## Résultat attendu

Le projet peut recevoir :

* une configuration de source ;
* une configuration de destination ;
* des documents ;
* des paramètres de génération ;
* des exécutions.

## Erreurs possibles

* nom absent ;
* configuration invalide ;
* doublon selon la règle d’unicité retenue ;
* erreur de stockage interne.

---

# UC-02 — Enregistrer une source de données

## Acteur principal

Utilisateur technique.

## Objectif

Associer une source CSV, JSON, REST ou PostgreSQL à un projet.

## Préconditions

Le projet existe.

## Scénario nominal

1. L’utilisateur choisit un type de source.
2. Il transmet la configuration nécessaire.
3. Le service vérifie la structure de la configuration.
4. Le connecteur compatible est sélectionné.
5. La configuration est enregistrée.

## Résultat attendu

La source peut être testée et analysée.

## Erreurs possibles

* type de connecteur inconnu ;
* configuration incomplète ;
* fichier introuvable ;
* URL invalide ;
* paramètres de connexion manquants ;
* secret absent ;
* projet inexistant.

---

# UC-03 — Tester une source

## Acteur principal

Utilisateur technique.

## Objectif

Vérifier qu’une source peut être utilisée.

## Préconditions

Une source est configurée.

## Scénario nominal

1. L’utilisateur demande un test.
2. Le Connector Registry sélectionne le connecteur.
3. Le connecteur tente une opération minimale.
4. Le résultat est retourné.
5. Le statut est enregistré.

## Résultat attendu

Le service indique si la source est accessible.

## Erreurs possibles

* fichier inaccessible ;
* API indisponible ;
* erreur HTTP ;
* authentification refusée ;
* connexion PostgreSQL impossible ;
* délai dépassé ;
* format non valide.

---

# UC-04 — Analyser un schéma

## Acteur principal

Utilisateur technique.

## Objectif

Obtenir une représentation technique normalisée de la source ou de la destination.

## Préconditions

La source existe et est accessible.

## Scénario nominal

1. L’utilisateur demande une analyse.
2. Le connecteur extrait les métadonnées disponibles.
3. Le Schema Analyzer normalise ces informations.
4. Les entités, champs et relations sont identifiés.
5. Le résultat est enregistré.
6. Un résumé est retourné.

## Résultat attendu

Un schéma normalisé est disponible pour le plan de génération.

## Erreurs possibles

* source inaccessible ;
* schéma vide ;
* structure JSON incohérente ;
* CSV sans en-têtes ;
* métadonnées insuffisantes ;
* relations non déterminables ;
* type non supporté.

## Règle importante

Le LLM ne doit jamais compléter arbitrairement un schéma incomplet.

Lorsque des informations sont absentes, le service doit demander une configuration ou une clarification.

---

# UC-05 — Charger un document métier

## Acteur principal

Utilisateur technique.

## Objectif

Associer une documentation métier à un projet.

## Préconditions

Le projet existe.

## Scénario nominal

1. L’utilisateur fournit un document supporté.
2. Le format et la taille sont validés.
3. Le document est enregistré.
4. Ses métadonnées sont conservées.
5. Son statut initial est défini.

## Résultat attendu

Le document est disponible pour indexation.

## Erreurs possibles

* fichier absent ;
* format non supporté ;
* fichier vide ;
* fichier trop volumineux ;
* contenu illisible ;
* document déjà enregistré ;
* projet inexistant.

---

# UC-06 — Indexer la documentation métier

## Acteur principal

Utilisateur technique.

## Objectif

Rendre la documentation interrogeable par le RAG.

## Préconditions

Un document valide est associé au projet.

## Scénario nominal

1. L’utilisateur déclenche l’indexation.
2. Le texte est extrait.
3. Le document est découpé.
4. Les métadonnées sont ajoutées.
5. Les embeddings sont générés.
6. Les chunks sont enregistrés dans ChromaDB.
7. Le statut d’indexation est mis à jour.

## Résultat attendu

Les règles et informations métier peuvent être retrouvées par recherche vectorielle.

## Erreurs possibles

* extraction impossible ;
* document vide ;
* erreur d’embeddings ;
* modèle indisponible ;
* ChromaDB indisponible ;
* métadonnées invalides ;
* indexation partielle.

---

# UC-07 — Définir une demande de génération

## Acteur principal

Utilisateur technique.

## Objectif

Décrire les données à générer.

## Préconditions

Le projet existe.

## Informations attendues

Selon le cas, la demande peut contenir :

* les entités concernées ;
* le volume ;
* le mode ;
* les contraintes supplémentaires ;
* les scénarios à favoriser ;
* la réutilisation ou non de données existantes ;
* une graine de génération ;
* des limites de taille.

La structure exacte sera définie lors de la conception de l’API.

## Erreurs possibles

* volume absent ;
* volume invalide ;
* entité inconnue ;
* mode inconnu ;
* configuration contradictoire ;
* schéma non analysé.

---

# UC-08 — Construire un plan de génération

## Acteur principal

LangGraph Orchestrator.

## Objectif

Construire un plan structuré avant la production des données.

## Préconditions

* projet valide ;
* schéma disponible ;
* demande de génération valide ;
* documentation indexée lorsque des règles métier sont nécessaires.

## Scénario nominal

1. Le workflow charge le schéma.
2. Il identifie les entités demandées.
3. Le RAG récupère les règles pertinentes.
4. Le contexte est construit.
5. Le LLM propose un plan structuré.
6. Pydantic valide le plan.
7. Les dépendances et volumes sont contrôlés.
8. Le plan est enregistré.

## Résultat attendu

Le plan précise :

* les entités ;
* l’ordre ;
* les volumes ;
* les dépendances ;
* les stratégies ;
* les règles ;
* les validations prévues.

## Erreurs possibles

* aucune règle pertinente trouvée ;
* contradiction entre règles ;
* sortie LLM invalide ;
* entité absente du schéma ;
* relation non résolue ;
* information essentielle manquante.

---

# UC-09 — Demander une clarification

## Acteur principal

LangGraph Orchestrator.

## Objectif

Suspendre le workflow lorsqu’une information indispensable manque.

## Préconditions

Le plan ne peut pas être construit de manière fiable.

## Scénario nominal

1. Une ambiguïté bloquante est détectée.
2. Une demande structurée est produite.
3. L’exécution passe au statut `WAITING_FOR_INPUT`.
4. L’utilisateur fournit la réponse.
5. Le workflow reprend.

## Exemples d’ambiguïtés

* volume non défini ;
* relation non déterminable ;
* règle contradictoire ;
* destination non choisie ;
* champ obligatoire sans stratégie ;
* type impossible à déduire.

## Résultat attendu

Le workflow ne poursuit pas en inventant l’information manquante.

---

# UC-10 — Générer des données

## Acteur principal

Generation Engine.

## Objectif

Produire un dataset conforme au plan.

## Préconditions

Le plan est valide.

## Scénario nominal

1. Les entités sont ordonnées.
2. Les données de référence sont chargées.
3. Les identifiants nécessaires sont préparés.
4. Les lignes sont générées.
5. Les relations sont conservées.
6. Les règles configurées sont appliquées.
7. Le dataset structuré est transmis à la validation.

## Stratégies autorisées

* génération déterministe ;
* valeurs aléatoires contrôlées ;
* bibliothèques de données synthétiques ;
* données de référence ;
* valeurs calculées ;
* génération assistée par LLM.

## Résultat attendu

Les données sont structurées conformément au schéma normalisé.

---

# UC-11 — Valider les données générées

## Acteur principal

Validation Engine.

## Objectif

Détecter les incohérences avant export ou insertion.

## Préconditions

Un dataset a été généré.

## Scénario nominal

1. Les modèles structurés sont validés.
2. Les types sont contrôlés.
3. Les champs obligatoires sont contrôlés.
4. Les contraintes sont contrôlées.
5. Les relations sont contrôlées.
6. Les règles métier sont appliquées.
7. Les conflits avec les données existantes sont recherchés lorsque nécessaire.
8. Un rapport est produit.

## Résultat attendu

Chaque problème est classé comme :

* erreur bloquante ;
* erreur non bloquante ;
* avertissement ;
* information.

---

# UC-12 — Prévisualiser une génération

## Acteur principal

Utilisateur technique.

## Objectif

Consulter les données avant toute écriture.

## Préconditions

Une génération a été exécutée.

## Scénario nominal

1. Le service prépare le Preview.
2. Il inclut les données ou un échantillon.
3. Il ajoute les résultats de validation.
4. Il ajoute les règles utilisées.
5. Il ajoute les statistiques.
6. Le résultat est retourné.

## Résultat attendu

L’utilisateur peut vérifier le résultat sans modifier une destination.

---

# UC-13 — Exporter en JSON

## Acteur principal

Utilisateur technique.

## Objectif

Exporter un dataset validé dans un fichier JSON.

## Préconditions

* génération terminée ;
* absence d’erreur bloquante ;
* format JSON demandé.

## Scénario nominal

1. L’utilisateur demande l’export.
2. Le statut de validation est vérifié.
3. Les données sont sérialisées.
4. Le fichier est produit.
5. Les métadonnées sont enregistrées.
6. La référence du fichier est retournée.

## Erreurs possibles

* validation bloquante ;
* erreur de sérialisation ;
* stockage indisponible ;
* fichier impossible à créer.

---

# UC-14 — Exporter en CSV

## Acteur principal

Utilisateur technique.

## Objectif

Exporter un dataset validé dans un ou plusieurs fichiers CSV.

## Préconditions

* génération terminée ;
* absence d’erreur bloquante ;
* format CSV demandé.

## Scénario nominal

1. L’utilisateur demande l’export.
2. Les données sont organisées par structure compatible.
3. Le séparateur et l’encodage configurés sont appliqués.
4. Les fichiers sont créés.
5. Les métadonnées sont enregistrées.
6. Les références sont retournées.

## Erreurs possibles

* structure non compatible avec un CSV simple ;
* validation bloquante ;
* encodage invalide ;
* erreur d’écriture ;
* stockage indisponible.

---

# UC-15 — Insérer dans PostgreSQL

## Acteur principal

Utilisateur technique.

## Objectif

Insérer un dataset validé dans une base PostgreSQL.

## Préconditions

* destination PostgreSQL configurée ;
* connexion valide ;
* schéma analysé ;
* génération terminée ;
* absence d’erreur bloquante ;
* demande explicite d’insertion.

## Scénario nominal

1. L’utilisateur confirme l’insertion.
2. Le service vérifie l’état de l’exécution.
3. Le connecteur est sélectionné.
4. L’ordre d’insertion est calculé.
5. Une transaction est ouverte.
6. Les données sont insérées.
7. Les résultats sont contrôlés.
8. La transaction est validée.
9. Le rapport est mis à jour.

## Scénario d’échec

1. Une erreur survient pendant l’insertion.
2. Le processus est interrompu.
3. Un rollback est exécuté.
4. L’erreur est enregistrée.
5. Le statut final est défini à `FAILED`.
6. Aucune insertion partielle ne doit être conservée lorsque la transaction couvre l’opération.

---

# UC-16 — Consulter un rapport d’exécution

## Acteur principal

Utilisateur technique ou application cliente.

## Objectif

Comprendre le résultat d’une génération.

## Préconditions

Une exécution existe.

## Contenu attendu

Le rapport doit inclure :

* l’identifiant d’exécution ;
* le projet ;
* le mode ;
* la configuration utilisée ;
* le schéma utilisé ;
* les règles récupérées ;
* les documents utilisés ;
* le plan ;
* les volumes ;
* les résultats de validation ;
* les erreurs ;
* les avertissements ;
* les durées ;
* les exports ;
* le résultat d’insertion ;
* le statut final.

---

# 7. Scénarios Preview du MVP

# PREVIEW-01 — Génération depuis un schéma PostgreSQL vide

## But

Démontrer la capacité à analyser un schéma relationnel et à produire des données cohérentes sans insertion.

## Entrées

* connexion PostgreSQL ;
* schéma existant ;
* documentation métier ;
* volume demandé.

## Étapes

1. tester la connexion ;
2. analyser le schéma ;
3. identifier les relations ;
4. indexer les règles ;
5. construire le plan ;
6. générer les données ;
7. valider le dataset ;
8. retourner le Preview.

## Résultat attendu

Le Preview contient plusieurs entités cohérentes et reliées.

---

# PREVIEW-02 — Génération à partir d’une structure CSV

## But

Démontrer la prise en charge d’une source fichier simple.

## Entrées

* fichier CSV ;
* configuration du format ;
* règles métier ;
* volume demandé.

## Étapes

1. lire le fichier ;
2. identifier les colonnes ;
3. construire une représentation du schéma ;
4. récupérer les règles ;
5. générer de nouvelles lignes ;
6. valider les types et contraintes ;
7. retourner le Preview.

## Limite

Les relations avec d’autres fichiers doivent être explicitement configurées.

---

# PREVIEW-03 — Génération à partir d’une structure JSON

## But

Démontrer la prise en charge d’un format structuré.

## Entrées

* fichier JSON ;
* documentation métier ;
* paramètres de génération.

## Étapes

1. valider le JSON ;
2. analyser la structure ;
3. identifier les propriétés ;
4. construire le plan ;
5. générer les objets ;
6. valider les résultats ;
7. retourner le Preview.

---

# PREVIEW-04 — Compléter une base existante

## But

Démontrer la génération tenant compte de données déjà présentes.

## Entrées

* base PostgreSQL existante ;
* lecture autorisée de certaines données ;
* règles métier ;
* volume complémentaire.

## Étapes

1. analyser le schéma ;
2. lire les références autorisées ;
3. identifier les valeurs existantes ;
4. éviter les conflits d’unicité ;
5. générer les nouvelles lignes ;
6. vérifier les relations ;
7. retourner le Preview.

---

# PREVIEW-05 — Blocage pour information manquante

## But

Démontrer que le service ne suppose pas une information critique.

## Entrées

* schéma incomplet ou ambigu ;
* règle essentielle absente.

## Étapes

1. analyser le contexte ;
2. détecter l’ambiguïté ;
3. produire une demande de clarification ;
4. suspendre l’exécution ;
5. reprendre après réponse.

## Résultat attendu

Aucune génération arbitraire n’est réalisée.

---

# PREVIEW-06 — Détection de données invalides

## But

Démontrer le rôle du Validation Engine.

## Entrées

* données générées contenant une violation ;
* règle ou contrainte correspondante.

## Étapes

1. générer les données ;
2. appliquer les validations ;
3. détecter la violation ;
4. classer le problème ;
5. afficher l’erreur dans le Preview ;
6. bloquer Export et Insert si l’erreur est bloquante.

---

# 8. Scénarios Export du MVP

# EXPORT-01 — Export JSON valide

## Préconditions

* Preview terminé ;
* aucune erreur bloquante.

## Résultat attendu

Un fichier JSON conforme au dataset validé est créé.

---

# EXPORT-02 — Export CSV valide

## Préconditions

* Preview terminé ;
* structure compatible ;
* aucune erreur bloquante.

## Résultat attendu

Un ou plusieurs fichiers CSV sont produits.

---

# EXPORT-03 — Export bloqué

## Préconditions

Une erreur bloquante est présente.

## Résultat attendu

* aucun fichier final n’est produit ;
* une erreur explicite est retournée ;
* le rapport indique la cause du blocage.

---

# EXPORT-04 — Erreur d’écriture

## Situation

Le stockage d’export est indisponible ou non accessible.

## Résultat attendu

* l’export échoue proprement ;
* les données générées restent disponibles dans l’exécution ;
* l’erreur est tracée ;
* aucune insertion n’est déclenchée.

---

# 9. Scénarios Insert du MVP

# INSERT-01 — Insertion réussie dans PostgreSQL

## Préconditions

* Preview validé ;
* confirmation explicite ;
* destination accessible ;
* schéma compatible.

## Résultat attendu

* transaction validée ;
* lignes insérées ;
* rapport d’insertion disponible ;
* statut `INSERTED`.

---

# INSERT-02 — Insertion refusée sans confirmation

## Situation

Une demande d’insertion n’est pas explicitement confirmée.

## Résultat attendu

* aucune écriture ;
* statut inchangé ;
* message explicite.

---

# INSERT-03 — Insertion bloquée par validation

## Situation

Le rapport contient une erreur bloquante.

## Résultat attendu

* aucune transaction ouverte ;
* aucune écriture ;
* erreur retournée ;
* violations listées.

---

# INSERT-04 — Rollback sur erreur relationnelle

## Situation

Une contrainte relationnelle échoue pendant l’insertion.

## Résultat attendu

* transaction annulée ;
* aucune donnée partielle conservée ;
* erreur enregistrée ;
* rapport détaillé ;
* statut `FAILED`.

---

# INSERT-05 — Conflit avec des données existantes

## Situation

Une clé ou une valeur unique existe déjà.

## Résultat attendu

* conflit détecté avant l’insertion lorsque possible ;
* insertion bloquée ;
* lignes concernées identifiées ;
* aucune modification de la base.

---

# INSERT-06 — Connexion perdue pendant l’opération

## Situation

La connexion devient indisponible.

## Résultat attendu

* tentative interrompue ;
* rollback lorsque possible ;
* erreur technique enregistrée ;
* statut final cohérent ;
* aucune relance automatique non contrôlée.

---

# 10. Règles métier prises en charge

SmartData Generator ne contient aucune règle métier fixe propre à un domaine.

Les règles sont fournies par le projet.

Le MVP doit toutefois prendre en charge plusieurs catégories génériques.

---

## 10.1 Champs obligatoires

Exemple générique :

* une propriété doit toujours être renseignée ;
* une valeur vide est interdite.

---

## 10.2 Domaines de valeurs

Exemple générique :

* un statut doit appartenir à une liste autorisée ;
* une catégorie doit correspondre à une référence.

---

## 10.3 Bornes numériques

Exemple générique :

* une quantité doit être positive ;
* un pourcentage doit respecter une plage définie ;
* une valeur maximale ne doit pas être dépassée.

---

## 10.4 Règles de dates

Exemple générique :

* une date de fin doit être postérieure à une date de début ;
* une date ne doit pas être dans le passé ;
* deux périodes ne doivent pas se chevaucher.

---

## 10.5 Règles conditionnelles

Exemple générique :

* si un statut possède une valeur donnée, un autre champ devient obligatoire ;
* un champ ne peut être présent que dans un certain contexte.

---

## 10.6 Règles d’unicité

Exemple générique :

* un identifiant doit être unique ;
* une combinaison de plusieurs champs doit être unique.

---

## 10.7 Règles relationnelles

Exemple générique :

* une référence doit pointer vers une entité existante ;
* un enfant doit être lié à un parent valide ;
* certaines entités doivent être générées avant d’autres.

---

## 10.8 Règles de cohérence entre entités

Exemple générique :

* deux valeurs liées doivent appartenir au même périmètre ;
* une relation n’est autorisée que lorsque certaines propriétés correspondent.

---

## 10.9 Règles de distribution

Exemple générique :

* répartir les données entre plusieurs catégories ;
* limiter la proportion d’une valeur ;
* favoriser certains scénarios.

Ces règles servent à rendre le dataset plus réaliste, mais ne remplacent pas les contraintes bloquantes.

---

## 10.10 Exceptions métier

Une règle peut inclure :

* des exceptions ;
* des cas particuliers ;
* un niveau de sévérité ;
* une période d’application ;
* une source documentaire.

Les exceptions doivent être explicitement fournies.

---

# 11. Format attendu des règles métier

Le format technique définitif sera conçu dans les tickets d’implémentation.

Toutefois, une règle exploitable devra pouvoir préciser au minimum :

* un identifiant ;
* un nom ;
* une description ;
* l’entité concernée ;
* les champs concernés ;
* la condition ;
* la contrainte attendue ;
* la sévérité ;
* le caractère bloquant ;
* la source documentaire.

Les règles uniquement exprimées en texte libre pourront être interprétées par le LLM, mais les validations critiques devront être converties en règles structurées et déterministes.

---

# 12. Contraintes de validation

Le MVP applique plusieurs niveaux de validation.

---

## 12.1 Validation des entrées

Le service vérifie :

* les paramètres obligatoires ;
* les types ;
* les formats ;
* le volume ;
* le mode ;
* les identifiants ;
* les configurations.

---

## 12.2 Validation du schéma

Le service vérifie :

* l’existence d’au moins une entité ;
* la présence des champs nécessaires ;
* les types identifiables ;
* la cohérence des relations ;
* les dépendances ;
* la possibilité de définir un ordre.

---

## 12.3 Validation du plan

Le service vérifie :

* la conformité du plan au modèle Pydantic ;
* l’existence des entités ;
* la cohérence des volumes ;
* la cohérence de l’ordre ;
* la présence des stratégies nécessaires ;
* les validations proposées.

---

## 12.4 Validation des données

Le service vérifie :

* les types ;
* les valeurs nulles ;
* les formats ;
* les longueurs ;
* les listes de valeurs ;
* les bornes ;
* les clés ;
* les relations ;
* les doublons ;
* les règles métier.

---

## 12.5 Validation avant export

Le service vérifie :

* l’absence d’erreur bloquante ;
* la compatibilité avec le format ;
* la capacité de sérialisation ;
* la présence des données.

---

## 12.6 Validation avant insertion

Le service vérifie :

* la confirmation explicite ;
* l’état de l’exécution ;
* la connexion ;
* le schéma ;
* les contraintes ;
* les conflits ;
* les relations ;
* l’ordre d’écriture ;
* la capacité transactionnelle.

---

# 13. Classification des résultats de validation

## 13.1 Erreur bloquante

Empêche l’export et l’insertion.

Exemples :

* type incompatible ;
* champ obligatoire absent ;
* clé étrangère invalide ;
* règle métier critique violée ;
* contradiction majeure ;
* schéma incompatible.

---

## 13.2 Erreur non bloquante

Le dataset reste consultable, mais une correction est recommandée.

Son autorisation pour l’export sera définie selon la politique du projet.

---

## 13.3 Avertissement

Signale un risque ou une qualité insuffisante.

Exemples :

* distribution peu réaliste ;
* documentation partielle ;
* faible confiance dans une règle interprétée ;
* valeur inhabituelle mais valide.

---

## 13.4 Information

Donne du contexte sans indiquer un problème.

Exemples :

* nombre de lignes générées ;
* règle appliquée ;
* document utilisé ;
* valeur par défaut choisie selon une configuration explicite.

---

# 14. Erreurs à gérer

# 14.1 Erreurs de projet

* projet inexistant ;
* projet inactif ;
* configuration manquante ;
* configuration incompatible ;
* ressource associée à un autre projet.

---

# 14.2 Erreurs de fichier

* fichier absent ;
* fichier vide ;
* fichier trop volumineux ;
* encodage invalide ;
* CSV sans en-têtes ;
* JSON invalide ;
* format non supporté ;
* accès refusé.

---

# 14.3 Erreurs REST

* URL invalide ;
* authentification absente ;
* authentification refusée ;
* erreur HTTP ;
* pagination invalide ;
* structure inattendue ;
* réponse vide ;
* délai dépassé ;
* API indisponible.

---

# 14.4 Erreurs PostgreSQL

* paramètres manquants ;
* authentification refusée ;
* hôte inaccessible ;
* base inexistante ;
* schéma inaccessible ;
* permission insuffisante ;
* table inexistante ;
* transaction échouée ;
* contrainte violée ;
* connexion interrompue.

---

# 14.5 Erreurs RAG

* document non indexé ;
* collection inexistante ;
* ChromaDB indisponible ;
* embeddings indisponibles ;
* aucun résultat pertinent ;
* résultat du mauvais projet ;
* métadonnées invalides ;
* indexation partielle.

---

# 14.6 Erreurs LLM

* fournisseur indisponible ;
* clé invalide ;
* limite de taux ;
* délai dépassé ;
* réponse vide ;
* sortie non structurée ;
* parsing impossible ;
* plan incompatible avec le schéma ;
* résultat non conforme après plusieurs tentatives.

---

# 14.7 Erreurs de génération

* stratégie inconnue ;
* champ sans stratégie ;
* dépendance circulaire ;
* volume impossible ;
* référence absente ;
* relation non résolue ;
* génération interrompue ;
* résultat incomplet.

---

# 14.8 Erreurs de validation

* type invalide ;
* champ obligatoire absent ;
* valeur hors domaine ;
* doublon ;
* clé invalide ;
* relation inexistante ;
* règle métier violée ;
* conflit avec une donnée existante.

---

# 14.9 Erreurs d’export

* format inconnu ;
* structure incompatible ;
* erreur de sérialisation ;
* espace indisponible ;
* chemin interdit ;
* écriture impossible ;
* validation bloquante.

---

# 14.10 Erreurs d’insertion

* confirmation absente ;
* validation bloquante ;
* destination inaccessible ;
* permission insuffisante ;
* conflit d’unicité ;
* clé étrangère invalide ;
* transaction impossible ;
* rollback échoué ;
* insertion partielle détectée.

---

# 15. Rapports attendus

Chaque scénario doit produire une trace exploitable.

Le rapport doit contenir :

* l’identifiant du projet ;
* l’identifiant d’exécution ;
* le type de source ;
* le type de destination ;
* le mode ;
* le statut ;
* le schéma utilisé ;
* les entités générées ;
* les volumes demandés ;
* les volumes obtenus ;
* les règles utilisées ;
* les documents utilisés ;
* les erreurs ;
* les avertissements ;
* les résultats de validation ;
* les durées ;
* les exports ;
* le résultat d’insertion.

---

# 16. Scénarios de démonstration retenus

Le MVP devra être démontré avec au minimum les scénarios suivants.

## Démonstration 1 — Preview PostgreSQL

* analyser un schéma PostgreSQL ;
* charger une documentation métier ;
* générer plusieurs entités reliées ;
* valider les données ;
* afficher le Preview.

## Démonstration 2 — Export

* reprendre une exécution validée ;
* exporter les données en JSON ou CSV ;
* consulter le rapport.

## Démonstration 3 — Insert

* confirmer explicitement l’insertion ;
* insérer dans PostgreSQL ;
* vérifier les lignes ;
* consulter le rapport transactionnel.

## Démonstration 4 — Erreur de validation

* générer ou injecter un scénario incohérent ;
* détecter une violation ;
* bloquer l’insertion ;
* afficher le détail.

## Démonstration 5 — Rollback

* provoquer une erreur pendant l’insertion ;
* exécuter un rollback ;
* démontrer l’absence de données partielles.

## Démonstration 6 — Réutilisabilité

* utiliser un second domaine fonctionnel ;
* conserver le même moteur ;
* remplacer uniquement le schéma, la documentation et la configuration ;
* produire un nouveau Preview.

Cette dernière démonstration est indispensable pour prouver l’indépendance vis-à-vis de Pricing Control Tower.

---

# 17. Limites du MVP

Le MVP ne prend pas en charge :

* les bases NoSQL ;
* les data warehouses cloud ;
* les systèmes Big Data ;
* les flux temps réel ;
* les messages Kafka ;
* les fichiers Parquet ;
* les tableurs complexes ;
* les bases propriétaires ;
* l’écriture vers une API REST ;
* la génération distribuée ;
* plusieurs millions de lignes ;
* les transformations complexes de migration ;
* la synchronisation entre systèmes ;
* l’anonymisation de données réelles ;
* le fine-tuning ;
* l’entraînement d’un modèle ;
* une interface graphique complète ;
* une authentification avancée ;
* le multi-tenant ;
* une gestion fine des rôles ;
* le déploiement multi-cloud.

---

# 18. Limites fonctionnelles

Le service ne peut pas garantir :

* la qualité d’une documentation métier incomplète ;
* la validité d’une règle absente ;
* la fidélité statistique parfaite à une population réelle ;
* la compréhension automatique de toute structure ;
* la détection de toutes les relations implicites ;
* l’absence totale d’hallucination du LLM ;
* la génération d’un dataset exploitable sans validation.

Le service ne doit jamais :

* inventer un schéma ;
* inventer une API ;
* inventer un format ;
* inventer une relation bloquante ;
* exécuter du SQL libre produit par le LLM ;
* écrire sans autorisation ;
* ignorer une erreur bloquante ;
* masquer un conflit entre le schéma et la documentation.

---

# 19. Critères de réussite du MVP

Le MVP est considéré comme réussi lorsqu’il permet de :

1. créer un projet ;
2. enregistrer une source ;
3. analyser un schéma ;
4. charger et indexer une documentation ;
5. construire un plan structuré ;
6. demander une clarification ;
7. générer plusieurs entités cohérentes ;
8. valider les données ;
9. afficher un Preview ;
10. exporter en JSON ou CSV ;
11. insérer dans PostgreSQL ;
12. effectuer un rollback ;
13. produire un rapport ;
14. signaler les erreurs ;
15. fonctionner sur deux domaines sans modification du cœur.

---

# 20. Décisions fonctionnelles retenues

Les décisions suivantes sont validées pour le MVP :

* CSV, JSON, REST et PostgreSQL sont supportés en lecture ;
* REST n’est pas supporté en écriture ;
* CSV et JSON sont supportés en export ;
* PostgreSQL est la seule destination d’insertion ;
* Preview est le mode par défaut ;
* Export nécessite une validation suffisante ;
* Insert nécessite une validation complète et une confirmation explicite ;
* les règles métier sont fournies par configuration et documentation ;
* les validations critiques sont déterministes ;
* le LLM ne décide pas seul d’une insertion ;
* le RAG ne remplace pas le Schema Analyzer ;
* les erreurs bloquantes empêchent l’écriture ;
* toutes les exécutions produisent un rapport ;
* le MVP doit être démontré sur deux domaines distincts.

---

# 21. Validation du document

Le document est considéré comme validé lorsque :

* les sources du MVP sont confirmées ;
* les destinations sont confirmées ;
* les scénarios Preview sont confirmés ;
* les scénarios Export sont confirmés ;
* les scénarios Insert sont confirmés ;
* les catégories de règles métier sont acceptées ;
* les niveaux de validation sont acceptés ;
* les erreurs principales sont identifiées ;
* les scénarios de démonstration sont validés ;
* les limites sont comprises ;
* le périmètre peut être implémenté pendant le sprint.

---

# 22. Conclusion

Le MVP de SmartData Generator doit démontrer un cycle complet de génération de données :

```text
Configuration
    → Analyse du schéma
    → Recherche des règles métier
    → Construction du plan
    → Génération
    → Validation
    → Preview
    → Export ou Insert
    → Rapport
```

Le périmètre reste volontairement limité afin de privilégier :

* la qualité ;
* la cohérence ;
* la sécurité ;
* la traçabilité ;
* la réutilisabilité.

Le service ne cherche pas à remplacer les bases de données, les contraintes applicatives ou l’expertise métier.

Il fournit un moteur générique permettant de préparer, générer, contrôler et livrer des données synthétiques dans un cadre maîtrisé.
