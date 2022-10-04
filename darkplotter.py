
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
        self.mypandas = pd.DataFrame()

    def getmetadataOLD(self,**kwargs):
        '''
        getmetadata : retrieve metedata information and retrieve a pandas
        url, folder in the url, files
        '''
        url=kwargs.get('url','https://github.com/odadoun/DarkPlotter/tree/main/WIMPLimits/')
        folder=kwargs.get('folder','SDp/')
        res = requests.get(url+folder)
        soup = bs(res.text, 'lxml')
        nav = soup.find_all('a',class_="js-navigation-open")
        files = [ i.text for i in nav if '.txt' in i.text  ]
        if files:
            path = 'https://raw.githubusercontent.com/odadoun/DarkPlotter/main/WIMPLimits/'+folder
        else:
            files = url.split('/')[-1]
            path =  url.replace(files,'')
            files = [files]
        exp_pd=pd.DataFrame({'url':path,'files':files})
        return exp_pd

    def getdataOLD(self,**kwargs):
        '''
        retrieve data from metadata
        '''
        mypd = self.getmetadata(**kwargs)
        exp_pd = pd.DataFrame(columns = ['exp','x','y'])
        dropexp = ['DEAP-3600.txt','DEAP3600.txt']
        mypd = mypd.loc[~mypd.files.isin(dropexp)]
        pathfile = mypd.apply(lambda x:x['url']+x['files'],axis = 1)
        for i, file in enumerate(pathfile):
            exp = file.split('/')[-1].replace('.txt','')
            tmp = pd.read_csv(file,comment='#',names=['x','y'],sep='\s+', engine='python')
            tmp['x'] = tmp['x'].astype('float')
            tmp['y'] = tmp['y'].astype('float')
            if i==0:
                exp_pd['exp']=[exp]
                exp_pd['x']=[tmp['x'].to_list()]
                exp_pd['y']=[tmp['y'].to_list()]
            else:
                exp_pd=pd.concat([exp_pd,pd.DataFrame({'exp':exp,'x':[tmp['x'].to_list()],'y':[tmp['y'].to_list()]})])
        return exp_pd.reset_index(drop=True)

    def githubpath2raw(self,**kwargs):
        url=kwargs.get('url','https://github.com/odadoun/DarkPlotter/tree/NewGraphicToAdd/json/')
        urlraw='https://raw.githubusercontent.com/odadoun/DarkPlotter/NewGraphicToAdd/json/'
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
        default = 'https://raw.githubusercontent.com/odadoun/DarkPlotter/NewGraphicToAdd/json/SI-CDMS-CDMS%20II%2C%20Reanalysis%20LT-5c87c458d484949dedf45757e811d495.json'
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
        if mypd.index=='experiment':
            mypd = mypd.reset_index()
        self.fig = figure(plot_width=800, plot_height=600,tooltips=self.tooltips,x_axis_type="log",y_axis_type='log')
        if not isinstance(mypandas,list):
            mypd =[ mypandas ]
        mypd = pd.concat(mypd)
        experiments=mypd.experiment.unique()
        xmax, ymax = 2*[-1.]
        xmin, ymin = 2*[1.e6]
        nbcolors=7
        palette = Category10[nbcolors]
        allplots={}
        for i,j in enumerate(experiments):
            focus=mypd.loc[mypd.experiment==j]
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
