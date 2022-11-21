
from bokeh.plotting import figure, output_file, show,output_notebook,curdoc
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS, MultiSelect,CheckboxGroup,CheckboxGroup,LabelSet,LinearAxis,LogAxis
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
import sys
output_notebook(hide_banner=True)

ssl._create_default_https_context = ssl._create_unverified_context

class DMdata():
    def __init__(self):
        self.url    = 'https://github.com/odadoun/DarkPlotter/tree/dev/json/'
        self.rawurl = 'https://raw.githubusercontent.com/odadoun/DarkPlotter/dev/json/'
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

    def get_metadata(self):
        return self.mypandas.drop(columns=['x','y']).set_index('experiment')

    def get_data(self):
        return self.mypandas[['experiment','x','y']].set_index('experiment')
    
    def get_pandas(self):
        return self.mypandas.set_index("experiment")

    def get_experiment(self,collaboration="",experiment=""):
        if collaboration == "":
            collab = self.mypandas
            if experiment == "":
                exp = self.mypandas
            else :
                exp = collab[collab["experiment"].apply(lambda x : any(k in x for k in experiment))]
        else :
            collab = self.mypandas[self.mypandas["collaboration"].apply(lambda x : any(k in x for k in collaboration))]
            if experiment == "":
                exp = collab
            else :
                exp = collab[collab["experiment"].apply(lambda x : any(k in x for k in experiment))]

        if len(exp["experiment"].value_counts()) > 0:
            return exp
        else:
            print ("Warning: no experiment exist")
            sys.exit()


class DMplotter():
    def __init__(self):
        self.tooltips = """
        <b>Expriment</b>:$name<br>
        <b>M </b> = @y cm<sup>2</sup>  <br>
        <b>&sigma;</b> = @x GeV/c<sup>2</sup> <br>
        """
        self.figlimits = {}
        self.fig = None

    def plot(self,mypandas=None,massunit="GeV"):
        mypd = mypandas
        self.fig = figure(plot_width=1000, plot_height=600,tooltips=self.tooltips,x_axis_type="log",y_axis_type='log')
        if not isinstance(mypandas,list):
            mypd =[ mypandas ]
        mypd = pd.concat(mypd)
        if mypd.index.name == 'experiment':
            mypd = mypd.reset_index()
        experiments=mypd.experiment.unique()
        xmax, ymax = 2*[-1.]
        xmin, ymin = 2*[1.e6]
        xunit = massunit
        zoom = 1.
        nbcolors=7
        palette = Category10[nbcolors]
        allplots={}
        lineplots={}
        areaplots={}
        neutrino={}
        if xunit == "MeV":
            zoom = 1e3
        elif xunit == "GeV":
            zoom = 1
        elif xunit == "TeV":
            zoom = 1e-3
        else:
            print("Please choose correct massunit")
            sys.exit()
        
        for i,j in enumerate(experiments):
            focus=mypd.loc[mypd.experiment==j]
            #print(focus['y-units'].item())
            if focus['y-units'].item() == 'fb':
                yscale = 1.E-39
            if focus['y-units'].item() == 'cm^2':
                yscale = 1.
            if focus['y-units'].item() == 'pb':
                yscale = 1.E-36
            if focus['y-units'].item() == 'zb':
                yscale = 1.E-45
            if focus['y-units'].item() == 'ub':
                yscale = 1.E-30
            if focus['x-units'].item() == 'MeV':
                xscale = 1e-3
            if focus['x-units'].item() == 'GeV':
                xscale = 1
            if focus['x-units'].item() == 'TeV':
                xscale = 1e3
            for i, s in enumerate(focus.y.item()):
                focus.y.item()[i] = s*yscale
            for i, s in enumerate(focus.x.item()):
                focus.x.item()[i] = s*zoom*xscale
            
            
            focus=focus.explode(['x','y'])
            #Plot area & neutrino background /testing
            if mypd.loc[mypd.experiment==j]['collaboration'].item()  == "neutrino":
                neutrino[j]=self.fig.varea(x = 'x', y1 = 'y', y2 =1e-50,fill_color="yellow",fill_alpha=0.2,name=j,source = ColumnDataSource(focus))
            else:    
                areaplots[j]=self.fig.varea(x = 'x', y1 = 'y', y2 =1e-10,fill_color="grey",fill_alpha=0.1,name=j,source = ColumnDataSource(focus))
                lineplots[j]=self.fig.line(x = 'x', y = 'y', line_width=2,line_color=palette[i%nbcolors],\
                        name=j,source = ColumnDataSource(focus))
            
            allplots = dict(areaplots.items()|lineplots.items()|neutrino.items())
            
            xmin, xmax, ymin, ymax = min(xmin,focus.x.min()), max(xmax,focus.x.max()),\
                                     min(ymin,focus.y.min()), max(ymax,focus.y.max())
            self.figlimits = {'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax}
     
            #Add labels /testing
            labels = LabelSet(x=focus.x.max(),y=(focus.y.min()), text='experiment',x_offset=-100, y_offset=0, source=ColumnDataSource(focus), render_mode='canvas')
            self.fig.add_layout(labels)
        
        self.draw(allplots,massunit)

    def draw(self,dico={},massunit="GeV"):
        fig = self.fig
        fig.x_range=Range1d(self.figlimits['xmin'], self.figlimits['xmax'])
        fig.y_range=Range1d(self.figlimits['ymin'], self.figlimits['ymax'])
        fig.extra_y_ranges = {"pb": Range1d(1e36*self.figlimits['ymin'], 1e36*self.figlimits['ymax'])}
       
        fig.yaxis.axis_label = r"WIMP-Nucleon Cross Section [cm²]"
        fig.xaxis.axis_label = f"WIMP Mass [{massunit}/c²]"
        fig.add_layout(LogAxis(y_range_name="pb",axis_label=r"WIMP-Nucleon Cross Section [pb]"),'right')
        #fig.yaxis.major_label_orientation = "vertical"        
        fig.axis.axis_label_text_font = 'helvetica' #aixs label font
        fig.axis.axis_label_text_font_size = '12pt'#axis label font size
        fig.axis.axis_label_text_font_style = 'normal' #axis label font style
        fig.axis.major_label_text_font_size = '11pt' #Tick label size
        
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
