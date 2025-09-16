---
execution:
  allow_errors: true
jupytext:
  encoding: '# -*- coding: utf-8 -*-'
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
language_info:
  name: python
  nbconvert_exporter: python
  pygments_lexer: ipython3
nbhosting:
  title: TP - un peu de musique
---

+++ {"slideshow": {"slide_type": ""}, "tags": []}

Licence CC BY-NC-ND, Valérie Roy & Thierry Parmentelat

+++

# TP - un peu de musique

+++

## avertissement

+++

pour le confort de chacun, veuillez vous assurer avant de commencer que le volume de votre haut parleur est réglé au minimum audible pour vous :)

+++

## imports

```{code-cell} ipython3
import numpy as np
```

```{code-cell} ipython3
import matplotlib.pyplot as plt

# en mode interactif ça peut être utile de choisir un mode interactif
# comme par exemple celui-ci
# par contre ça nécessite de faire un `pip install ipympl`
# %matplotlib ipympl
```

````{admonition} à quoi ça sert ?
Grâce au mode de rendu dit *"ipympl"*, on a plus de possibilités d'interaction avec la figure  
pour zoomer (icône carrée), déplacer (les deux flêches croisées), revenir au point de vue de départ (la maison)..
````

```{code-cell} ipython3
# pour jouer le son qu'on va produire
from IPython.display import Audio
```

## nature du son

+++

comme vous le savez sans doute, lorsqu'on enregistre un morceau de musique, on capture la position de la membrane du microphone au cours du temps

puisqu'il s'agit de son, la membrane oscille autour de sa position d'équilibre, dans un mouvement pseudo-périodique, et la fréquence à un moment donné détermine la *hauteur* du son qu'on entend

ainsi la fréquence de 440Hz a été définie comme étant la fréquence du LA (enfin pour être précis, d'*un* LA, on y reviendra)

+++

## comment on capture du son

+++

une technique pour enregistrer le son consiste à simplement capturer la position de la membrane **à intervalles réguliers** : on appelle cela l'**échantillonnage**, qui produit en sortie une collection de valeurs numériques

les fréquences audibles sont comprises, disons, pour être très large, entre 20 Hz et 20 kHz  
du coup pour ne pas perdre en précision, on échantillonne traditionnellement à une fréquence de 44.1 kHz (chiffre qui date de l'époque des CD)

ce qui signifie que si on produit un tableau de 44100 valeurs qui représentent une sinusoïde parfaite, on pourra jouer cela comme un son de 1s et sur une note continue; ce sera notre premier exercice

```{code-cell} ipython3
RATE = 44_100
LA = 440
```

## synthétiseur - fréquence

+++

reste à déterminer l'amplitude, pour l'instant on prend une amplitude de 1

+++

imaginons que nous voulions produire un son correspondant à un LA à 440 Hz, sur une seconde:
  1. nous devons donc calculer un tableau qui fait combien d'entrées ?
  1. quelle est en fonction du temps, et donc sur l'intervalle $[0, 1]$,  
     l'équation de la fonction qui nous intéresse ?
  1. comment on peut s'y prendre pour calculer ce tableau ?

+++

````{tip}
:class: dropdown

la fonction qui donne la position de la membrane en fonction du temps est, si $\phi$ représente la fréquence du son

$$ 
f: [0, 1] \rightarrow [0, 1] \\
  f(t) = sin(2\pi\phi t)
$$
````

```{code-cell} ipython3
# bien sûr ce n'est pas comme ça qu'il faut faire
# mais pour que la suite soit vaguement cohérente 
# et que l'énoncé ne contienne pas des milliers d'erreurs...

t = np.linspace(0,1, RATE+1)
```

```{code-cell} ipython3
# votre code
DO = 520
la_1seconde = np.sin(2*np.pi*LA*t)
```

***
***

```{code-cell} ipython3
---
slideshow:
  slide_type: ''
tags: [raises-exception]
---
# pour écouter le résultat
# remarquez qu'on a maintenant perdu la fréquence d'échantillonnage
# il faut repasser cette information au lecteur de musique

Audio(la_1seconde, rate=RATE)
```

**commodité**

comme on ne va produire que des sons échantillonnés à 44.100 Hz, ce sera plus commode de ne pas avoir à le répéter à chaque fois

```{code-cell} ipython3
def MyAudio(what, **kwds):
    return Audio(what, rate=RATE, **kwds)
```

```{code-cell} ipython3
---
cell_style: split
slideshow:
  slide_type: ''
tags: [raises-exception]
---
MyAudio(la_1seconde)
```

```{code-cell} ipython3
---
cell_style: split
slideshow:
  slide_type: ''
tags: [raises-exception]
---
MyAudio(la_1seconde, autoplay=True)
```

### on en fait une fonction

+++

pour généraliser un petit peu, on va écrire une fonction  
qui produit un son sinusoïdal, et qui prend en paramètres  
la fréquence et la durée

````{tip}
:class: dropdown

commencez par vous demander combien d'échantillons on doit produire
````

```{code-cell} ipython3
# pareil ici: je donne une implémentation folklorique
# pour ne pas avoir plein d'erreurs dans l'énoncé

#def sine(freq, duration=1, amplitude=1.):
#    return la_1seconde
```

```{code-cell} ipython3
# votre code

def sine(freq, duration=1, amplitude=1.):
    t = np.linspace(0, duration, int(duration*RATE) + 1)
    return amplitude * np.sin(2*np.pi * freq * t)
```

```{code-cell} ipython3
# pour écouter: plus court

MyAudio(sine(LA, .5), autoplay=True)
```

```{code-cell} ipython3
# pour écouter: plus long

MyAudio(sine(LA, 1.5), autoplay=True)
```

+++ {"tags": ["level_intermediate"]}

### pour les rapides

on veut obtenir un effet de 'note qui monte'

améliorer un peu pour générer une courbe avec un fréquence qui croit (ou décroit) linéairement avec le temps

écrire une fonction `sine_linear(freq1, freq2, duration)`

```{code-cell} ipython3
:tags: [level_intermediate]

# votre code
def sine_linear(freq1, freq2, duration):
    slide_freq = np.linspace(freq1, freq2, int(duration*RATE) + 1)
    t = np.linspace(0, duration, int(duration*RATE) + 1)
    return np.sin(2*np.pi * slide_freq * t)
```

```{code-cell} ipython3
:tags: [level_intermediate]

# pour écouter
MyAudio(sine_linear(440, 660, 3), autoplay=True)
```

## réglage du volume

+++

### crescendo

+++

imaginons qu'on veuille produire un son de plus en plus fort  
par exemple qui monte crescendo de manière linéaire  
sur toute la durée du son

1. comment on pourrait faire ça ?

```{code-cell} ipython3
# votre code pour 1.

crescendo_la_1seconde = t*la_1seconde
```

```{code-cell} ipython3
# pour écouter
MyAudio(crescendo_la_1seconde, autoplay=True)
```

2. en faire une fonction

   ```python
   def crescendo_sine(freq, duration):
        ...
   ```

```{code-cell} ipython3
# votre code pour 2.
def crescendo_sine(freq, duration):
    t = np.linspace(0, duration, int(duration*RATE) + 1)
    return (t/duration) * np.sin(2*np.pi * freq * t)
```

```{code-cell} ipython3
# pour écouter
MyAudio(crescendo_sine(LA, 2), autoplay=True)
```

3. ajouter un paramètre pour pouvoir décroître
   ```python
   def crescendo_sine(freq, duration, increase=True):
        ...
   ```

```{code-cell} ipython3
# votre code pour 3.
def crescendo_sine(freq, duration, increase=True):
    t = np.linspace(0, duration, int(duration*RATE) + 1)
    return (t/duration) * np.sin(2*np.pi * freq * t) if increase else (1 - t/duration) * np.sin(2*np.pi * freq * t)
```

```{code-cell} ipython3
# pour écouter

MyAudio(crescendo_sine(LA, 2, increase=False)) #, autoplay=True)
```

4. avancés:
   est-ce qu'on ne pourrait pas faire un choix un peu plus malin ?

````{tip}
on vient de faire le crescendo pour un son sinusoïdal  
mais ça pourrait s'appliquer à plein d'autres sons, comment faire pour n'écrire ce code qu'une seule fois ?
````

```{code-cell} ipython3
# votre code pour 4.
def crescendo(sound, duration, increase=True):
    return (t/duration) * sound if increase else (1 - t/duration) * sound
```

## concaténation

+++

on sait maintenant produire des notes élémentaires

sachant que la note DO immédiatement au dessus du la-440 a une fréquence de l'ordre de 523 Hz, comment pourrait-on maintenant produire une succession de deux notes la et do ?

```{code-cell} ipython3
# la fréquence du DO
DO = 523.25
```

```{code-cell} ipython3
# votre code
la_do = np.concatenate((sine(LA), sine(DO)))
```

```{code-cell} ipython3
# pour écouter

MyAudio(la_do, autoplay=True)
```

## amplitude et types

+++

jusqu'ici, chaque échantillon est représenté par un **nombre flottant** entre -1 et 1

il se trouve que ça n'est pas forcément le plus pertinent comme approche, notamment lorsqu'il va s'agir de sauver notre son sur fichier

aussi nous allons maintenant nous poser la question de changer d'échelle - et de type de données - pour utiliser plutôt des **entiers 16 bits** (que pour rappel on a à notre disposition avec `numpy.int16`)

+++

### entiers signés ou non

ce qui nous amène à une petite digression: profitons-en pour regarder un peu comment sont encodés les entiers;

l'encodage des **entiers signés** fonctionne comme suit; on regarde ici les types `int8` et `uint8` car c'est plus simple, le principe est exactement le même pour des tailles plus grandes

il y a deux types d'encodages pour les entiers, **signés** (`int8`) et **non signés** (`uint8`, le `u` signifie *unsigned*)

les entiers **non signés** sont simples à encoder, avec 8 bits on peut aller de 0 à 255

par contre pour les entiers **signés**, on va devoir utiliser **un bit comme bit de signe**, ce qui limite le spectre de ce qu'il est possible d'encoder; avec en tout 8 bits on peut encoder de -128 à 127 inclus.

+++

| entier |    int8    |     uint8    |
|--------|------------|--------------|
| -128   | `10000000` | n/a |
| -127   | `10000001` | n/a |
| -126   | `10000010` | n/a |
| ...    |
| -003   | `11111101` | n/a |
| -002   | `11111110` | n/a |
| -001   | `11111111` | n/a |
| ------- |
| 000    | `00000000` | `00000000` (idem) |
| 001    | `00000001` | `00000001` (idem) |
| 002    | `00000010` | `00000010` (idem) |
| ...    |
| 125    | `01111101` | `01111101` (idem) |
| 126    | `01111110` | `01111110` (idem) |
| 127    | `01111111` | `01111111` (idem) |
| ------- |
| 128    | n/a | `10000000` |
| 129    | n/a | `10000001` |
| 130    | n/a | `10000011` |
| ...    |
| 253    | n/a | `11111101` |
| 254    | n/a | `11111110` |
| 255    | n/a | `11111111` |

+++

du coup avec le type `int16` on va pouvoir encoder l'intervalle [-32768, 32767]

```{code-cell} ipython3
2**15
```

ça veut dire que si on sort de cet intervalle on va avoir des surprises

+++

````{admonition} signé ou pas signé ?

pour coder le son, faut-il utiliser des entiers signés ou non signés ?
* fabriquez un tableau de -5 à 5 comme des entiers 16 bits non signés
* fabriquez un tableau contenant les entiers de 32764 à 32771 comme des entiers 16 bits signés
* que constatez-vous
* qu'est-ce que cela signifie pour la génération de son ?

```{note}
d'ailleurs il semble qu'avec les versions futures de numpy, ce genre de manipes tordues provoquera une exception...
```
````

```{code-cell} ipython3
# à vous

# t1 = np.arange(-5, 5, dtype=np.uint16) -> renvoie une erreur

# t2 = np.arange(32764, 32771, dtype=np.int16) -> ne renvoie pas d'erreur, mais passage dans les négatifs après 32767
```

### mise à l'échelle

+++

**exercice**

en vous souvenant qu'on a à notre disposition la méthode `array.astype()`  
pour fabriquer une copie d'un tableau numpy convertie dans un autre type,

écrivez une fonction qui transforme  
notre tableau de flottants dans [-1, 1].
en un tableau d'**entiers signés 16bits**

et pour préserver le niveau sonore, il faut que les entrés maximales  
i.e. 1 ou -1 dans le 1er format  
correspondent au maximum codable dans le second format

le son produit doit être totalement identique - le volume notamment

```{code-cell} ipython3
# votre code
def float_to_int16(as_float):
    l = as_float.shape - 1 // 2
    
```

```{code-cell} ipython3
:cell_style: split

# pour écouter
MyAudio(float_to_int16(la_do), autoplay=True)
```

```{code-cell} ipython3
:cell_style: split

# sans conversion
MyAudio(la_do, autoplay=True)
```

+++ {"jp-MarkdownHeadingCollapsed": true}

## fréquences des notes de la gamme

+++

dans cette partie, nous allons calculer les fréquences des notes

pour les non-musiciens, sachez que, pour simplifier :

+++

### gamme chromatique

la gamme chromatique (toutes les notes du piano) contient 12 notes  
$do$ ・ $do\sharp$ ・ $ré$ ・ $ré\sharp$ ・ $mi$ ・ $fa$ ・ $fa\sharp$ ・ $sol$ ・ $sol\sharp$ ・ $la$ ・ $la\sharp$ ・ $si$  
séparées de 1/2 ton  
(le $la\sharp$ s'appelle aussi $si\flat$ mais c'est une autre histoire...)

et si on rajoute la note suivante (qu'on appelle $do'$), cela fait 13 notes donc 12 intervalles

+++

### intervalles

notre oreille reconnait bien les **intervalles** entre deux notes  
par exemple si vous jouez les deux extraits ci-dessous  
vous allez reconnaitre dans les deux cas le pin-pon des pompiers

```{code-cell} ipython3
:cell_style: split

Audio(filename='media/pin-pon-la-si.wav')
```

```{code-cell} ipython3
:cell_style: split

Audio(filename='media/pin-pon-fa-sol.wav')
```

ici dans les deux cas, les deux notes utilisées (la - si, puis fa - sol)  
sont dans les deux cas séparées de 2 crans dans la gamme chromatique  
(on dit que les deux notes constituent un *intervalle* de 2 demi-tons, soit un ton)  
et comme c'est le **même intervalle**, notre oreille entend dans les deux cas la même "mélodie"

+++

### un intervalle = un rapport entre fréquences

enfin, il faut savoir que ce qui caractérise un intervalle,
c'est le **rapport** entre les fréquences des deux notes

ainsi par exemple, vous pouvez constater que si on multiplie une fréquence par 2

```{code-cell} ipython3
:cell_style: center

# une octave de LA
MyAudio(
    np.concatenate((sine(LA, 0.5),
                    sine(2*LA, 0.5))),
    autoplay=True)
```

on entend une note qui ressemble beaucoup à la premiére  
en réalité, le fait de **multiplier la fréquence par 2**  
permet d'obtenir une note **une octave** au dessus  
(c'est-à-dire de passer d'un DO au DO au dessus)

```{code-cell} ipython3
:cell_style: center

# même effet avec le DO naturellement
MyAudio(
    np.concatenate((sine(DO, 0.5),
                    sine(2*DO, 0.5))),
    autoplay=True)
```

### calculons les fréquences des notes

+++

on a toutes les informations à ce stade pour calculer  
les fréquences des notes de la gamme (dite *bien tempérée*)

en effet on sait que, puisque c'est toujours le même intervalle,  
un demi-ton correspond à un rapport constant entre les (fréquences des) notes  
qu'on va appeler $\alpha$

$$
\frac{do\sharp}{do} =
\frac{ré}{do\sharp} =
\ldots
\frac{si}{la\sharp} =
\frac{do'}{si} = \alpha
$$

+++ {"cell_style": "center"}

et comme par ailleurs on sait qu'entre les deux *do* il y a une octave 
donc $
\frac{do'}{do} = 2
$

mais c'est aussi
$
\frac{do'}{do} = \frac{do'}{si}.\frac{si}{la\sharp}.\frac{la\sharp}{la}...\frac{ré}{do\sharp}.\frac{do\sharp}{do} = \alpha^{12}
$

d'où il ressort que $\alpha^{12} = 2$

+++ {"cell_style": "split"}

**exercices**

1. calculer - sans boucle for - un tableau contenant  
   les 13 - de *do* à *do'* inclus -  
   rapports entre do et les notes de la gamme  
   (`ratios[0]` devrait valoir 1, et `ratios[12]` devrait valoir 2)

+++ {"cell_style": "split"}

$$
\begin{array}{cccc}
00 & 1 & 2^0 & do\\
1 & \sqrt[^{12}]{2} & 2^{1/12} & do\sharp\\
2 & (\sqrt[^{12}]{2})^2 & 2^{2/12} & ré\\
...\\
11 & (\sqrt[^{12}]{2})^{11} & 2^{11/12} & la\sharp\\
12 & 2 & 2^{12/12} & do'\\
\end{array}
$$

+++

2. on a besoin d'une fonction qui calcule la fréquence  
   d'une note à partir de son nom  
   on veut bien sûr que $la \rightarrow 440$

```{code-cell} ipython3
scale = ['do', 'do#', 'ré', 'ré#', 'mi', 'fa', 'fa#', 'sol', 'sol#', 'la', 'la#', 'si']
```

```{code-cell} ipython3
# votre code
def freq_from_name(name):
    ...
```

```{code-cell} ipython3
:cell_style: center

# pour vérifier: devrait retourner 
# ou presque (rappelez-vous les erreurs d'arrondi avec les flottants)

freq_from_name('la')
```

```{code-cell} ipython3
:cell_style: split

# attention à la précision !
freq_from_name('la') == 440
```

```{code-cell} ipython3
:tags: [framed_cell]

# question: on fait comment déjà pour comparer deux flottants ?
# à vous
```

+++ {"cell_style": "split"}

```{tip}
:class: dropdown

pensez à utiliser ceci `np.isclose(freq_from_name('la'), 440)`
```

+++ {"jp-MarkdownHeadingCollapsed": true}

## rationnels approchants

+++

pour comprendre les harmonies, ce qui intéressant  
c'est que parmi les ratios qu'on a calculés plus haut,  
certains sont **très proches** de rapports **rationnels simples**

````{note}
il n'y a pas d'exercice dans cette section, juste un exemple de visualisation
````

```{code-cell} ipython3
:cell_style: split

# intervalle do-mi (tierce majeure) ~= 5/4
ratios[4]
```

```{code-cell} ipython3
:cell_style: split

# intervalle do-sol (quinte) ~= 3/2
ratios[7]
```

### visuel (1)

+++ {"cell_style": "center"}

pour visualiser les ratios de la gamme

(uniquement des exemples d'utilisation de matplotlib)

```{code-cell} ipython3
:cell_style: center

plt.figure(figsize=(2, 6))

# on veut afficher 12 points de coordonnées
# tous avec une coordonnée X=0
X = np.zeros(ratios.shape)

# et pour marqueur un petit trait horizontal
plt.scatter(X, ratios, marker=0, linewidth=0.5);
```

### visuel (2)

+++

pareil, mais en superposant les rationnels $\frac{3}{2}$, $\frac{5}{4}$ et $\frac{4}{3}$

```{code-cell} ipython3
:scrolled: true

# on remarque quelques rapports proches
specials = np.array([1, 5/4, 4/3, 3/2, 2])
```

```{code-cell} ipython3
:cell_style: split

# pour dessiner des traits un peu plus beaux
# où on contrôle la taille et l'épaisseur

def strike(height, width, color, linewidth):
    plt.plot([-width, width], [height, height],
             color=color, linewidth=linewidth)

def turn_off_xticks():
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off
```

```{code-cell} ipython3
:cell_style: split

# on crée une figure
plt.figure(figsize=(2, 6))
# on enlève les marques sur l'axe des X
turn_off_xticks()
# on dessine les notes de la gamme en orange
for ratio in ratios:
    strike(ratio, 0.1, 'orange', 0.5)
# et les quelques rapports qu'on a remarqués à l'oeil nu
for special in specials:
    strike(special, 0.2, 'blue', 0.2)
```

+++ {"jp-MarkdownHeadingCollapsed": true}

## superposer deux sons

+++

comment faire pour jouer plusieurs sons en même temps ?

```{code-cell} ipython3
do = sine(freq_from_name('do'), 2)
mi = sine(freq_from_name('mi'), 2)
sol = sine(freq_from_name('sol'), 2)
```

```{code-cell} ipython3
# votre code
accord_do_mi_sol = ...
```

```{code-cell} ipython3
# pour écouter

MyAudio(accord_do_mi_sol, autoplay=True)
```

+++ {"jp-MarkdownHeadingCollapsed": true}

## sauver un son dans un `.wav`

+++

on peut facilement sauver nos sons  
grâce à la librairie `scipy`  
par contre il faut savoir que le **format le plus robuste**  
est celui qui utilise les **entiers 16 bits** qu'on a vus plus haut

```{code-cell} ipython3
from scipy.io import wavfile
```

**exercice**

1. chercher dans la documentation comment sauver un son dans un fichier `.wav`
1. sauver un de vos morceaux (par exemple `la_do`)
1. relisez-le
1. assurez-vous que le résultat est conforme au morceau de départ

```{code-cell} ipython3
:tags: [raises-exception]

# votre code
original = la_do # par exemple
#
# sauver le son 'before' dans un fichier 'sample.wav'
#
restored = ... # relisez le fichier 'sample.wav' dans une variable 'after'
```

```{code-cell} ipython3
:cell_style: split
:tags: [raises-exception]

# pour vérifier

MyAudio(original)
```

```{code-cell} ipython3
:cell_style: split

# pour vérifier

MyAudio(restored)
```

+++ {"jp-MarkdownHeadingCollapsed": true}

## un vrai son

+++

on part d'un petit fichier `media/sounds-cello.wav`

+++

<audio controls src="media/sounds-cello.wav" style="width:100%">

+++

**exercice**

1. lire le fichier (ranger le signal dans une variable `data`)
   (voyez `wavfile.read`)

```{code-cell} ipython3
# votre code
```

2. écoutez le

```{code-cell} ipython3
# votre code
```

3. afficher le samplerate utilisé dans le fichier

```{code-cell} ipython3
# votre code
```

4. afficher le nombre d'échantillons

```{code-cell} ipython3
# votre code
```

5. afficher la longueur du morceau en secondes

```{code-cell} ipython3
# votre code
```

### à quoi ça ressemble

+++ {"tags": ["licence"]}

on va utiliser matplotlib pour afficher le signal

affichez le signal du morceau (la position de la membrane) en fonction du temps à l'aide de la fonction `plt.plot()`

````{tip}
* c'est important d'avoir un rendu interactif (souvenez vous de `%matplotlib`)
* pour pouvoir zoomer dans le diagramme
* notamment utiles: pour zoomer (icône carrée), déplacer (les deux flêches croisées), revenir au point de vue de départ (la maison)..
````

+++ {"jp-MarkdownHeadingCollapsed": true}

## effet d'echo

+++

maintenant on veut ajouter un effet d'echo  

il nous faut pour cela

* créer une version du son initial, mais décalée dans le temps  
* et ajouter les deux

sauf que si on s'y prend comme cela:

* les deux signaux apparaissent avec le même niveau sonore  
  or un effet d'echo sous-entend une atténuation du signal tardif
* en plus avec le type `int16`, on risque de causer des erreurs de débordement  
  en effet si au même instant les deux signaux contiennent tous deux  
  une valeur >= 20_000, la somme va dépasser $2^{15}$ et donc provoquer  
  une conversion et donc une erreur

+++ {"tags": ["level_advanced"]}

```{image} media/sounds-offsets.png
:align: center
```

c'est ce qu'on essaie d'illustrer ici

* le signal de départ (en vert)
* est décalé vers la droite de la valeur du retard
* et on applique à chacun une pondération  
  par exemple 70% pour le signal de départ,
  et 30% pour le signal retardé
* avant de les ajouter

```{code-cell} ipython3
# quelques constantes

# en seconde
delay = 2

# les deux ratios
main_ratio, delayed_ratio = 0.7, 0.3
```

**exercice** v1

1. traduire `delay` en nombre d'échantillons `offset`
1. produire le son avec echo,
   sur une durée correspondant au son de départ

```{code-cell} ipython3
# votre code pour produire
# le son de 'data' avec echo
data_echoed = ...
```

```{code-cell} ipython3
# pour écouter

MyAudio(data_echoed)
```

```{code-cell} ipython3
:scrolled: true

# pour observer

plt.figure(figsize=(12, 4))
plt.plot(data_echoed, linewidth=0.05);
```

**exercice** v2

1. idem mais pour produire une durée un peu plus longue, correspondant à la somme

  * de la durée du son de départ
  * et du retard

```{code-cell} ipython3
# votre code

data_echoed_v2 = ...
```

```{code-cell} ipython3
# pour écouter
MyAudio(data_echoed_v2)
```

```{code-cell} ipython3
:scrolled: true

# pour observer

plt.figure(figsize=(10, 4))
plt.plot(data_echoed_v2, linewidth=0.05);
```

+++ {"jp-MarkdownHeadingCollapsed": true}

## transposer

+++

### transposer d'une octave

+++

on a vu qu'une octave correspond à une fréquence deux fois plus élevée

partant de par exemple `data`, comment produire un son une octave au dessus ?  
(on s'astreint à ne pas modifier le samplerate)

+++

***
***
***
***
***
***
je vous laisse y réfléchir un moment...
***
***
***
***
***
***

+++

pour élever d'une octave, il suffit d'ignorer un échantillon sur deux

pourquoi ? de cette façon on va artificiellement

* diminuer la durée par 2 (2 fois moins d'échantillons, toujours à la même fréquence d'échantillonage de 44.100 Hz)
* et du coup multiplier par 2 la fréquence des sons perçus

+++

```{image} media/sounds-sample-2-1.png
:align: center
```

+++

**exercice**

fabriquer un son qui soit similaire à celui dans `data`, mais une octave au dessus

```{code-cell} ipython3
# votre code ici

data2 = ...
```

```{code-cell} ipython3
:cell_style: split

# pour écouter

MyAudio(data)
```

```{code-cell} ipython3
:cell_style: split

# pour écouter

MyAudio(data2)
```

naturellement le profil reste le même mais l'échelle des X est plus courte (deux fois moins d'échantillons)

```{code-cell} ipython3
plt.figure(figsize=(10, 4))
plt.plot(data2, linewidth=0.05);
```

### transposer d'une quinte

+++

pour transposer d'une quinte, il nous faut multiplier la fréquence par 3/2; on peut utiliser une approche voisine

```{image} media/sounds-sample-3-2.png
:align: center
```

+++

sauf que cette fois, il faut un peu interpoler; on est donc amené à faire des moyennes comme ceci

```
data         data3  
0    0       0
1    1+2/2   1
2    --
3    3       2
4    4+5/2   3
5    --
...
```

+++

**exercice** appliquez l'idée ci-dessus :

1. créez un tableau `data3` dont la taille est 2/3 de celle de `data`
1. remplir dans `data3` les données de rang pair  
   qui correspondent aux multiples de 3 dans le tableau de départ
1. remplir dans `data3` les données de rang impair  
   en implémentant l'interpolation

**remarque**: nos data sont en `int16`, on va s'efforcer
de continuer à travailler dans ce format

```{code-cell} ipython3
# votre code
data3 = ...
```

```{code-cell} ipython3
# vérification de visu
# ces deux segments correspondent normalement
# au même instant dans le morceau

data[12000:12007], data3[8000:8005]
```

```{code-cell} ipython3
# pour écouter
MyAudio(data3)
```

+++ {"tags": ["level_intermediate"]}

## la fraction la plus proche (avancés - sans exercice)

+++ {"tags": ["level_intermediate"]}

on peut s'amuser à calculer, pour chaque note, la fraction la plus proche - si on se restreint à des rationnels avec un dénominateur "petit"

+++ {"tags": ["level_intermediate"]}

pour ça on se fixe par exemple N=7 et pour chaque note x, on veut minimiser abs(x-r) pour r étant dans l'espace
$$r\in\{1 + p/q, q<=N, 0<=p<=q\}$$

+++ {"tags": ["level_intermediate"]}

si on voulait faire ça en Python pur, on pourrait écrire quelque chose comme

```{code-cell} ipython3
:tags: [level_intermediate]

from fractions import Fraction
```

```{code-cell} ipython3
:tags: [level_intermediate]

N = 7

# tous les rationnels concernés dans [1, 2[
rationals = {1 + Fraction(p, q) for q in range(1, N+1) for p in range(q+1)}
rationals
```

```{code-cell} ipython3
:tags: [level_intermediate]

# la version la plus rapide à écrire
def closest1(note):
    return min(abs((note-rational)/rational) for rational in rationals)
```

```{code-cell} ipython3
:tags: [level_intermediate]

# mais le souci c'est qu'on a perdu de l'information
tierce, quinte = ratios[4], ratios[7]
closest1(quinte)
```

```{code-cell} ipython3
:tags: [level_intermediate]

# du coup ça se complique un peu

def closest2(note):
    minimum = np.inf
    result = None
    for rational in rationals:
        if abs(note-rational) < minimum:
            minimum = abs(note-rational)/note
            result = rational
    return result, minimum
```

```{code-cell} ipython3
:tags: [level_intermediate]

closest2(quinte)
```

```{code-cell} ipython3
:tags: [level_intermediate]

# encore une autre version

def closest(note):
    """
    on retourne le rationnel le plus proche
    avec l'erreur relative que ça représente

    sous la forme d'un tuple
    (rationnel, erreur relative)
    """
    # on va trier une liste de tuples (rational, relative_error)
    # c'est sous-optimal d'un point de vue algorithmique
    # car on n'a pas vraiment besoin de trier toute la liste
    # dans ces ordres de grandeur ça n'a pas bcp d'importance
    # par contre ça donne un code un peu plus intéressant
    candidates = [(rational, abs(note-rational)/note) for rational in rationals]

    return sorted(candidates, key=lambda couple: couple[1])[0]
```

```{code-cell} ipython3
:tags: [level_intermediate]

closest(quinte)
```

+++ {"tags": ["level_intermediate"]}

### les accords harmonieux

+++ {"tags": ["level_intermediate"]}

si on ne garde que les notes qui sont très proches - avec une erreur relative de moins de 0.5%  
on trouve les intervalles do-fa et do-sol

```{code-cell} ipython3

```
