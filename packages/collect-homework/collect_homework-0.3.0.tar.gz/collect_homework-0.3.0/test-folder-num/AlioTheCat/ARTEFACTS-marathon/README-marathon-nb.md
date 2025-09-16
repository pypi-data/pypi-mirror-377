---
jupytext:
  encoding: '# -*- coding: utf-8 -*-'
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# marathon (divers basique)

pour réaliser ce TP localement sur votre ordi, {download}`commencez par télécharger le zip<./ARTEFACTS-marathon.zip>`

un petit TP pour travailler

* le chargement et la sélection
* un peu de groupby
* un peu de gestion du temps et des durées

```{code-cell} ipython3
import pandas as pd
```

## les données

+++

On va étudier un jeu de données trouvé sur Internet

```{code-cell} ipython3
# 2024: le site original semble être *down*
# URL = "http://www.xavierdupre.fr/enseignement/complements/marathon.txt"

DATA = "data/marathon.txt"
```

```{code-cell} ipython3
# regardons les 5 premières lignes du fichier de données
# (ou bien ouvrez-le dans vs-code)

with open(DATA) as f:
    for _ in range(5):
        print(next(f), end="")
```

## chargement

+++

Le premier réflexe pour charger un fichier de ce genre, c'est d'utiliser la fonction `read_csv` de pandas

```{code-cell} ipython3
# votre cellule de code
# qu'on va faire descendre
# et raffiner au fur et à mesure

df0 = pd.read_csv(DATA)
df0.head()
```

c'est un début, mais ça ne marche pas franchement bien !

+++

il faut donc bien regarder la doc

```{code-cell} ipython3
# pd.read_csv?
```

+++ {"tags": ["level_basic"]}

et pour commencer je vous invite à préciser le séparateur:

```{code-cell} ipython3
# à vous de modifier cette première approche

df1 = pd.read_csv(DATA, sep = "\t")
df1
```

```{code-cell} ipython3
# pour vérifier, ceci doit afficher True

df1.shape == (358, 4) and df1.iloc[0, 0] == 'PARIS' and df1.columns[0] == 'PARIS'
```

+++ {"tags": ["level_basic"], "slideshow": {"slide_type": ""}}

c'est mieux, mais les noms des colonnes ne sont pas corrects  
en effet par défaut, `read_csv` utilise la première ligne pour déterminer les noms des colonnes  
or dans le fichier texte il n'y a pas le nom des colonnes ! (voyez ci-dessus)

du coup ce serait pertinent de donner un nom aux colonnes

```{code-cell} ipython3
NAMES = ["city", "year", "duration", "seconds"]
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
# à vous de créer une donnée bien propre
df = pd.read_csv(DATA, sep = "\t", names = NAMES)
df
```

```{code-cell} ipython3
:tags: [raises-exception]

# pour vérifier, ceci doit afficher True

df.shape == (359, 4) and df.iloc[0, 0] == 'PARIS' and df.columns[0] == 'city'
```

```{code-cell} ipython3
:tags: [raises-exception]

# ce qui maintenant nous donne ceci

df.head(2)
```

## sauvegarde dans un fichier csv

+++

dans l'autre sens, quand on a produit une dataframe et qu'on veut sauver le résultat dans un fichier texte

```{code-cell} ipython3
# df.to_csv?
```

par exemple je crée ici un fichier qu'on peut relire sous excel

```{code-cell} ipython3
:tags: [raises-exception]

loop = "marathon-loop.csv"
df.to_csv(loop, sep=";", index=False)
```

```{code-cell} ipython3
:tags: [raises-exception]

# pour voir un aperçu
#  nouveau vous pouvez regarder le fichier avec vs-code 
# ou encore dans le terminal avec $ less marathon-loop.csv (sortir avec 'q')

%cat marathon-loop.csv
```

## des recherches

+++ {"tags": ["level_basic"]}

### les éditions de 1971

```{code-cell} ipython3
# à vous de calculer les éditions de 1971

df_1971 = df[ (df["year"] == 1971) ]
```

```{code-cell} ipython3
:tags: [raises-exception]

# ceci doit retourner True

df_1971.shape == (3, 4) and df_1971.seconds.max() == 8574
```

+++ {"tags": ["level_basic"]}

### l'édition de 1981 à Londres

```{code-cell} ipython3
# à vous

df_london_1981 = df[ (df["year"]==1981) & (df["city"] == "LONDON") ]
```

```{code-cell} ipython3
:tags: [raises-exception]

# ceci doit retourner True

df_london_1981.shape == (1, 4) and df_london_1981.iloc[0].seconds == 7908
```

### trouver toutes les villes

+++ {"tags": ["level_basic"]}

on veut construire une collection de toutes les villes qui apparaissent au moins une fois

```{code-cell} ipython3
# à vous

cities = df["city"].unique()
cities
```

intéressez-vous au type du résultat (dataframe, series, ndarray, liste ?)

+++

## des extraits

attention ici dans les consignes, les numéros de ligne **commencent à 1**

+++

### extrait #1

+++ {"tags": ["level_basic"]}

les entrées correspondant aux lignes 10 à 12 inclusivement

```{code-cell} ipython3
# à vous

df_10_to_12 = df.iloc[9:12]
```

```{code-cell} ipython3
:tags: [raises-exception]

# ceci doit retourner True

df_10_to_12.shape == (3, 4) and df_10_to_12.iloc[0].year == 2002 and df_10_to_12.iloc[-1].year == 2000
```

### extrait #2

+++ {"tags": ["level_basic"]}

une Series correspondant aux événements à Paris après 2000 (inclus), 
dans laquelle on n'a gardé que l'année

```{code-cell} ipython3
# à vous
s_paris_2000 = df[ (df["year"] >= 2000) & (df["city"] == "PARIS") ].year
```

```{code-cell} ipython3
s_paris_2000
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# ceci doit retourner True

isinstance(s_paris_2000, pd.Series) and len(s_paris_2000) == 12 and s_paris_2000.iloc[-1] == 2000
```

### extrait #3

+++ {"tags": ["level_basic"]}

une DataFrame correspondant aux événements à Paris après 2000, 
dans laquelle on n'a gardé que les deux colonnes `year` et `seconds`

```{code-cell} ipython3
df_paris_2000_ys = df[ (df["year"] >= 2000) & (df["city"] == "PARIS") ][["year", "seconds"]]
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# ceci doit retourner True

(isinstance(df_paris_2000_ys, pd.DataFrame)
 and df_paris_2000_ys.shape == (12, 2) 
 and df_paris_2000_ys.iloc[-2].seconds == 7780)
```

+++ {"slideshow": {"slide_type": ""}}

## aggrégats

+++

### moyenne

+++ {"tags": ["level_basic"]}

ce serait quoi la moyenne de la colonne `seconds` ?

```{code-cell} ipython3
# calculer la moyenne de la colonne 'seconds'

seconds_average = df.seconds.mean()
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# pour vérifier

import math
math.isclose(seconds_average, 7933.660167130919)
```

+++ {"slideshow": {"slide_type": ""}}

### combien de marathons par an

+++ {"tags": ["level_basic"], "slideshow": {"slide_type": ""}}

si maintenant je veux produire une série qui compte par année combien il y a eu de marathons

il y a plein de façons de faire, si vous en voyez plusieurs n'hésitez pas...

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
# à vous

count_by_year = df.year.value_counts()
count_by_year
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# pour vérifier

(isinstance(count_by_year, pd.Series)
 and len(count_by_year) == 65
 and count_by_year.loc[1947] == 1
 and count_by_year.loc[2007] == 9
 and count_by_year.loc[2011] == 5)
```

+++ {"slideshow": {"slide_type": ""}}

## les durées

+++ {"tags": ["level_intermediate"]}

dans cette partie, notre but est de simplement vérifier que la colonne `seconds` contient bien le nombre de secondes correspondant à la colonne `duration`

+++

pour cela on va commencer par convertir la colonne `duration` en quelque chose d'un peu plus utilisable

`numpy` expose deux types particulièrement bien adaptés à la gestion du temps

* `datetime64` pour modéliser un instant particulier
* `timedelta64` pour modéliser une durée entre deux instants

voir plus de détails si nécessaire ici: <https://numpy.org/doc/stable/reference/arrays.datetime.html>

+++ {"slideshow": {"slide_type": ""}}

### `read_csv(parse_dates=)`

+++ {"slideshow": {"slide_type": ""}}

commençons par écarter une fausse bonne idée

dans `read_csv` il y a une option `parse_dates`; mais regardez ce que ça donne

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
df_broken = pd.read_csv(
    DATA, sep='\t', 
    names=['city', 'year', 'duration', 'seconds'], 
    parse_dates=['duration'])
df_broken
```

+++ {"slideshow": {"slide_type": ""}}

**ça ne va pas !**

le truc c'est que ici, on n'a **pas une date**, ce que nous avons c'est **une durée**

+++ {"slideshow": {"slide_type": ""}}

### `pd.to_timedelta()`

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# repartons des données de départ

df = pd.read_csv(DATA, sep="\t", names=NAMES)

df.dtypes
```

+++ {"tags": ["level_basic"], "slideshow": {"slide_type": ""}}

non, pour convertir la colonne en `datetime64` on va utiliser `pd.to_timedelta()`

voyez la documentation de cette fonction, et modifiez la dataframe `df` pour que la colonne `duration` soit maintenant du type `timedelta64`

```{code-cell} ipython3
# à vous
df["duration"] = pd.to_timedelta(df["duration"])
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# pour vérifier - doit retourner True

df.duration.dtype == 'timedelta64[ns]'
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# et maintenant ça devrait être beaucoup mieux

df.head(2)
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
df.duration.dt.components
```

+++ {"slideshow": {"slide_type": ""}}

### duration == seconds ?

+++ {"slideshow": {"slide_type": ""}}

à présent qu'on a converti `duration` dans le bon type, on peut utiliser toutes les fonctions disponibles sur ce type.  
en pratique ça se fait en deux temps

* sur l'objet `Series` on applique l'attribut `dt` pour, en quelque sorte, se projeter dans l'espace des 'date-time'  
  c'est exactement comme on l'a vu déjà avec le `.str` lorsqu'on a eu besoin d'appliquer des méthodes comme `.lower()` ou `replace()` sur les chaines et non pas sur la série  
  plus de détails ici <https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.html>
* de là on peut appeler toutes les méthodes disponibles sur les objets `timedelta` - on pourra en particulier s'intéresser à `total_seconds`

+++ {"tags": ["level_basic"], "slideshow": {"slide_type": ""}}

du coup pour vérifier que la colonne `seconds` correspond bien à `duration`, on écrirait quoi comme code (qui doit afficher `True`)

```{code-cell} ipython3
# à vous
import numpy as np
def seconds(d, h, m, s) :
    return s + 60*(m + 60*(h + 24*d) )

secs = np.vectorize(seconds)
t = df.duration.dt.components
(df.seconds == secs(t.days, t.hours, t.minutes, t.seconds)).value_counts()
```

+++ {"slideshow": {"slide_type": ""}}

### colonnes `hour` `minute` et `second`

+++ {"tags": ["level_basic"], "slideshow": {"slide_type": ""}}

on se propose maintenant de rajouter des colonnes `hour` `minute` et `second` - qui doivent être de type entier

pour cela deux approches:

- "à la main": on fait les calculs nous-mêmes
- après quoi on découvre par hasard dans une question SO que c'est disponible directement dans la colonne `duration` - mais c'est bien caché...

+++ {"slideshow": {"slide_type": ""}}

#### à la main

**indices**

* on peut calculer le quotient et le reste entre deux objets de type "durée" avec les opérateurs usuels `//` et `%`

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
# par exemple
import numpy as np

# une durée de 1h
one_hour = np.timedelta64(1, 'h')

# guess what...
one_minute = np.timedelta64(1, 'm')
one_second = np.timedelta64(1, 's')

# une durée de 2h25
random_duration = 2*one_hour + np.timedelta64(25, 'm')


# eh bien on peut faire comme avec des entiers

quotient, reste = random_duration // one_hour, random_duration % one_hour

quotient, reste
```

+++ {"slideshow": {"slide_type": ""}, "tags": ["level_basic"]}

maintenant qu'on sait faire tout ça, on peut calculer les colonnes `hour`, `minute` et `second`

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
# à vous
df["hour"], r = df.duration // one_hour, df.duration % one_hour
df["minute"], r = r // one_minute, (r % one_minute)
df["second"] = r // one_second
df.head()
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# pour vérifier
(    np.all(df.loc[0, ['hour', 'minute', 'second']] == [2, 6, 29])
 and df.hour.dtype == int
 and df.minute.dtype == int 
 and df.second.dtype == int)
```

+++ {"slideshow": {"slide_type": ""}}

#### version paresseuse avec `dt.components`

il se trouve qu'on peut faire le même travail sans s'embêter autant, une fois qu'on découvre que [l'accesseur `.dt` possède un attribut qui donne accès à ce genre de détails ](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.dt.components.html)

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
# on défait le travail de la section précédente, si nécessaire

for col in 'hour', 'minute', 'second':
    if col in df.columns:
        df.drop(columns=col, inplace=True)
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
---
# à vous
df[["hour", "minute", "second"]] = df.duration.dt.components[["hours", "minutes", "seconds"]]
df.head()
```

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# pour vérifier
(    np.all(df.loc[0, ['hour', 'minute', 'second']] == [2, 6, 29])
 and df.hour.dtype == int
 and df.minute.dtype == int 
 and df.second.dtype == int)
```

```{code-cell} ipython3

```
