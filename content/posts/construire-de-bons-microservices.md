---
title: "Construire de bons microservices"
date: 2018-09-02T14:51:00+01:00
draft: false
---


## Configuration

La configuration d'un service doit être optionnelle et tous ses paramètres doivent avoir une valeur par défaut :

```javascript
const ELASTICSEARCH_HOST = process.env.ELASTICSEARCH_HOST || 'localhost';
```

Ou encore :

```bash
ELASTICSEARCH_HOST=${$ELASTICSEARCH_HOST:-localhost} 
```

Chaque élément de configuration doit être modifiable par une variable d'environnement correctement nommée. L'intérêt est de permettre de changer le comportement de l'application au _runtime_ plutôt qu'au _buildtime_. De plus, l'usage d'orchestrateurs de conteneurs comme _Docker Swarm_ ou _Kubernetes_ rendent plus pratique le passage de variables d'environnement que de fichiers de configuration.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: foo
spec:
  containers:
  - name: foo
    image: foo:1.0
    env:
    - name: ELASTICSEARCH_HOST
      value: "elasticsearch.example.com"
```



## Signaux et fermeture

Une application doit être en mesure de réagir aux [signaux](http://man7.org/linux/man-pages/man7/signal.7.html) envoyés par l'OS et en tirer parti. Par exemple, [Prometheus](https://prometheus.io) recharge sa configuration à la réception d'un SIGHUP :

```bash
$ kill -HUP 1234
INFO[1234] Loading configuration file prometheus.yml source=main.go:201
INFO[1234] Stopping target manager... source=targetmanager.go:281
INFO[1234] Target manager stopped. source=targetmanager.go:216
INFO[1234] Starting target manager... source=targetmanager.go:122
```

L'application doit s'éteindre proprement lorsqu'elle reçoit un `SIGTERM`. Elle doit pouvoir nettoyer tous les éléments externes dont elle a eu besoin : connections ouvertes, caches utilisés, fichiers ouverts, fichiers temporaires créés, etc...

## Logs

La gestion des logs est souvent bien plus complexe que ce que l'on pense. Il est donc généralement intéressant de faire usage d'une librairie dédiée. Cette librairie est en charge de différents paramètres :

* format : JSON, clé-valeur
* contexte : date et heure, module émétteur
* export : réseau (`tcp/udp`, `http`, `kafka`, ...), `syslog`, fichiers
* rotation

Dans le cas d'un microservice, l'application ne doit pas s'occuper du routage et du stockage de ses logs. Elle doit simplement écrire dans `stdout` et `stderr` en fonction des besoins, et laisser un routeur de logs (comme [fluentd](https://github.com/fluent/fluentd) ou [filebeat](https://www.elastic.co/products/beats/filebeat)) gérer et acheminer les logs.

Chaque message de log doit être associé au bon niveau (`debug`, `info`, `warn`, `error`, ...) pour qu'il puisse être affiché et/ou traité de façon optimale. Il peut être intéressant d'afficher un message pour certains cas :

* Message de démarrage de l'application;
* Ports sur lesquels elle écoute;
* Services auxquels elle est connectée;
* Évènements prévus et imprévus;
* Signaux reçus;
* Fermeture;

> [foo] [INFO] Listening on port 80

> [foo] [INFO] Connected to mysql://foo:bar@host:port/database. Alive and kicking !

> ...

> [foo] [INFO] SIGHUP received. Reloading configuration

> ...
 
> [foo] [INFO] Shutting down... Closing connexions, removing temporary files


## Choix du langage

### Éviter les langages à machines virtuelles

Les langages basés sur des machines virtuelles (Java, Clojure, Erlang, .NET) sont plus lents à démarrer et ont nécessairement besoin de plus de ressources. De plus, ces machines virtuelles sont généralement conçues pour gérer de large applications monolithiques qui ont besoin de fonctionnalités avancées de gestion de mémoire, de CPU, de threads, etc... Ces fonctionnalités sont redondantes avec les orchestrateurs et les runtimes et peuvent créer des conflits, comme par exemple la JVM qui ne supporte pas (ou mal) les limites de CPU et de mémoire définies dans un conteneur. Seules les [versions les plus récentes du JDK 10](https://bugs.openjdk.java.net/browse/JDK-8196595) permettent une prise en charge correcte de ces paramètres.

### Créer des binaires statiques

Utiliser un langage qui crée des binaires statiques présente plusieurs avantages :

* le binaire est portable : les librairies liées sont distribuées avec le binaire;
* il n'est pas nécessaire d'avoir une arborescence complète d'un OS (`/bin`, `/usr/bin`, `/tmp`, etc...) pour exécuter le binaire;
* la construction du binaire est prévisible;
* le binaire est moins sensible aux contaminations de ses librairies par des tierces-parties;

C'est avec toutes ces contraintes que des langages comme [Go](https://golang.org/) et [Rust](https://www.rust-lang.org/) ont vu leur popularité croître énormément ces dernière années.

Pour un même programme C++ :

```cpp
#include <iostream>

int main() {
    std::cout << "Foo";
    return 0;
}
```

Le binaire compilé dynamiquement pèse 7.8Ko contre 1.6Mo statiquement. La différence vient de la présence (ou non) des librairies nécessaires au sein du binaire.

La commande `ldd` permet de connaître les librairies liées au binaire :

```bash
$ g++ -o foo foo.cpp
$ ldd foo
	linux-vdso.so.1 (0x00007fffc9ff8000)
	libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007f6c9c4b6000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f6c9c1b5000)
	libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007f6c9bf9f000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f6c9bbf4000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f6c9c7c1000)
```

Mon binaire `foo` requiert notamment `libstdc++.so.6 ` (`/usr/lib/x86_64-linux-gnu/libstdc++.so.6`) et `libc.so.6` (`/lib/x86_64-linux-gnu/libc.so.6`). Si je distribue ce binaire sur une autre machine, il faudra non seulement qu'elle tourne sur le même OS, mais aussi que les librairies soient les mêmes (chemin et version) :

```bash
$ mv /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/libc.so.6.old
$ ./foo
./foo: error while loading shared libraries: libc.so.6: cannot open shared object file: No such file or directory
```


## Stateless vs Stateful

Un bon conteneur est un conteneur que l'on peut déplacer et redémarrer à la demande, sans pré-requis. Il faut donc qu'il soit le plus possible `stateless` : toutes les données persistantes dont a besoin l'application doivent être stockées dans des systèmes externes comme une base de données. Il ne doit pas y avoir de différence entre plusieurs instances d'une application.


## Robustesse, healtchecks et timeouts

L'application doit être en mesure de gérer les erreurs via une dégradation de service ou via du _back-off_ plutôt que de crasher. Elle doit pouvoir non-seulement répondre à des _health checks_ (via une route http par exemple) mais aussi en émettre afin de surveiller la disponibilité des services liés.

À un stade plus avancé, l'application doit supporter des mécanismes plus complexes comme les _timeouts_, le _throttling_ et les [circuit-breakers](https://en.wikipedia.org/wiki/Circuit_breaker_design_pattern).