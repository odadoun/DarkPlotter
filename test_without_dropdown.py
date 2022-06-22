from bokeh.plotting import figure, output_file, show,output_notebook
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS
#from bokeh.models.widgets import Select
from bokeh.layouts import column, row
import pandas as pd
from bokeh.io import curdoc
from bokeh.palettes import Spectral4
import requests
from pandas.io.json import json_normalize
import ssl
output_notebook(hide_banner=True)
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Select
from bokeh.io import show
from bokeh.models import Panel, Tabs
from bokeh.plotting import figure


ssl._create_default_https_context = ssl._create_unverified_context

import json

url="https://raw.githubusercontent.com/odadoun/Xenon/main/json/graphcc2.json"
df = pd.read_json(url)
url1="https://raw.githubusercontent.com/odadoun/Xenon/main/json/gcoupp.json"
df1 = pd.read_json(url1)
url2="https://raw.githubusercontent.com/odadoun/Xenon/main/json/cresst2.json"
df2 = pd.read_json(url2)
url3="https://raw.githubusercontent.com/odadoun/Xenon/main/json/gxenon100run8profilelimit.json"
df3 = pd.read_json(url3)

TOOLTIPS = [
    ("(x,y)", "($x, $y)"),
    ('name', "$name")
]

fig = figure(plot_width=400, plot_height=400,tooltips=TOOLTIPS,y_axis_type="log")
source=ColumnDataSource(df)
source1=ColumnDataSource(df1)
source2=ColumnDataSource(df2)
source3=ColumnDataSource(df3) 

fig.line(line_width=2,name='collaboration',source=source)
fig.line(line_width=2,name='collaboration1',source=source1)
fig.line(line_width=2,name='collaboration2',source=source2)
fig.line(line_width=2,name='collaboration3',source=source3)

show(fig)
