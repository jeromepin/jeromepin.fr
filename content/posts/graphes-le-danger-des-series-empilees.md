---
title: "Graphes : Le danger des séries empilées"
date: 2020-05-03T11:33:00+01:00
---



Le graphe suivant montre un nombre de requêtes en fonction du temps sur 4 serveurs. Les séries sont empilées afin de pouvoir facilement lire la somme de ces requêtes sur l'ensemble de l'infrastructure.

{{< figure src="/images/graphes-le-danger-des-series-empilees/mischievous_node_first.svg" title="Exemple typiques de séries empilées : nombre de requêtes en fonction du temps sur 4 serveurs" >}}

Il est très facile d'extraire quelques informations : 

* 3 des 4 serveurs reçoivent chacun une dizaine de requêtes par seconde;
* L'un des serveurs reçoit plus de requêtes que les autres;
* L'ensemble de l'infrastructure encaisse une soixantaine de requêtes par seconde;

## Pourquoi les séries empilées sont dangereuses ?

Il semble aussi évident que l'infrastructure a vu une chute massive des requêtes sur chacun des noeuds.

En réordonnant les séries en plaçant le serveur le plus chargé en haut, une différence intéréssante se dessine :

{{< figure src="/images/graphes-le-danger-des-series-empilees/mischievous_node_last.svg" title="Le même exemple avec les séries ordonnées différement" >}}

Toute l'infrastructure n'est pas affectée par la diminution brutale du nombre de requêtes mais seulement un des serveurs !

{{< figure src="https://media.giphy.com/media/3o7btW7VDxqrhJEnqE/giphy.gif" title="Denis Brogniart est stupéfait de cette découverte" width="300" >}}

### Est-ce un problème avec les données ? Avec le graphe ?

Les séries inférieures influencent la forme des séries supérieures. L'ordre des séries change donc la perception que l'on a d'un graphe et, par conséquent, les conclusions qu'on en tire ! 

Le fait de pouvoir facilement lire une somme pousse à ne plus prendre en compte les différences entre les séries mais seulement lire la série la plus haute et ainsi voir, de façon erronée, une baisse sur toute l'infrastructure.

Ce ne sont ni les données ni leur représentation qui sont erronées, mais bien la lecture que nous en avons. Sans être vigilant, il est facile de penser que la baisse du nombre de requêtes affecte tout l'infrastructure.

## Comment s'en prémunir ?

Il est très facile de se prémunir d'une telle erreur d'interprétation : ne pas empiler les séries. Pour pouvoir quand même lire un total, il suffit d'ajouter une série représentant leur somme :

{{< figure src="/images/graphes-le-danger-des-series-empilees/unstacked.svg" title="Le même exemple sans empiler les séries et avec une somme des séries (noir)" >}}

Avec cette représentation, il apparait de façon très évidente que les variations d'une série ont bien un effet sur le total (puisqu'il s'agit de la somme des points des séries) mais pas sur les autres séries.
