# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_json: true
#     notebook_metadata_filter: language_info,nbhosting
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.12.4
#   nbhosting:
#     title: TP sur le tri d'une dataframe
# ---

# %% [markdown]
# License CC BY-NC-ND, Valérie Roy & Thierry Parmentelat

# %%
from IPython.display import HTML
HTML(filename="_static/style.html")

# %% [markdown]
# # TP sur le tri d'une dataframe

# %% [markdown]
# **Notions intervenant dans ce TP**
#
# * affichage des données par `plot`
# * tri de `pandas.DataFrame` par ligne, par colonne et par index
#
# **N'oubliez pas d'utiliser le help en cas de problème.**

# %% [markdown]
# 1. importez les librairies `pandas`et `numpy`

# %%
# votre code
import pandas as pd
import numpy as np

# %% [markdown]
# 2. importez la librairie `matplotlib.pyplot` avec le nom `plt` 

# %%
# votre code
import matplotlib.pyplot as plt

# %% [markdown]
# 3. lors de la lecture du fichier de données `data/titanic.csv`  
#    1. gardez uniquement les colonnes `cols` suivantes `'PassengerId'`, `'Survived'`, `'Pclass'`, `'Name'`, `'Sex'`, `'Age'` et `'Fare'`
#
#    1. mettez la colonne `PassengerId` comme index des lignes
#    1. besoin d'aide ? faites `pd.read_csv?`

# %%
# votre code

df = pd.read_csv("data/titanic.csv", index_col=["PassengerId"], usecols=["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "Fare"])
df

# %% [markdown]
# 4. en utilisant la méthode `pd.DataFrame.plot`  
#    plottez la dataframe (pas la série) réduite à la colonne des ages  
#    utilisez le paramètre de `style` `'rv'` (`r` pour rouge et `v` pour le style: points triangulaires)
#
#    vous allez voir les points *en vrac*; dans la suite on va s'efforcer de les trier, pour mieux
#    voir la distribution des âges dans la population concernée

# %%
# votre code

df["Age"].plot(style="rv", ylabel="Age")

# %% [markdown]
# 5. pour commencer on va trier - i.e. mettre les lignes de la  dataframe suivant l'ordre d'une colonne    
#    en utilisant la méthode `df.sort_values()`:
#    1. créez une nouvelle dataframe  dont les lignes sont triées  
#       dans l'ordre croissant des `'Age'` des passagers
#    2. pour constater qu'elles sont triées, affichez les 4 premières lignes de la dataframe  
#       la colonne des `Age` est triée  
#       les lignes ont changé de place dans la table
#    3. remarquez que l'indexation a été naturellement conservée 

# %%
# votre code
new_df = df.sort_values(by=["Age"])
new_df.head(4)

# %% [markdown]
# 6. 1. plottez la colonne des ages de la dataframe triée  
#       pour changer un peu on va mettre un style `'b.'`
#    1. Que constatez-vous ?

# %%
# votre code
new_df["Age"].plot(style="b", ylabel="Age")

# %% [markdown]
# 7. 1. la logique de `df.plot()` consiste
#
#       * à **utiliser comme abscisses** l'index de la dataframe
#       * et accessoirement à faire autant de plots que de colonnes - ici on n'en a qu'une
#     vous tracez donc le point $(804, 0.42)$ puis le point $(756, 0.67)$ ...  
#     alors que vous voudriez tracer le point $(0, 0.42)$ puis le point $(1, 0.67)$ ...  
#     c'est à dire: le fait d'utiliser le 'PassengerId' n'est pas bon, on voudrait que les abscisses soient les indices de lignes
#    1. une solution: voyez la méthode `reset_index()`
#       qui permet de transformer l'index en une colonne normale  
#    1. utiliser cette méthode et regardez ce que vous avex dans l'index ensuite
#    1. plottez le résultat  
#       normalement à ce stade vous obtenez la visualisation qu'on cherche

# %%
# votre code
new_df.reset_index(inplace=True)
new_df["Age"].plot(style="b", ylabel="Age")

# %% [markdown]
# ## tri des lignes *égales* au sens d'un premier critère d'une dataframe

# %% [markdown]
# 0. rechargez la dataframe

# %%
# votre code
df = pd.read_csv("data/titanic.csv", index_col=["PassengerId"], usecols=["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "Fare"])
df

# %% [markdown]
# 2. utilisez `df.sort_values()` pour trier la dataframe suivant la colonne (`'Pclass'`)  
#    et trier les lignes identiques (passagers de même classe) suivant la colonne (`'Age'`)  
#    *note*: on appelle cela un ordre lexicographique, car c'est un peu comme dans un dictionnaire

# %%
# votre code
df.sort_values(by = ["Pclass", "Age"], inplace = True)
df

# %% [markdown]
# 3. sélectionnez, dans la nouvelle dataframe, la sous-dataframe dont les ages ne sont pas définis  
#    *hint*: utiliser la méthode `isna` sur une série, pour créer un masque booléens, et appliquer ce masque à la dataframe   

# %%
# votre code
dfna = df[df["Age"].isna()]
dfna

# %% [markdown]
# 4. combien manque-il d'ages ?

# %%
# votre code
( df["Age"].isna() ).sum()

# %% [markdown]
# 5. où sont placés ces passagers dans la data-frame globale triée ?  
# en début (voir avec `head`) ou en fin (voir avec `tail`) de dataframe ?

# %%
# votre code
# Ils sont placés dans la tail
df.tail()

# %% [markdown]
# 6. trouvez le paramètre de `sort_values()`  
# qui permet de mettre ces lignes en début de dataframe lors du tri

# %%
# votre code
new_df2 = df.sort_values(by = ["Age"], na_position = "first")
new_df2

# %% [markdown]
# 7. produire une nouvelle dataframe en ne gardant que les ages connus,
#    et triée selon les ages, puis les prix de billet

# %% [markdown] {"tags": ["level_intermediate"]}
# ## tri d'une dataframe selon l'index
#
# (optionnel)
#
# en utilisant `df.sort_index()` il est possible de trier une dataframe  
# dans l'axe de ses index de ligne (ou même de colonnes)  

# %% [markdown] {"tags": ["level_intermediate"], "cell_style": "center"}
# 1. reprenez la dataframe du Titanic, en choisissant toujours comme index `PassengerId`  
#    utilisez la méthode des dataframe `sort_index` pour la trier dans l'ordre des index 

# %% {"tags": ["level_intermediate"]}
# votre code
df = pd.read_csv("data/titanic.csv", index_col=["PassengerId"], usecols=["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "Fare"])

df.sort_index(inplace=True)
df

# %% [markdown]
# ***
