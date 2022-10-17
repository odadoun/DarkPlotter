
from bokeh.plotting import figure, output_file, show,output_notebook,curdoc
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS, MultiSelect,CheckboxGroup,CheckboxGroup
from bokeh.models.glyphs import Line
from bokeh.models import Legend
from bokeh.themes import Theme
from bokeh.layouts import column, row
import pandas as pd
from bokeh.io import curdoc
from bokeh.palettes import Category10
import requests
from pprint import pprint
from pandas.io.json import json_normalize
import ssl
import json
from bokeh.palettes import Category10
from bs4 import BeautifulSoup as bs
import requests
import numpy as np
import pandas as pd
output_notebook(hide_banner=True)

ssl._create_default_https_context = ssl._create_unverified_context

class DMdata():
    def __init__(self):
        self.url    = 'https://github.com/odadoun/DarkPlotter/tree/main/json/'
        self.rawurl = 'https://raw.githubusercontent.com/odadoun/DarkPlotter/main/json/'
        self.mypandas = pd.DataFrame()

    def githubpath2raw(self,**kwargs):
        url = kwargs.get('url',self.url)
        urlraw = self.rawurl
        res = requests.get(url)
        soup = bs(res.text, 'lxml')
        nav = soup.find_all('a',class_="js-navigation-open")
        files = [ i.text for i in nav if '.json' in i.text  ]
        if files:
            path = [ urlraw + i for i in files ]
        else:
            raise Exception('Nothing to parse in this folder ...')
        exp_pd=pd.DataFrame({'rawurl':path})
        return exp_pd

    def uploadexperiement(self,**kwargs):
        default = self.rawurl + 'SI-CDMS-CDMS%20II%2C%20Reanalysis%20LT-5c87c458d484949dedf45757e811d495.json'
        url = kwargs.get('url',default)
        if not isinstance(url,list):
            url=[url]
        for i in url:
            tmp = pd.read_json(i.replace(' ','%20'))
            tmp = tmp.apply(lambda x: x.to_list() if x.name in ['x','y'] else x[0])
            if self.mypandas.empty:
                self.mypandas = pd.DataFrame(data={i:[tmp[i]] for i in tmp.index})
            else:
                if tmp['experiment'] not in self.mypandas.experiment.to_list():
                    self.mypandas = pd.concat([self.mypandas,pd.DataFrame(data={i:[tmp[i]] for i in tmp.index})])
        self.mypandas = self.mypandas.loc[~self.mypandas['experiment'].isin([''])]

    def getmetadata(self):
        return self.mypandas.drop(columns=['x','y']).set_index('experiment')

    def getdata(self):
        return self.mypandas[['experiment','x','y']].set_index('experiment')
    
    def getpandas(self):
        return self.mypandas


class DMplotter():
    def __init__(self):
        self.tooltips = """
        <b>Expriment</b>:$name<br>
        <b>M </b> = @y cm<sup>2</sup>  <br>
        <b>&sigma;</b> = @x GeV/c<sup>2</sup> <br>
        """
        self.figlimits = {}
        self.fig = None

    def plot(self,mypandas=None):
        mypd = mypandas
        self.fig = figure(plot_width=800, plot_height=600,tooltips=self.tooltips,x_axis_type="log",y_axis_type='log')
        if not isinstance(mypandas,list):
            mypd =[ mypandas ]
        mypd = pd.concat(mypd)
        if mypd.index.name == 'experiment':
            mypd = mypd.reset_index()
        experiments=mypd.experiment.unique()
        xmax, ymax = 2*[-1.]
        xmin, ymin = 2*[1.e6]
        nbcolors=7
        palette = Category10[nbcolors]
        allplots={}
        for i,j in enumerate(experiments):
            focus=mypd.loc[mypd.experiment==j]
            #print(focus['y-units'].item())
            if focus['y-units'].item() == 'fb':
                scale = 1.E-39
            if focus['y-units'].item() == 'cm^2':
                scale = 1.
            if focus['y-units'].item() == 'pb':
                scale = 1.E-36
            if focus['y-units'].item() == 'zb':
                scale = 1.E-45
            if focus['y-units'].item() == 'ub':
                scale = 1.E-30

            for i, s in enumerate(focus.y.item()):
                focus.y.item()[i] = s*scale
            focus=focus.explode(['x','y'])
            allplots[j]=self.fig.line(x = 'x', y = 'y', line_width=2,line_color=palette[i%nbcolors],\
                    name=j,source = ColumnDataSource(focus))
            xmin, xmax, ymin, ymax = min(xmin,focus.x.min()), max(xmax,focus.x.max()),\
                                     min(ymin,focus.y.min()), max(ymax,focus.y.max())
            self.figlimits = {'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax}
        self.draw(allplots)

    def draw(self,dico={}):
        fig = self.fig
        fig.x_range=Range1d(self.figlimits['xmin'], self.figlimits['xmax'])
        fig.y_range=Range1d(self.figlimits['ymin'], self.figlimits['ymax'])
        fig.xaxis.axis_label = r"WIMP Mass GeV/c²"
        fig.yaxis.axis_label = r"WIMP-Nucleon Cross Section cm²"

        legend_it=[]
        for k,v in dico.items():
            legend_it.append((k, [v]))
        legend = Legend(items=legend_it)
        legend.click_policy="hide"
        fig.add_layout(legend, 'right')
        curdoc().theme = Theme(filename="./theme.yml")

        checkbox = CheckboxGroup(labels=list(dico.keys()), active=list(range(len(dico))), width=100)
        callback = CustomJS(args=dict(lines=list(dico.values()), checkbox=checkbox),
        code="""
                for(var i=0; i<lines.length; i++){
                    lines[i].visible = checkbox.active.includes(i);
            }
        """)

        checkbox.js_on_change('active', callback)
        curdoc().theme = Theme(filename="./theme.yml")
        layout = row(fig,checkbox)
        layout=fig
        show(layout)
