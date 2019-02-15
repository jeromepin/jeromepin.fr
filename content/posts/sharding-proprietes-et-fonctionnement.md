---
title: "Sharding : Propriétés et fonctionnement"
date: 2018-07-12T08:54:00+01:00
draft: false
---

Le sharding est une méthode de séparation des données d'une base de données en plusieurs groupes logiques, généralement répartis sur plusieurs serveurs différents.

Le sharding a plusieurs avantages :

* dépasser les limitations d'une machine seule (CPU, stockage, etc...);
* Effectuer des traitements concurrents;

Le sharding est souvent implémenté au niveau de la base de donnée elle-même (comme [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/6.2/_basic_concepts.html#getting-started-shards-and-replicas), Cassandra ou [MongoDB](https://docs.mongodb.com/manual/sharding/)) mais peut aussi l'être au niveau applicatif pour supporter des bases de données où le sharding n'est pas natif ([Redis](https://redis.io/topics/partitioning)).

Il existe plusieurs stratégies pour distribuer des données dans plusieurs base de données. Chacune a ses avantages et ses inconvénients et doit être choisie avec soin en fonction des besoins et des contraintes. Quelque soit la stratégie choisie, il faut toujours prendre en compte les possibles **hotspots** : une distribution inégale des données entraine une sur-utilisation de certains shards et réduit presque à néant l'interêt du sharding.

## Principes de base

### Notions

* clé de partition : (_partition key_) Suite de charactères qui identifient de façon unique une partition.
* shard logique : (_logical shard_) Ensemble de données partageant la même clé de partition, stocké sur un seul noeud.
* shard physique : (_physical shard_) Un noeud du cluster, il peut contenir plusieurs shards logiques.

### Comment les données sont lues et écrites

Les bases de données sont utilisées pour stocker et récuperer des données. Par conséquent le choix de la stratégie de sharding dépend de ces accès. Il s'agit de définir à l'avance les [SLOs](https://landing.google.com/sre/sre-book/chapters/service-level-objectives/) :

* Quelle est la distribution entre la lecture et l'écriture ? (50/50, 80/20, etc...)
* Quels volumes sont gérés ?
* Quels sont les objectifs de performance (latence, vitesse, etc...)

### Comment les données sont distribuées

Comme évoqué ci-dessus, les **hotspot** contre-balancent presque totalement l'interêt du sharding. Il faut donc choisir avec le soin le critère sur lequel les données vont être distribuées. Se baser sur un clé trop commune et non-uniformément distribuée va créer un désequilibre dans la répartition de nos données.

Par exemple, dans une base de donmées qui stocke des documents utilisateurs, distribuer les données en se basant sur l'identifiant de l'utilisateur est une mauvaise idée. Si un utilisateur enregistre beaucoup plus de documents que les autres, le shard auquel il est associé va croître énormément. Que va-t'il se passer lorsque ce shard dépasse la taille d'un serveur ?

### Comment gérer le redistribution des données

Une fois que les questions ci-dessus sont traitées, que le cluster fonctionne et que l'utilisation prend de l'ampleur, un premier problème arrive : comment ajouter/modifier/supprimer des noeuds sans affecter les performances ?

Lors de la modification de l'état du cluster, les données stockées vont devoir être redistribuées et il va falloir en déplacer de grandes quantités rapidement sans avoir d'incidence sur les performances.



## Sharding algorithmique

Le sharding algorithmique (aussi nommé _Client side partitioning_) permet au client de determiner le shard sans aide extérieure, en se basant uniquement sur une fonction généralement de la forme `hash(key) % num_nodes`.

[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-routing-field.html) utilise cette stratégie pour définir sur quel shard doit se trouver un document :
```
shard_num = hash_murmur3(doc._id) % num_primary_shards
```

Le sharding algorithmique distribue les données en se basant uniquement sur cette fonction, et ne prend en compte aucun paramètre extérieur comme le taux d'utilisation d'un noeud, la taille de la donnée à traiter, etc...

Re-distribuer les données peut s'avérer complexe : cela requiert non seulement de déplacer les données mais aussi de mettre à jour la fonction utilisée. La fonction idéale ne devrait pas nécéssiter de déplacer plus de `1/n` données et ne devrait pas déplacer des données qui n'ont pas besoin de l'être.


## Sharding dynamique

Le sharding dynamique (parfois nommé _Proxy assisted partitioning_) nécéssite un **service externe** pour determiner l'emplacement d'une donnée. Ce service agit comme un annuaire et indique la correspondance entre une clé (ou un ensemble de clés) et le shard sur lequel cette clé est assignée. Par exemple, [HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html#NameNode_and_DataNodes) utilise un _Namenode_ pour stocker ses méta-donnnées.

| range		| shard 		|
|------------|-------------|
| 0, 3			| 0				|
| 4, 7			| 1				|
| 8, B			| 2				|
| C, F			| 3				|

Pour lire ou écrire une donnée, les clients ont nécéssairement besoin de contacter d'abord le service de localisation avant de pouvoir contacter la base de donnée elle-même.

Ce service externe permet de mieux gérer les données non-uniformément distribuées puisque les ensemble de clés m'ont pas besoin d'être de taille identique mais peuvent varier en fonction des besoins.

En revanche, il devient aussi un point de défaillance unique : chaque lecture ou écriture à besoin d'y accéder, il faut donc que la stabilité et les performances soient au rendez-vous. Il ne peut pas être caché ni dupliqué  facilement : des données obsolètes causeraient un désastre monstrueux sur le cluster.