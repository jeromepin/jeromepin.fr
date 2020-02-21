---
title: "Timeseries : Cardinalité et explosion"
date: 2020-01-04T21:12:00+01:00
---


[Wikipédia](https://fr.wikipedia.org/wiki/Cardinalit%C3%A9_(math%C3%A9matiques)) indique :

> En mathématiques, la cardinalité est une notion de taille pour les ensembles. Lorsqu'un ensemble est fini, c'est-à-dire si ses éléments peuvent être listés par une suite finie, son cardinal est la longueur de cette suite, autrement dit il s'agit du nombre d'éléments de l'ensemble.

C'est donc le nombre de valeurs uniques d'un ensemble.

Dans le cas de Prometheus, la cardinalité d'une métrique $M$ est le produit de la cardinalité de ses $n$ labels $L_{n}$ tel que :

$$ Card(M) = \prod_{n=0}^{X}Card(L_n) $$

Ainsi, il est facile d'imaginer une métrique `http_request_duration_seconds` ayant les caractéristiques suivantes :

* Un label `verb` qui représente les méthodes HTTP et qui a pour valeurs possibles : `GET`, `POST`, `PUT` et `DELETE` ($Card = 4$);
* Un label `le` qui est le bucket dans lequel la mesure tombe. Il a pour valeurs possibles : 0.1, 0.2, 0.5, 1, `+Inf` ($Card = 5$);
* Un label `browser` qui indique le navigateur utilisé par le client : Chrome, Firefox, IE, Edge, Safari, Opera, Others ($Card = 7$);
* Un label `device` qui représente la famille de périphérique utilisé par le client : Desktop, Mobile, Tablet ($Card = 3$);
* En enfin, un label `os` qui indique la "marque" de l'OS utilisé par le client : Linux, Microsoft, Apple ($Card = 3$);

Si la métrique n'avait qu'un seul label, voire deux, la cardinalité serait faible. Le problème survient lorsque un label est ajouté ou lorsque la cardinalité d'un label augmente subitement. La métrique fini innévitablement par arriver à une [explosion combinatoire](https://fr.wikipedia.org/wiki/Explosion_combinatoire) : un petit changement du nombre de données rend la cardinalité de notre métrique irraisonable.

Au début, tout commence de manière raisonnable : il n'y a que 2 verbes et 5 buckets. Puis on se dit qu'il faudrait séparer par OS. Puis par famille de client. Puis par navigateur. Puis par... Et la cardinalité est passée de $2 \cdot 5 = 10$ à $4 \cdot 5 \cdot 7 \cdot 3 \cdot 3 = 1260$ !

Le plus surprenant c'est que l'augmentation de la cardinalité des labels augmente considérablement la cardinalité de la métrique ! Admettons que chaque cardinalité augmente de 1 (ce qui est peu), la cardinalité de la métrique passe de $1260$ à $5 \cdot 6 \cdot 8 \cdot 4 \cdot 4 = 3840$, soit plus du triple de la valeur initiale !

Que va-t'il se passer si l'on décide d'ajouter un label `customer` qui a pour valeur un UUID ? D'après [Wikipédia](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)), un UUID dans sa version 4 a 122 bits générés aléatoirement à 0 ou 1, soit $2^{122}$ possiblités !

{{< figure src="https://media.giphy.com/media/O3GqAYR9jFxLi/source.gif" title="Boooooom" >}}

 
Il semble évident que demander une granularité aussi fine à un tel système est impossible. Les timeseries sont conçues pour traiter et afficher des données en temps réel. Malheureusement, le temps réel est quelque chose de très coûteux, il faut donc faire quelques compromis. Limiter la précision (et donc la cardinalité) est un bon moyen d'équilibrer le cout. Il faudrait alors se tourner vers un second système dédié à de la précision, tel que l'analyse de logs, pour compléter les mesures.

Les timeseries servent à donner une vue d'ensemble d'un système (que ce soit au niveau d'un serveur, d'une application, d'un cluster, d'un datacenter...) mais ne peuvent pas servir à débugger et à trouver l'origine d'un problème. Une fois qu'un problème est détecté, c'est vers les logs qu'il faut se tourner.