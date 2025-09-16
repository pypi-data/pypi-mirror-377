---
jupytext:
  cell_metadata_json: true
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

<div class="licence">
<span>Licence CC BY-NC-ND</span>
<span>Thierry Parmentelat &amp; Arnaud Legout</span>
</div>

```{code-cell} ipython3
---
slideshow:
  slide_type: slide
---
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib ipympl
```

# l'ensemble de Mandelbrot

il s'agit de calculer l'image de la convergence de mandelbrot:

```{image} media/mandelbrot.png
:width: 400px
:align: right
```

+++

## comment ça marche ?

+++ {"cell_style": "center", "slideshow": {"slide_type": "slide"}}

* dans l'espace complexe, on définit pour chaque $c\in\mathbb{C}$ la suite
   * $z_0 = c$
   * $z_{n+1} = z_n^2 + c$
* on démontre que 
  * lorsque $|z_n|>2$, la suite diverge

+++ {"cell_style": "center", "slideshow": {"slide_type": "-"}}

il s'agit pour nous de 

* partir d'un pavé rectangulaire; par exemple sur la figure, on a pris l'habituel  
  $re \in [-2, 0.8]$ et  $im \in [-1.4, 1.4]$
* découper ce pavé en un maillage de $h \times w$ points  (sur la figure, 1000 x 1000)
* on se fixe un nombre maximal `max` d'itérations (disons 20)  
  et pour chaque point du maillage, on va calculer si la suite diverge avant `max` itérations
* c'est-à-dire plus spécifiquement on calcule un tableau `diverge` de la taille du maillage
  * pour chaque point `z`, on calcule les `max` premiers termes de la suite
  * et à la première itération `n` où la suite diverge (son module est supérieur à 2)  
    alors on affecte `diverge[z] = n`
* on n'a plus qu'à afficher ensuite l'image obtenue `diverge` avec `plt.imshow`

+++ {"slideshow": {"slide_type": "slide"}}

````{admonition} indices

pour fabriquer la grille des points de départ, on pourra regarder `np.linspace` et `np.meshgrid`
````

```{code-cell} ipython3
# à vous de jouer

MAX = 10

mod_2 = lambda z : z[0]**2 + z[1]**2

@np.vectorize
def carre(x, y) :
    return (x**2 - y**2, 2*x*y)

def mandelbrot(h, w):
    x = np.linspace(-2, 0.8, h)
    y = np.linspace(-1.4, 1.4, w)
    grid = np.array(np.meshgrid(x,y)).T #En transposant on inverse l'ordre des axes et on obtient le produit cartésien.
    diverge = np.array([[MAX for _ in range(w)] for _ in range(h)]) #On initialise à MAX -> La zone dont l'éventuelle "divergence" est la plus lente de toute la fenêtre
    grid0 = grid.copy()
    
    for n in range(1, MAX+1):
        grid[:,:,0], grid[:,:,1] = carre(grid[:,:,0], grid[:,:,1])
        grid = grid + grid0
        for i in range(h):
            for j in range(w):
                if mod_2(grid[i,j,:]) > 4 : #module au carré > 4 <=> module > 2
                    grid[i,j] = [0,0] #On reborne la suite pour éviter de la faire diverger pour de vrai.
                    if diverge[i,j]==MAX : #Si on n'a pas encore noté ce complexe comme divergent. 
                        diverge[i, j] = n
    plt.imshow(diverge.T, extent = [-2, 0.8, -1.4, 1.4]) #On prend la transposée de diverge, car le premier axe est vertical sur l'image.
    plt.colorbar()
    plt.show()
```

```{code-cell} ipython3
# et pour la tester, pour produire la même figure que ci-dessus

mandelbrot(1000, 1000)
```

## v2

* on peut passer en paramètre à la fonction
  * le domaine en x et en y
  * le nombre maximum d'itérations
* on veut pouvoir produire une image (pour l'insérer dans l'énoncé par exemple)
  * quels formats sont disponibles ?
  * sauvez votre image dans un format vectoriel
  * affichez cette depuis votre notebook

```{code-cell} ipython3
# à vous de jouer
# je vous laisse définir la signature de votre fonction

#Version alternative -> on utilise les complexes

def mandelbrot2(h, w, window, MAX):
    if len(window) == 4 :
        xmin, xmax, ymin, ymax = window
    else : #Si pas de précision sur y, on va garder le même aspect ratio que pour le 1e exemple
        xmin, xmax = window
        demir = (xmax-xmin)/(0.8+2)*1.4
        ymin, ymax = demir, -demir
        window = [xmin, xmax, ymin, ymax]
    x = np.linspace(xmin, xmax, h)
    y = np.linspace(ymin, ymax, w)
    numbs = np.array(np.meshgrid(x,y)).T #En transposant on inverse l'ordre des axes et on obtient le produit cartésien.
    grid = numbs[:,:,0] + 1j*numbs[:,:,1]
    
    diverge = np.array([[0 for _ in range(w)] for _ in range(h)]) #On initialise à 0 -> La zone bornée est à MAX
    grid0 = grid.copy()
    
    for n in range(1, MAX+1):
        mask_ndvg = (np.abs(grid) <= 4) #On va faire les calculs uniquement sur la zone non divergente.
        grid[ mask_ndvg ] = np.square(grid[ mask_ndvg ]) + grid0 [ mask_ndvg ]
        diverge[ mask_ndvg ] = diverge[ mask_ndvg ] + 1
        grid[ mask_ndvg ]
    plt.imshow(diverge.T, extent = window) #On prend la transposée de diverge, car le premier axe est vertical sur l'image.
    plt.colorbar()
    plt.show()
```

### Des petits tests

```{code-cell} ipython3
# test #1

mandelbrot2(500, 500, MAX = 10, window=[-3, 1.2])
```

### Mandelbrot est un ensemble fractal, pourquoi pas zoomer ?

```{code-cell} ipython3
# test #2
mandelbrot2(1000, 1000, MAX = 20, window=[-2, -0.7])
```

```{image} media/more.png
:width: 400px
:align: right
```

```{code-cell} ipython3
# test #3

mandelbrot2(1000, 1000, MAX = 20, window=[-1.66, -1.22])
```

----
