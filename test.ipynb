from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS
#from bokeh.models.widgets import Select
from bokeh.layouts import column, row
import pandas as pd
from bokeh.io import curdoc
from bokeh.palettes import Spectral4
import requests
from pandas.io.json import json_normalize
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_file("line.html")

import json

url="https://raw.githubusercontent.com/odadoun/Xenon/main/json/graphcc2.json"
df = pd.read_json(url)

TOOLTIPS = [
    ("(x,y)", "($x, $y)"),
    ('name', "$name")
]

fig = figure(plot_width=400, plot_height=400,tooltips=TOOLTIPS,)
source=ColumnDataSource(df)

fig.line('x', 'y',line_width=2,name='collaboration',legend_label='experiment',source=source)


fig.legend.location = "top_right"
fig.legend.click_policy="hide"
show(fig)
