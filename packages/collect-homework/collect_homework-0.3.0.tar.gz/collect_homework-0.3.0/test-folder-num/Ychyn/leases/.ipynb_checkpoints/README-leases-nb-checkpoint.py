# ---
# jupyter:
#   jupytext:
#     custom_cell_magics: kql
#     notebook_metadata_filter: language_info
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
# ---

# %% [markdown]
# # grouping through time and category
#
# to work on this assignment locally on your laptop, {download}`start with downloading the zip<./ARTEFACTS-leases.zip>`
#
# in this TP we work on 
#
# - data that represents *periods* and not just one timestamp
# - checking for overlaps
# - grouping by time
#   - later grouping by time and category
# - and some simple visualization tools
#
# here's an example of the outputs we will obtain
#
# ```{image} media/result-m.png
# :width: 300px
# :align: center
# ```

# %% [markdown]
# ## imports

# %%
import pandas as pd
import matplotlib.pyplot as plt


# %% [markdown]
# 1. make sure to use matplotlib in interactive mode - aka `ipympl`

# %%
# your code

# %matplotlib ipympl

# %% [markdown]
# ## the data
#
# we have a table of events, each with a begin and end time; in addition each is attached to a country

# %%
leases = pd.read_csv("data/leases.csv")
leases.head(10)

# %% [markdown]
# ### adapt the type of each columns

# %%
# your code

# FORMAT = "%Y-%m-%d %H:%M:%S"
FORMAT = "ISO8601"

leases['beg'] = pd.to_datetime(leases.beg, format=FORMAT)
leases['end'] = pd.to_datetime(leases.end, format=FORMAT)

# %%
# check it

leases.dtypes

# %% [markdown]
# ### raincheck
#
# check that the data is well-formed, i.e. **the `end`** timestamp **happens after `beg`**

# %%
# your code
print(sum( leases.beg < leases.end) == len(leases))

# %% [markdown]
# ### are there any overlapping events ?

# %% [markdown]
#    it turns out there are **no event overlap**, but write a code that checks that this is true
#
#    ```{admonition} note
#    :class: tip
#
#    nothing in the rest depends on this question, so if you find this too hard, you can skip to the next question
#    ```

# %%
# your code
leases_sorted = leases.sort_values(by=["country",'beg'])
leases_sorted['end_shifted'] = leases_sorted['end'].shift(periods=-1)
leases_sorted['country_shifted'] = leases_sorted['country'].shift(periods=-1)
nb_errors = sum((leases_sorted.beg > leases_sorted.end_shifted) & (leases_sorted.country_shifted == leases_sorted.country))
print(nb_errors)

# %% [markdown]
# ### timespan
#
# What is the timespan coverred by the dataset (**earliest** and **latest** events, and **duration** in-between) ?

# %%
# your code
debut = leases.sort_values(by='beg').iloc[0,0]
fin = leases.sort_values(by='end').iloc[-1,1]
duration = (fin - debut)
print('earliest event:',debut)
print('latest event:',fin)
print('duration:',(fin - debut))

# %% [markdown]
# ### aggregated duration
#
# so, given that there is no overlap, we can assume this corresponds to "reservations" attached to a unique resource (hence the term  *lease*)
#
# write a code that computes the **overall reservation time**, as well as the **average usage ratio** over the active period  

# %%
# your code
overall_time = (leases.end - leases.beg).sum()
print('the overall reservation time was',overall_time)
print('the average usage ration is then', overall_time/duration)

# %% [markdown]
# ## visualization - grouping by time only
#
# ### usage by period
#
# grouping by periods: by week, by month or by year, display the **total usage in that period**  
# (when ambiguous, use the `beg` column to determine if a lease is in a period or the other)
#
# for now, just get the grouping right, we'll improve miscellaneous details below
#
# also you can [refer to this section below](#label-sample-results) to get a glimpse of the expected output, even though for now we have no grouping, so a single color for all bars.

# %%
# your code

# %% [markdown]
# ### improve the title and bottom ticks
#
# add a title to your visualisations
#
# also, and particularly relevant in the case of the per-week visu, we don't get to read **the labels on the horizontal axis**, because there are **too many of them**  
# to improve this, you can use matplotlib's `set_xticks()` function; you can either figure out by yourself, or read the few tips below
#
# ````{admonition} a few tips
# :class: dropdown tip
#
# - the object that receives the `set_xticks()` method is an instance of `Axes` (one X&Y axes system),  
#   which is not the figure itself (a figure may contain several Axes)  
#   ask google or chatgpt to find the way you can spot the `Axes` instance in your figure
# - it is not that clear in the docs, but all you need to do is to pass `set_xticks` a list of *indices* (integers)  
#   i.e. if you have, say, a hundred bars, you could pass `[0, 10, 20, ..., 100]` and you will end up with one tick every 10 bars.
# - there are also means to use smaller fonts, which may help see more relevant info
# ````

# %%
# let's say as arule of thumb
LEGEND = {
    'W': "week",
    'M': "month",
    'Y': "year",
}

SPACES = {
    'W': 12,   # in the per-week visu, show one tick every 12 - so about one every 3 months
    'M': 3,    # one every 3 months
    'Y': 1,    # on all years
}


# %%
# your code

# %% [markdown]
# ### a function to convert to hours
#
# write a function that converts a timedelta into a number of hours - see the test code for the details of what is expected

# %%
# your code

def convert_timedelta_to_hours(timedelta):
    pass

# %%
# test it

# if an hour has started even by one second, it is counted
# seconds, hours
test_cases = ( (0, 0), (1, 1), (3600, 1), (3601, 2), (7199, 2), (7200, 2), (7200, 3))

def test_convert_timedelta_to_hours():
    for seconds, exp in test_cases:
        timedelta = pd.Timedelta(seconds=seconds)
        got = convert_timedelta_to_hours(timedelta)
        print(f"with {timedelta=} we get {got} and expected {exp} -> {got == exp}")

test_convert_timedelta_to_hours()

# %% [markdown]
# ### use it to display totals in hours
#
# keep the same visu, but display **the Y axis in hours**
#
# btw, what was the unit in the graphs above ?

# %%
# your code

# %% [markdown]
# ## grouping by time and by region
#
# the following table allows you to map each country into a region

# %%
# load it

countries = pd.read_csv("data/countries.csv")
countries.head(3)

# %%
# how many countries ?

countries.region.value_counts()

# %% [markdown]
# that is to say, 5 groups (at most)

# %% [markdown]
# your mission is to now show the same graphs, but with each bar split into up to 5, to reflect the relative usage of each region

# %% [markdown]
# ### attach a region to each lease
#
# most likely your first move is to tag all leases with a `region` column

# %%
# your code

# %% [markdown]
# (label-sample-results)=
#
# ### visu by time and by region
#
# you can now produce the target figures; the expected final results looks like this
#
# ```{image} media/result-w.png
# ```
# ```{image} media/result-m.png
# ```
# ```{image} media/result-y.png
# ```

# %%
# your code
