---
title: Règles de gestion des clients
category: rule
entity: Client
---

## Relation entre client et commandes

Chaque commande doit référencer un client existant. Une commande ne peut pas être générée pour un identifiant client qui n'existe pas dans le référentiel client.

## Adresse email valide

L'adresse email d'un client doit respecter un format d'email standard (présence d'un `@` et d'un domaine). Deux clients ne peuvent pas partager la même adresse email.

## Segment client

Le champ segment doit appartenir à la liste suivante : `PARTICULIER`, `PROFESSIONNEL`. Un client `PROFESSIONNEL` doit obligatoirement renseigner un numéro d'entreprise ; ce champ reste vide pour un `PARTICULIER`.

## Exception : clients de test

Les clients dont l'identifiant commence par le préfixe `TEST-` sont exclus des contrôles d'unicité d'email : plusieurs clients de test peuvent partager la même adresse email factice utilisée en environnement de démonstration.
