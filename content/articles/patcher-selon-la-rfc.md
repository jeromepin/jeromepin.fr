---
title: "PATCH-er selon la RFC"
date: 2019-04-02T16:08:00+01:00
lang: fr
taxonomies:
  tags: []
extra:
  sources: []
  footnotes: []
---


## PUT: mise à jour totale

La plupart des APIs REST proposent des mécanismes pour modifier des ressources, notamment grâce au verbe _PUT_ qui permet d'envoyer la ressource à mettre à jour. _PUT_ pose tout de même 3 problèmes :

* Il est nécéssaire de faire un _GET_ au préalable afin d'obtenir la totalité de la ressource
* Il faut s'assurer que la ressource n'a pas été modifiée côté serveur entre le _GET_ et le _PUT_
* Il faut envoyer l'intégralité de la ressource, y compris les champs qui restent inchangés.

La méthode _PUT_ apparait ne pas être la solution idéale pour effectuer une mise à jour partielle.

Certaines API proposent d'exposer directement chaque champ de la ressource et d'utiliser _PUT_ pour faire la mise à jour :

```json,linenos
PUT /users/jeromepin/age

24
```

C'est une solution simple mais qui rajoute beaucoup de complexité dans l'API. Et si le client souhaite mettre à jour plusieurs informations, il doit effectuer plusieurs appels _PUT_. La solution n'est toujours pas là. Heureusement, la [RFC 5789](https://tools.ietf.org/html/rfc5789) propose un verbe HTTP conçu pour les mises à jour partielles : _PATCH_

## PATCH: mauvais usage

_PATCH_ permet donc de modifier **partiellement** une ressource donnée. Ainsi beaucoup d'APIs ont ajouté le support de ce verbe au travers d'appels tels que :

```json,linenos
PATCH /users/jeromepin

age=25
```

ou encore :

```json,linenos
PATCH /users/jeromepin

{ "age" : "25" }
```

**CE N'EST PAS LE RÔLE DE _PATCH_ !**

_PATCH_ ne doit pas envoyer une partie d'une ressource.


## PATCH-er correctement

Le but de _PATCH_ n'est pas seulement de mettre à jour une ressource. En réalité, ce n'est pas du tout la façon dont _PATCH_ doit fonctionner. La RFC indique :

> The difference between the PUT and PATCH requests is reflected in the way the server processes the enclosed entity to modify the resource identified by the Request-URI.  In a PUT request, the enclosed entity is considered to be a modified version of the resource stored on the origin server, and the client is requesting that the stored version be replaced.  With PATCH, however, the enclosed entity contains a set of instructions describing how a resource currently residing on the origin server should be modified to produce a new version.

Il est clairement indiqué que _PATCH_, contrairement à _PUT_ qui envoi la nouvelle ressource dans son intégralité, doit envoyer une **liste d'instructions décrivant la façon selon laquelle la ressource située sur le serveur doit être modifiée**.

Une requête _PATCH_ ressemble à ça :

```json,linenos
PATCH /users/jeromepin HTTP/1.1
Host: www.example.com
Content-Type: application/example

[description of changes]
```

`[description of changes]` est appelé "_patch document_" (ou plus simplement "_patch_"). Le format de ce patch n'est pas défini dans cette RFC est peut-être de n'importe quel type comme par exemple la sortie de la commande `diff` :

```json,linenos
PATCH /users/jeromepin HTTP/1.1
Host: www.example.com
Content-Type: application/diff

--- old-json	2019-04-01 12:02:50.000000000 +0200
+++ new-json	2019-04-01 12:03:00.000000000 +0200
@@ -1,4 +1,4 @@
{
    "name": "Jerome Pin",
-   "age": 24
+   "age": 25
}
```

Le `Content-Type` du _PATCH_ doit être adapté au format du patch envoyé.

Le serveur **DOIT** appliquer la totalité des changements de la requête de façon atomique et ne jamais fournir (c.à.d enregistrer en base ou retourner à un client) la ressource partiellement modifiée. Si le patch ne peut pas être appliqué dans sa totalité, alors il ne doit pas être appliqué du tout.


### Quel format pour un patch ?

La RFC 5789 est très souple et n'indique pas de type spécifique pour le format du patch, ainsi, c'est au serveur de veiller à supporter le type de patch approprié aux documents qu'il manipule.

Heureusement, pour la manipulation de documents JSON (issus par exemple de base de données orientées documents), les RFC [6901](https://tools.ietf.org/html/rfc6901) et [6902](https://tools.ietf.org/html/rfc6902) définissent respectivement les termes _"JSON Pointer"_ et _"JSON Patch"_.

Un _"JSON Pointer"_ défini une syntaxe sous forme de chaine de caractères pour identifier une valeur spécifique au sein d'un objet JSON : `/users/0/email`.
Un _"JSON Patch"_ défini la structure d'un document JSON permettant d'exprimer une série de modifications à appliquer à un document JSON :

```json,linenos
[
     { "op": "test", "path": "/a/b/c", "value": "foo" },
     { "op": "remove", "path": "/a/b/c" },
     { "op": "add", "path": "/a/b/c", "value": [ "foo", "bar" ] },
     { "op": "replace", "path": "/a/b/c", "value": 42 },
     { "op": "move", "from": "/a/b/c", "path": "/a/b/d" },
     { "op": "copy", "from": "/a/b/d", "path": "/a/b/e" }
]
```

Avec ces deux nouvelles RFC, il est possible d'effectuer une requête _PATCH_ pour enfin modifier un document JSON :

```json,linenos
PATCH /users/jeromepin HTTP/1.1
Host: www.example.com
Content-Type: application/json-patch+json

[
    { "op": "replace", "path": "/age", "value": "25" }
]
```

Dans le cas où le serveur manipule du XML, une [RFC](http://tools.ietf.org/html/rfc5261) décrit un format équivalent au JSON-Patch.

## Conclusion

Cet usage de _PATCH_ reste très peu connu. Il est censé être le standard à utiliser pour des mises à jour partielles, mais il est facile de s'aperçevoir qu'un tel fonctionnement complexifie la gestion du serveur et la façon dont nous avons l'habitude d'utiliser les verbes plus traditionnels (_GET_, _POST_, _PUT_). La RFC étant très souple, il est tout à fait possible d'utiliser son propre format de patch, ainsi pour incrémenter l'age, il est possible de faire quelque chose comme :

```json,linenos
PATCH /users/jeromepin HTTP/1.1
Host: www.example.com
Content-Type: application/custom-format+json

[
    { "increment": "age" }
]
```

Évidemment, d'un point de vue conceptuel, il faut alors se demander si cette façon d'envoyer des actions plutôt que des états est compatible avec la philosophie REST ? N'est-ce pas plus proche de RPC ?
