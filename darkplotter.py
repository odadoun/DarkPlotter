from bokeh.plotting import figure, output_file, show,output_notebook,curdoc
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS, MultiSelect,CheckboxGroup,CheckboxGroup
from bokeh.models.glyphs import Line

from bokeh.layouts import column, row
import pandas as pd
from bokeh.io import curdoc
from bokeh.palettes import Spectral4
import requests
from pprint import pprint
from pandas.io.json import json_normalize
import ssl
import json
from bokeh.palettes import Spectral
#output_notebook(hide_banner=True)

ssl._create_default_https_context = ssl._create_unverified_context

class DMplotter():
    def __init__(self):
        self.figlimits = {}
        tooltips = """
        <b>Expriment</b>:$name<br>
        <b>M </b> = @y cm<sup>2</sup>  <br>
        <b>&sigma;</b> = @x GeV/c<sup>2</sup> <br>

        """
        self.allplots = {}
        self.figlimits = {}
        self.fig = figure(plot_width=800, plot_height=600,tooltips=tooltips,x_axis_type="log",y_axis_type='log')

    @staticmethod
    def reportexp():
        url='https://raw.githubusercontent.com/cajohare/NeutrinoFog/main/data/WIMPLimits/SDn/'
        cajoharefiles=['CDMS.txt','CDMSlite.txt','CRESST.txt','LUX.txt','PICASSO.txt','PandaX.txt','XENON100.txt','XENON1T-Migdal.txt','XENON1T.txt']
        d={'url':url,'exp':cajoharefiles}
        return d

    def getfig(self,):
        url=DMplotter.reportexp()['url']
        xmax, ymax = [-1.]*2
        xmin, ymin = [1.e6]*2
        palette = Spectral[len(DMplotter.reportexp()['exp'])]
        for i, expfile in enumerate(DMplotter.reportexp()['exp']):
            tmp = pd.read_csv(url+expfile,header=None,names=["x", "y"],sep='\t')
            exp=expfile.replace('.txt','')
            tmp=tmp[:-1]
            tmp['x']=tmp['x'].astype('float')
            tmp['y']=tmp['y'].astype('float')
            tmp=tmp.dropna()
            xmin, xmax, ymin, ymax = min(xmin,tmp.x.min()), max(xmax,tmp.x.max()), min(ymin,tmp.y.min()), max(ymax,tmp.y.max())
            self.allplots[exp]=self.fig.line(x = 'x', y = 'y', line_width=2,line_color=palette[i],name=exp, source = ColumnDataSource(tmp))
        self.figlimits = {'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax}
        return self.allplots

    def plot(self,plots):
        self.fig.x_range=Range1d(self.figlimits['xmin'], self.figlimits['xmax'])
        self.fig.y_range=Range1d(self.figlimits['ymin'], self.figlimits['ymax'])
        self.fig.xaxis.axis_label = r"$$\mathrm{\color{white}WIMP~Mass~GeV/c^{2}}$$"
        self.fig.yaxis.axis_label = r"$$\mathrm{\color{white}WIMP-Nucleon~Cross~Section~cm^2}$$"
        curdoc().theme = 'dark_minimal'

        checkbox = CheckboxGroup(labels=list(plots.keys()), active=list(range(len(plots))), width=100)
        callback = CustomJS(args=dict(lines=list(plots.values()), checkbox=checkbox),
        code="""
                for(var i=0; i<lines.length; i++){
                    lines[i].visible = checkbox.active.includes(i);
            }
        """)

        checkbox.js_on_change('active', callback)
        curdoc().theme = 'dark_minimal'
        layout = row(self.fig,checkbox)
        show(layout)
