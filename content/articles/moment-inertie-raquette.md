---
title: Moments d'inertie d'une raquette de tennis
date: 2024-07-19
lang: fr
taxonomies:
  tags:
    - physics
    - tennis
    - french
extra:
  sources:
    - - https://doi.org/10.1007/s12283-019-0303-8
      - Taraborrelli, L., Grant, R., Sullivan, M. et al. Recommendations for
        estimating the moments of inertia of a tennis racket. Sports Eng 22, 11
        (2019).
    - - https://pubmed.ncbi.nlm.nih.gov/24260004/
      - Nesbit, Steven M et al. “The effects of racket inertia tensor on elbow
        loadings and racket behavior for central and eccentric impacts.” Journal
        of sports science & medicine vol. 5,2 304-17. 1 Jun. 2006
  footnotes: []

---

Le _moment d'inertie_ (exprimé en {{ katex(body="kg.m^{2}") }}) est une mesure de la résistance d'un objet à changer sa vitesse de rotation autour d'un axe (au même titre que l'_inertie_ est la résistance d'un objet à changer sa vitesse de translation).
Il varie avec la masse et la distance de la-dite masse par rapport à l'axe de rotation.

{{ figure(src="https://www.ncbi.nlm.nih.gov/pmc/articles/instance/3827573/bin/jssm-05-304-g001.jpg" title="Axes de rotations d'une raquette de tennis") }}

Une raquette de tennis possède 3 moments d'inertie principaux (passant par le centre de masse) :
- _transversal_: la raquette tourne autour de l'aze _x_ (Fig. 1).
- _lateral_: la raquette tourne autour de l'axe _y_ (Fig. 1) de façon similaire à un coup droit (le réel moment d'inertie pour ce genre de coup est toutefois mesuré là où la main se place sur le manche plutôt qu'au centre de masse pour être plus représentatif de l'effort à fournir dans la réalité).
- _polaire_: la raquette tourne autour de l'axe _z_ (Fig. 1), comme par exemple lorsqu'une balle est frappée décentrée.

Le _moment de rotation polaire_ est généralement appelé _twistweight_. C'est lui qui est impliqué lorsqu'une balle est frappée de façon décentrée par rapport à l'axe de rotation _z_. L'augmenter permet donc de rendre une raquette moins sensible au décentrage, en placant des masses à 3h et 9h.

Le _moment de rotation lateral_ est généralement appelé _swingweight_. Il est impliqué dès lors que la raquette entre en mouvement. L'augmenter (en ajoutant une masse à 12h par exemple) va permettre d'augmenter la puissance de frappe.

Plus on ajoute de la masse à distance de l'axe de rotation, plus le moment d'inertie augmente, plus il va être difficile de faire tourner la raquette autour de ce même axe.