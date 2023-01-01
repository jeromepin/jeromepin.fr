---
title: "Chiffrement, codage et hachage"
date: 2020-07-22T08:12:00+02:00
draft: true
---


## Codage de l'information

## Fonction de hachage

Fonction qui calcule, à partir d'une donnée, une empreinte (un _hash_) servant à identifier la donnée initiale.

Un changement, même mineur, dans la donnée initiale est censé assurer une empreinte différente. Dans la cas contraire, il s'agit d'une collision : des données différentes créent une même empreinte.

``` bash,linenos
$ echo "fonction" | md5sum
3427b8d6a435abf3673490bfa2762ef4

$ echo "Fonction" | md5sum
24a1b0ab350265cd7eb37aa544237288
```

Certaines fonctions, notamment utilisée en cryptographie, sont des fonctions à sens unique : connaissant le hash, il est impossible de calculer la donnée initiale.

Les applications sont multiple :

* Vérifier l'intégrité d'une donnée (_checksum_)
* Identifier rapidement des données (_fingerprinting_) : il est plus rapide de calculer et comparer des hashs de quelques octets que des données complètes
* Indexer du contenu dans des tables (_hash table_)
* Stocker des données sensibles sans possibilité de calculer la donnée originale


## Chiffrement

