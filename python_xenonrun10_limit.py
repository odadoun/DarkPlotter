from bokeh.plotting import figure, output_file, show,output_notebook,curdoc
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS, MultiSelect,CheckboxGroup,CheckboxGroup

#from bokeh.models.widgets import Select
from bokeh.layouts import column, row
import pandas as pd
from bokeh.io import curdoc
from bokeh.palettes import Spectral4
import requests
from pprint import pprint
from pandas.io.json import json_normalize
import ssl
from bs4 import BeautifulSoup
from github import Github
import json
from bokeh.palettes import Spectral
#output_notebook(hide_banner=True)

ssl._create_default_https_context = ssl._create_unverified_context

tooltips = """
<b>Expriment</b>:$name<br>
<b>M </b> = @y cm<sup>2</sup>  <br>
<b>&sigma;</b> = @x GeV/c<sup>2</sup> <br>

"""

fig = figure(plot_width=800, plot_height=600,tooltips=tooltips,x_axis_type="log",y_axis_type='log')

url='https://raw.githubusercontent.com/cajohare/NeutrinoFog/main/data/WIMPLimits/SDn/'
cajoharefiles=['CDMS.txt','CDMSlite.txt','CRESST.txt','LUX.txt','PICASSO.txt','PandaX.txt','XENON100.txt','XENON1T-Migdal.txt','XENON1T.txt']
df = []
right, top = [-1.]*2
left, bottom = [1.e6]*2
palette = Spectral[len(cajoharefiles)]
for i, expfile in enumerate(cajoharefiles):
    tmp = pd.read_csv(url+expfile,header=None,names=["x", "y"],sep='\t')
    exp=expfile.replace('.txt','')
    tmp=tmp[:-1]
    tmp['x']=tmp['x'].astype('float')
    tmp['y']=tmp['y'].astype('float')
    tmp=tmp.dropna()
    #left= min(left,tmp.x.min())
    left, right, bottom, top = min(left,tmp.x.min()), max(right,tmp.x.max()), min(bottom,tmp.y.min()), max(top,tmp.y.max())
    df.append(fig.line(x = 'x', y = 'y', line_width=2,line_color=palette[i],name=exp, source = ColumnDataSource(tmp)))
fig.x_range=Range1d(left, right)
fig.y_range=Range1d(bottom, top)
fig.xaxis.axis_label = r"$$\mathrm{\color{white}WIMP~Mass~GeV/c^{2}}$$"
fig.yaxis.axis_label = r"$$\mathrm{\color{white}WIMP-Nucleon~Cross~Section~cm^2}$$"
curdoc().theme = 'dark_minimal'
checkbox = CheckboxGroup(labels=[i.replace('.txt','') for i in cajoharefiles], active=list(range(len(expfile))), width=100)
callback = CustomJS(args=dict(lines=df, checkbox=checkbox),
code="""
        for(var i=0; i<lines.length; i++){
            lines[i].visible = checkbox.active.includes(i);
    }
""")

checkbox.js_on_change('active', callback)
curdoc().theme = 'dark_minimal'
layout = row(fig,checkbox)
show(layout)


def toto():
    jfiles=['cresst2.json', 'gcoupp.json','graphcc2.json', 'gxenon100run8profilelimit.json']

    TOOLTIPS = [
        ("(x,y)", "($x, $y)"),
        ('expriment', "$name")
    ]
    fig = figure(plot_width=600, plot_height=600,tooltips=TOOLTIPS,x_axis_type="log",y_axis_type='log')

    df = []#https://raw.githubusercontent.com/odadoun/Xenon/main/json/"+exp[0])
    exp  = []
    right, top = [-1]*2
    left, bottom = [1e6]*2

    for i in jfiles:
        tmp = pd.read_json("https://raw.githubusercontent.com/odadoun/Xenon/main/json/"+i)
        left, right, bottom, top = min(left,tmp.x.min()), max(right,tmp.x.max()), min(bottom,tmp.y.min()), max(top,tmp.y.max())
        exp.append(tmp.experiment[0])
        df.append(fig.line(x = 'x', y = 'y', color = tmp.color[0], line_width=2,name = tmp.experiment[0], source = ColumnDataSource(tmp)))
    fig.x_range=Range1d(left, right)
    fig.y_range=Range1d(bottom, top)

    fig.legend.location = "top_right"
    fig.legend.click_policy="hide"
    fig.xaxis.axis_label = r"$$\color{white} \nu \:(10^{15} s^{-1})$$"
    fig.yaxis.axis_label = r"$$\color{white} B_\nu(\nu, T) \quad(10^{-9} J s m^{-3})$$"
    #fig.xaxis.axis_label = r"$$WIMP Mass \color{red} \nGeV/c^{2}$$"
    #fig.yaxis.axis_label = r"WIMP-Nucleon Cross Section cm^2$$"

    nbexp = list(range(len(exp)))


    checkbox = CheckboxGroup(labels=exp, active=nbexp, width=100)
    callback = CustomJS(args=dict(lines=df, checkbox=checkbox),
    code="""
            for(var i=0; i<lines.length; i++){
                lines[i].visible = checkbox.active.includes(i);
        }
    """)

    checkbox.js_on_change('active', callback)
    curdoc().theme = 'dark_minimal'
    layout = row(fig,checkbox)
    show(layout)
