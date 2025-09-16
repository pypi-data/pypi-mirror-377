---
jupytext:
  cell_metadata_json: true
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
  title: TP simple avec des images
---

Licence CC BY-NC-ND, Valérie Roy & Thierry Parmentelat

+++

# TP images (1/2)

merci à Wikipedia et à stackoverflow

**vous n'allez pas faire ici de traitement d'image  
on se sert d'images pour égayer des exercices avec `numpy`  
(et parce que quand on se trompe: on le voit)**

+++

**Notions intervenant dans ce TP**

* création, indexation, slicing, modification  de `numpy.ndarray`
* affichage d'image (RBG, RGB-A, niveaux de gris)
* lecture de fichier `jpg`
* les autres notions utilisées sont rappelées (très succinctement)

**N'oubliez pas d'utiliser le help en cas de problème.**

+++

## import des librairies

+++

1. Importez la librairie `numpy`

1. Importez la librairie `matplotlib.pyplot`  
ou toute autre librairie d'affichage que vous aimez et/ou savez utiliser `seaborn`...

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt
```

2. optionnel - changez la taille par défaut des figures matplotlib
   par exemple choisissez d'afficher les figures dans un carré de 4x4 (en théorie ce sont des inches)

````{tip}
il y a plein de façons de le faire, google et/ou stackoverflow sont vos amis...
````

+++

## création d'une image de couleur

+++

**Rappels (rapides)**

* dans une image en couleur, les pixels sont représentés par leurs *dosages* dans les 3 couleurs primaires: `red`, `green`, `blue` (RGB)  
* si le pixel vaut `(r, g, b) = (255, 0, 0)`, il ne contient que de l'information rouge, il est affiché comme du rouge
* l'affichage à l'écran, d'une image couleur `rgb`, utilise les règles de la synthèse additive  
`(r, g, b) = (255, 255, 255)` donne la couleur blanche  
`(r, g, b) = (0, 0, 0)` donne la couleur noire  
`(r, g, b) = (255, 255, 0)` donne la couleur jaune ...

```{image} media/synthese-additive.png
:width: 200px
:align:center
```

* pour afficher le tableau `im` comme une image, utilisez: `plt.imshow(im)`
* pour afficher plusieurs images dans une même cellule de notebook faire `plt.show()` après chaque `plt.imshow(...)`

+++

**Exercices**

1. Créez un tableau blanc, de 91 pixels de côté, d'entiers non-signés 8 bits et affichez-le  
   indices:  
   . le tableau n'est pas forcément initialisé à ce stade  
   . il vous faut pouvoir stocker 3 uint8 par pixel pour ranger les 3 couleurs

```{code-cell} ipython3
# votre code
img = np.zeros((91,91,3), dtype=np.uint8)
img[:] = 255
plt.imshow(img)
```

2. Transformez le en tableau noir (en un seul slicing) et affichez-le

```{code-cell} ipython3
img[:] = 0
plt.imshow(img)
```

3. Transformez le en tableau jaune (en un seul slicing) et affichez-le

```{code-cell} ipython3
img[:,:] = np.array([255,255,0])
plt.imshow(img)
```

4. Affichez les valeurs RGB du premier pixel de l'image, et du dernier

```{code-cell} ipython3
print(img[0,0], img[-1,-1])
```

5. Faites un quadrillage d'une ligne bleue, toutes les 10 lignes et colonnes et affichez-le

```{code-cell} ipython3
for x in range(0,len(img), 10):
    for y in range(0,len(img)):
        img[x,y] = [0,255,255]
        img[y,x] = [0,255,255]

#ou alors
img[::10, :, :] = [0,0,255]
img[:, ::10, :] = [0,0,255]
plt.imshow(img)
```

## lecture d'une image en couleur

+++

1. Avec la fonction `plt.imread` lisez le fichier `data/les-mines.jpg`  
ou toute autre image - *faites juste attention à la taille*

```{code-cell} ipython3
imarray = plt.imread("data/les-mines.jpg")
```

2. Vérifiez si l'objet est modifiable avec `im.flags.writeable`  
si il ne l'est pas copiez-le

```{code-cell} ipython3
im.flags.writeable
```

3. Affichez l'image

```{code-cell} ipython3
plt.imshow(imarray)
```

4. Quel est le type de l'objet créé ?

```{code-cell} ipython3
type(_)
```

5. Quelle est la dimension de l'image ?
6. Quelle est la taille de l'image en hauteur et largeur ?

```{code-cell} ipython3
np.shape(imarray)
```

7. Quel est le nombre d'octets utilisé par pixel ?
8. Quel est le type des pixels ?  
(deux types pour les pixels: entiers non-signés 8 bits ou flottants sur 64 bits)

```{code-cell} ipython3
# 1 octet par canal et par pixel, donc 3 octets pour chaque pixel

imarray.dtype
```

9. Quelles sont ses valeurs maximale et minimale des pixels ?

```{code-cell} ipython3
# votre code

print(np.max(imarray))
print(np.min(imarray))
```

10. Affichez le rectangle de 10 x 10 pixels en haut de l'image

```{code-cell} ipython3
# votre code
tmp = imarray[:10,:10,:]
plt.imshow(tmp)
```

## accès à des parties d'image

+++

1. Relire l'image

```{code-cell} ipython3
# votre code

plt.imshow(imarray)
```

2. Slicer et afficher l'image en ne gardant qu'une ligne et qu'une colonne sur 2, 5, 10 et 20  
(ne dupliquez pas le code)

**[indices]**
* vous pouvez créer plusieurs figures depuis une seule cellule
* vous pouvez ensuite choisir de 'replier' ou non la zone *output* en hauteur;  
  c'est-à-dire d'afficher soit toute la hauteur, soit une zone de taille fixe avec une scrollbar pour naviguer  
  pour cela cliquez dans la marge gauche de la zone *output*

```{code-cell} ipython3
# votre code

imarray_1sur2 = imarray[::2,::2,:]
imarray_1sur5 = imarray[::5,::5,:]
imarray_1sur10 = imarray[::10,::10,:]
plt.imshow(imarray_1sur2)
plt.show()
plt.imshow(imarray_1sur5)
plt.show()
plt.imshow(imarray_1sur10)
plt.show()
```

3. Isoler le rectangle de `l` lignes et `c` colonnes en milieu d'image  
affichez-le pour `(l, c) = (10, 20)`) puis `(l, c) = (100, 200)`)

```{code-cell} ipython3
# votre code
L, H, _ = imarray.shape
xm, ym = L//2, H//2

l, c = (100,200)
encard = imarray[xm-l//2:xm+l//2,ym-c//2:ym+c//2,:]
plt.imshow(encard)
```

4. Affichez le dernier pixel de l'image

```{code-cell} ipython3
# votre code
plt.imshow(imarray[-1:,-1:,:])
```

## canaux rgb de l'image

+++

1. Relire l'image

```{code-cell} ipython3
# votre code
plt.imshow(imarray)
```

2. Découpez l'image en ses trois canaux Red, Green et Blue

```{code-cell} ipython3
# votre code
red = imarray[:,:,0]
green = imarray[:,:,1]
blue = imarray[:,:,2]
```

3. Afficher chaque canal avec `plt.imshow`  
    La couleur est-elle la couleur attendue ?  
    Si oui très bien, si non que se passe-t-il ?

    **rappel** table des couleurs

    * `RGB` représente directement l'encodage de la couleur du pixel  
    et non un indice dans une table

    * donc pour afficher des pixel avec les 3 valeurs RGB pas besoin de tables de couleurs  
    on a la couleur

    * mais pour afficher une image unidimensionnelle contenant des nombres de `0` à `255`  
    il faut bien lui dire à quoi correspondent les valeurs  
    (lors de l'affichage, le `255` des rouges n'est pas le même `255` des verts)

    * donner le paramètre `cmap=` à `plt.imshow`, `'Reds'`,  `'Greens'` ou  `'Blues'`

```{code-cell} ipython3
# votre code
for i in (red,green,blue):
    plt.imshow(i)
    plt.show()
```

4. Corrigez vos affichages si besoin

```{code-cell} ipython3
# votre code
```

5. Copiez l'image, remplacer dans la copie, un carré de taille `(200, 200)` en bas à droite  
   . par un carré de couleur RGB avec R à 219, G à 112 et B à 147 (vous obtenez quelle couleur)  
   . par un carré blanc avec des rayures horizontales rouges de 1 pixel

```{code-cell} ipython3
imarray_cp = imarray.copy()

imarray_cp[-200:,-200:] = [219,112,147]
plt.imshow(imarray_cp)
plt.show()

carre_ray = np.full((200,200,3), 255)
carre_ray[::2,:] = [255,0,0]
plt.imshow(carre_ray)
plt.show()

imarray_cp2 = imarray.copy()
imarray_cp2[-200:,-200:] = carre_ray
plt.imshow(imarray_cp2)
plt.show()
```

6. enfin affichez les 20 dernières lignes et colonnes du carré à rayures

```{code-cell} ipython3
# votre code
print(carre_ray[-20:,-20:,:])
```

## transparence des images

+++

````{admonition} rappel: la transparence
**rappel** RGB-A

* on peut indiquer, dans une quatrième valeur des pixels, leur transparence
* ce 4-ème canal s'appelle le canal alpha
* les valeurs vont de `0` pour transparent à `255` pour opaque
````

+++

1. Relire l'image initiale (sans la copier)

```{code-cell} ipython3
# votre code
plt.imshow(imarray)
```

2. Créez un tableau vide de la même hauteur et largeur que l'image, du type de l'image initiale, avec un quatrième canal

```{code-cell} ipython3
# votre code
imarray.shape
transp = np.zeros((L,H,4), dtype=np.uint)
```

3. Copiez-y l'image initiale, mettez le quatrième canal à `128` et affichez l'image

```{code-cell} ipython3
# votre code
transp[:,:,:3] = imarray
transp[:,:,3] = 128
plt.imshow(transp)
```

## image en niveaux de gris en `float`

+++

1. Relire l'image `data/les-mines.jpg`

```{code-cell} ipython3
# votre code
plt.imshow(imarray)
```

2. Passez ses valeurs en flottants entre 0 et 1 et affichez-la

```{code-cell} ipython3
# votre code
imf = np.astype(imarray,float)
```

3. Transformer l'image en deux images en niveaux de gris :  
a. en mettant pour chaque pixel la moyenne de ses valeurs R, G, B  
b. en utilisant la correction 'Y' (qui corrige le constrate) basée sur la formule  
   `G = 0.299 * R + 0.587 * V + 0.114 * B`

```{code-cell} ipython3
# votre code

#a)
gris1 = np.zeros((L,H,1))
gris1[:,:,0] = (imf[:,:,0]+imf[:,:,1]+imf[:,:,2])/3
plt.imshow(gris1, cmap="Greys")
plt.show()

#b)

gris2 = np.zeros((L,H,1))
gris2[:,:,0] = .299 * imf[:,:,0] + .587 * imf[:,:,1] + .114 * imf[:,:,2]
plt.imshow(gris2, cmap="Greys")
```

4. Passez au carré les pixels et affichez l'image

```{code-cell} ipython3
# votre code
square = gris2 * gris2
plt.imshow(square, cmap="Greys")
```

5. Passez en racine carré les pixels et affichez-la

```{code-cell} ipython3
# votre code
# votre code
root = np.sqrt(gris2)
plt.imshow(root, cmap="Greys")
```

6. Convertissez l'image de niveaux de gris en type entier non-signé 8 bits et affichez la  
en niveaux de gris

```{code-cell} ipython3
# votre code
int_ver = 256*root
```

## affichage grille de figures

+++

Affichage en `matplotlib.pyplot` de plusieurs figures sur une grille

**1) on créé une figure globale et des sous-figures**

les sous-figures sont appelées `axes` par convention `matplotlib`

on construit notre grille ici de 2 lignes et 3 colonnes

```python
fig, axes = plt.subplots(2, 3)
print(type(axes))
print(axes.shape)
```

les cases pour les sous-figures sont ici dans la variable `axes`  
qui est un `numpy.ndarray` de taille 2 lignes et 3 colonnes

**2) on affiche des sous-figure dans des cases de la grille**

```python
x = np.linspace(0, 2*np.pi, 50)
axes[0, 0].plot(x, np.sin(x), 'b')
axes[0, 1].plot(x, np.sin(x), 'r')
axes[0, 2].plot(x, np.sin(x), 'y')
axes[1, 0].plot(x, np.sin(x), 'k')
axes[1, 1].plot(x, np.sin(x), 'g')
axes[1, 2].plot(x, np.sin(x), 'm')
```

**3) on peut faire un peu de cosmétique mais**  
quand on commence on ne s'arrête plus et on perd beaucoup de temps  
préférez au début des affichages minimalistes à peu près lisibles
```python
fig.suptitle("sinus en couleur", fontsize=20) # titre général
axes[0, 0].set_title('sinus bleu')            # titre d'une sous-figure
axes[0, 2].set_xlabel('de 0 à 2 pi')          # label des abscisses
axes[1, 1].set_ylabel('de -1 à 1')            # label d'ordonnées
axes[1, 2].set_title('sinus magenta')
plt.tight_layout()                            # ajustement automatique des paddings
```

```{code-cell} ipython3
# ce qui nous donne, mis bout à bout
import numpy as np
import matplotlib.pyplot as plt

# le code
fig, axes = plt.subplots(2, 3)
print(type(axes))
print(axes.shape)

x = np.linspace(0, 2*np.pi, 50)

axes[0, 0].plot(x, np.sin(x), 'b')
# axes[0, 1].plot(x, np.sin(x), 'r')
axes[0, 2].plot(x, np.sin(x), 'y')
axes[1, 0].plot(x, np.sin(x), 'k')
axes[1, 1].plot(x, np.sin(x), 'g')
axes[1, 2].plot(x, np.sin(x), 'm')

fig.suptitle("sinus en couleur", fontsize=20)
axes[0, 0].set_title('sinus bleu')
axes[0, 2].set_xlabel('de 0 à 2 pi')
axes[1, 1].set_ylabel('de -1 à 1')
axes[1, 2].set_title('sinus magenta')
plt.tight_layout();
```

## reprenons le TP

+++

Reprenez les trois images en niveau de gris que vous aviez produites ci-dessus:  
  A: celle obtenue avec la moyenne des rgb  
  B: celle obtenue avec la correction Y  
  C: celle obtenue avec la racine carrée

1. Affichez les trois images côte à côte  
   1 2 3

+++

2. Affichez-les en damier:  
   1 2 3  
   3 1 2  
   2 3 1

```{code-cell} ipython3
# votre code
```
