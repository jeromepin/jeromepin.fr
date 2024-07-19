---
title: "Sharding : Propriétés et fonctionnement"
date: 2018-07-12T08:54:00+01:00
lang: fr
taxonomies:
  tags: []
extra:
  sources: []
  footnotes: []
---

Le sharding (aussi souvent nommé _horizontal partitioning_) est une méthode de séparation des données d'une base de données en plusieurs groupes logiques, généralement répartis sur plusieurs nœuds d'un cluster.

Le sharding a plusieurs avantages :

* dépasser les limitations d'une machine seule (CPU, stockage, etc...);
* effectuer des traitements concurrents;
* limiter la diffusion d'une requête à un sous-set de données;

Le sharding est souvent implémenté au niveau de la base de donnée elle-même (comme [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/6.2/_basic_concepts.html#getting-started-shards-and-replicas), Cassandra ou [MongoDB](https://docs.mongodb.com/manual/sharding/)) mais peut aussi l'être au niveau applicatif pour supporter des bases de données où le sharding n'est pas natif (comme [Redis](https://redis.io/topics/partitioning)).

Il existe plusieurs stratégies pour distribuer des données dans plusieurs base de données. Chacune a ses avantages et ses inconvénients et doit être choisie avec soin en fonction des besoins et des contraintes. Quelle que soit la stratégie choisie, il faut toujours prendre en compte les possibles **hotspots** : une distribution inégale des données entraine une surutilisation de certains shards et réduit presque à néant l'intérêt du sharding.

## Principes de base

### Notions

* clé de shard : (_shard key_) Suite de caractères qui identifie de façon unique un shard.
* shard logique : (_logical shard_) Ensemble de données stockées sur un seul nœud et partageant la même clé de shard.
* shard physique : (_physical shard_) Un nœud du cluster, il peut contenir plusieurs shards logiques.

### Comment les données sont lues et écrites

Les bases de données sont utilisées pour stocker des données. Par conséquent le choix de la stratégie de sharding dépend de ces accès. Il s'agit de définir à l'avance les [SLOs](https://landing.google.com/sre/sre-book/chapters/service-level-objectives/) :

* Quelle est la distribution entre la lecture et l'écriture ? (50/50, 80/20, etc...)
* Quels volumes sont gérés ?
* Quels sont les objectifs de performance ? (latence, vitesse, etc...)

### Comment les données sont distribuées

Les **hotspot** contrebalancent presque totalement l'intérêt du sharding. Il faut donc choisir avec soin le critère sur lequel les données vont être distribuées. Se baser sur une clé trop commune et non-uniformément distribuée va créer un déséquilibre dans la répartition de nos données.

Par exemple, dans une base de données qui stocke des documents utilisateurs, distribuer les données en se basant sur l'identifiant de l'utilisateur est une mauvaise idée. Si un utilisateur enregistre beaucoup plus de documents que les autres, le shard auquel il est associé va croître fortement. Que va-t-il se passer lorsque ce shard dépassera la taille d'un nœud ? Comment ce shard va impacter les performances du reste du cluster ?

### Comment gérer la redistribution des données

Une fois que les questions ci-dessus sont traitées, que le cluster fonctionne et que l'utilisation prend de l'ampleur, un premier problème survient : comment ajouter/modifier/supprimer des nœuds sans affecter les performances ?

Lors de la modification de l'état du cluster, les données stockées vont devoir être redistribuées et il va falloir en déplacer de grandes quantités rapidement sans avoir d'incidence sur les performances.



## Sharding algorithmique

Le sharding algorithmique (aussi nommé _Client side partitioning_) permet au client de déterminer le shard sans aide extérieure, en se basant uniquement sur une fonction généralement de la forme `hash(key) % num_nodes`.

[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-routing-field.html) utilise cette stratégie pour définir sur quel shard doit se trouver un document :
```
shard_num = hash_murmur3(doc._id) % num_primary_shards
```

Le sharding algorithmique distribue les données en se basant uniquement sur cette fonction, et ne prend en compte aucun paramètre extérieur comme le taux d'utilisation d'un nœud, la taille de la donnée à traiter, etc...

Redistribuer les données peut s'avérer complexe : cela requiert non seulement de déplacer les données mais aussi de mettre à jour la fonction utilisée. La fonction idéale ne devrait pas nécessiter de déplacer plus de `1/n` données et ne devrait pas déplacer des données qui n'ont pas besoin de l'être.


## Sharding dynamique

Le sharding dynamique (parfois nommé _Proxy assisted partitioning_) nécessite un **service externe** pour déterminer l'emplacement d'une donnée. Ce service agit comme un annuaire et indique la correspondance entre une clé (ou un ensemble de clés) et le shard sur lequel cette clé est assignée. Par exemple, [HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html#NameNode_and_DataNodes) utilise un _Namenode_ pour stocker ses métadonnnées.

| range		| shard 		|
|------------|-------------|
| 0, 3			| 0				|
| 4, 7			| 1				|
| 8, B			| 2				|
| C, F			| 3				|

Pour lire ou écrire une donnée, les clients ont nécessairement besoin de contacte le service de localisation. Celui va ensuite contacter la base de données elle-même, faisant office de proxy.

Ce service externe permet de mieux gérer les données non-uniformément distribuées puisque les ensembles de clés n'ont pas besoin d'être de taille identique mais peuvent varier en fonction des besoins.

En revanche, il devient aussi un point de défaillance unique : chaque lecture ou écriture a besoin d'y accéder, il faut donc que la stabilité et les performances soient au rendez-vous. Il ne peut pas être caché ni dupliqué  facilement : des données obsolètes causeraient un désastre sur le cluster.


## Conclusion

Le sharding ajoute de la complexité non seulement en termes de développement mais aussi d'opérations : les données ne sont plus stockées au même endroit, le réseau introduit de la latence, la topologie change, plus de serveurs doivent être configurés, etc...

Le sharding ne doit pas être le premier axe d'amélioration. Bien connaître les données que à stocker et la façon dont elles vont être utilisées est beaucoup plus important. Utiliser un serveur plus puissant suffit souvent à régler les problèmes de performances tant que l'échelle reste modérée.

Si l'application est limitée par les performances de lecture de la base de données, ajouter des **caches** ou des **replicas de lecture** peut corriger le problème sans ajouter trop de complexité.

Enfin, il est important de s'assurer que les données sont organisées de façon optimale : les blobs sont sur un stockage externe (système de fichier, stockage objets, etc...), l'analyse et la recherche sont délégués à d'autres systèmes, etc...

