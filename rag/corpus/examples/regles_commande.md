---
title: Règles de gestion des commandes
category: rule
entity: Commande
---

## Champs obligatoires d'une commande

Une commande doit toujours renseigner un identifiant client, une date de commande et au moins une ligne de commande. Une commande sans ligne de commande est invalide.

## Montant total positif

Le montant total d'une commande doit toujours être strictement positif. Un montant nul ou négatif est une valeur invalide.

## Cohérence des dates

La date de livraison prévue doit être postérieure à la date de commande. Un écart de plus de 90 jours entre les deux dates est considéré comme un avertissement, pas comme une erreur bloquante.

## Statut de commande

Le champ statut doit appartenir à la liste suivante : `EN_ATTENTE`, `CONFIRMEE`, `EXPEDIEE`, `LIVREE`, `ANNULEE`. Toute autre valeur est invalide.

## Règle conditionnelle sur l'annulation

Si le statut d'une commande est `ANNULEE`, un motif d'annulation devient obligatoire. Pour tout autre statut, ce champ reste optionnel.

## Unicité de la référence

La référence de commande doit être unique sur l'ensemble du système. Deux commandes ne peuvent jamais partager la même référence.
