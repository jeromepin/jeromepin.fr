---
title: "Elasticsearch: comment fonctionne la recherche distribuée"
date: 2020-11-18T13:07:00+02:00
draft: true
---

Une opération `CRUD` classique est très simple à effectuer. En effet, le document affecté est représenté par une combinaison unique de son index, son type et son ID.

 À l'inverse, effectuer une recherche nécéssite d'interroger l'ensemble du cluster du fait de la nature distribuée des documents. En effet, nous ne savons pas à l'avance quels documents vont satisfaire à la recherche ni dans les shards ils se trouvent. Il faut alors interroger tous les shards d'un index pour être en mesure de savoir s'ils contiennent des documents satisfaisants la recherche et si oui, lesquels. 

La recherche est séparée en deux étapes : _query_ et _fetch_. 



## Query phase

La première phase est appelée _query phase_. Elle a pour but de savoir quels documents sont concernés par la recherche et dans quels shards ils se trouvent.


{{< fig src="elasticsearch_search_query_animation.gif" title="Représentation de la phase 'Query'" >}}


1. Le client envoi la requête HTTP à l'un des noeuds du cluster. Ce noeud devient -- pour la durée de la requête -- un _coordinating node_. Son rôle est de coordoner la suite de la requête au sein du cluster.
1. La requête est broadcastée à chaque shard (_primary_ ou _replica_) de l'index recherché.
1. Chaque shard effectue la recherche localement et constuit une liste ordonnée contenant les IDs des _n_-documents satisfaisants la recherche. Cette liste -- de taille `from + size` (passés par le client) est appelée _priority queue_. 
1. Les shards retournent leur _priority queue_ au _coordinating node_ qui les regroupe au sein de sa propre _priority queue_, triée elle aussi.



Cette dernière étape marque la fin de la _query phase_. Le _coordinating node_ possède une liste d'IDs triés mais ne possède pas encore les documents eux-mêmes. C'est le rôle de la _fetch phase_.



## Fetch phase

À l'issue de la _query phase_, le _coordinating node_ possède une liste triée d'IDs de documents de taille `(from + size) * shards`.



{{< fig src="elasticsearch_search_fetch_animation.gif" title="Représentation de la phase 'Fetch'" >}}



1. Le _coordinating node_ décide -- au sein de sa propre _priority queue_ -- quels documents doivent être récupérés.  Il effectue des requêtes `mget` aux shards possédant les documents dont l'ID est listé dans sa _priority queue_.
1. Chaque shard construit le document demandé à partir de son champ `_source` et -- si nécéssaire -- modifie son contenu : c'est l'_enrichissement_.  Le shard retourne ensuite le document au _coordinating node_.
1. Une fois tous les documents récupérés, le _coordinating node_ retourne la réponse au client.