from bokeh.plotting import figure, output_file, show,output_notebook,curdoc,save
from bokeh.models import Range1d, ColumnDataSource, Column, Select, CustomJS, MultiSelect,CheckboxGroup,CheckboxGroup,LabelSet,LinearAxis,LogAxis,Slider,Label,Dropdown
from bokeh.models.glyphs import Line
from bokeh.models import Legend
from bokeh.themes import Theme
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.palettes import Category10
from bokeh.models import FixedTicker

import pandas as pd
import requests
from pprint import pprint
from pandas.io.json import json_normalize
import ssl
import json
from bs4 import BeautifulSoup as bs
import numpy as np
import sys
import os
output_notebook(hide_banner=True)


ssl._create_default_https_context = ssl._create_unverified_context

class DMdata():
    def __init__(self,**kwargs):
        self.path = kwargs.get('path','./json')
        self.mypandas = pd.DataFrame()
        self.uploaddata(path=self.path)

    def uploaddata(self,**kwargs):
        path = kwargs.get('path')
        files = []
        for dirpath,_,filenames in os.walk(path):
            for f in filenames:
                files.append(os.path.abspath(os.path.join(dirpath, f)))
        for ifile in files:
            tmp = pd.read_json(ifile)
            tmp = tmp.apply(lambda x: x.to_list() if x.name in ['x','y'] else x[0])
            if self.mypandas.empty:
                self.mypandas = pd.DataFrame(data={i:[tmp[i]] for i in tmp.index})
            else:
#                if tmp['experiment'] not in self.mypandas.experiment.to_list():
                self.mypandas = pd.concat([self.mypandas,pd.DataFrame(data={i:[tmp[i]] for i in tmp.index})])
        self.mypandas = self.mypandas.loc[~self.mypandas['experiment'].isin([''])]

    def get_metadata(self):
        return self.mypandas.drop(columns=['x','y']).set_index('experiment')

    def get_data(self):
        return self.mypandas[['experiment','x','y']].set_index('experiment')
    
    def get_pandas(self):
        return self.mypandas.set_index("experiment")

    def get_experiment(self,collaboration="",experiment="",label=""):
            
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

        if label != "":
            collab = self.mypandas
#            exp = collab[collab["label"].apply(lambda x : any(k in x for k in label))]
            exp = collab[collab["label"].isin(label)]
                
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
        TOOLS = "pan,wheel_zoom,reset,save"
        self.fig = figure(plot_width=1200, plot_height=600,tooltips=self.tooltips, tools=TOOLS,x_axis_type="log",y_axis_type='log',sizing_mode="scale_width",outline_line_color='black', outline_line_width=1)
        if not isinstance(mypandas,list):
            mypd =[ mypandas ]
        mypd = pd.concat(mypd)
#        if mypd.index.name == 'experiment':
#            mypd = mypd.reset_index()
#        experiments=mypd.experiment.unique()
#        print(experiments)
        xmax, ymax = 2*[-1.]
        xmin, ymin = 2*[1.e6]
        xunit = massunit
        zoom = 1.
        nbcolors=7
        palette = Category10[nbcolors]
        allplots={}
        lineplots={}
        areaplots={}
        bgplots={}
        bgareaplots={}
        labels={}
        slider={}
        callback={}
        theta=0
        if xunit == "MeV":
            zoom = 1e3
        elif xunit == "GeV":
            zoom = 1
        elif xunit == "TeV":
            zoom = 1e-3
        else:
            print("Please choose correct massunit")
            sys.exit()
            
        focus=mypd.loc[mypd.experiment=="LZ"]
#        print(focus)

        icolor = 0

        for index,row in mypd.iterrows():

            print("-----",row["label"])
            
            if row['y-units'] == 'fb':
                yscale = 1.E-39
            if row['y-units'] == 'cm^2' or row['y-units'] == 'cm2':
                yscale = 1.
            if row['y-units'] == 'pb':
                yscale = 1.E-36
            if row['y-units'] == 'zb':
                yscale = 1.E-45
            if row['y-units'] == 'ub':
                yscale = 1.E-30
            if row['x-units'] == 'MeV':
                xscale = 1e-3
            if row['x-units'] == 'GeV':
                xscale = 1
            if row['x-units'] == 'TeV':
                xscale = 1e3
            for i, s in enumerate(row.y):
                row.y[i] = s*yscale
            for i, s in enumerate(row.x):
                row.x[i] = s*zoom*xscale

            rowxy = {'x': row['x'], 'y': row['y']}

            #Plot Range
            #xmin, xmax, ymin, ymax = min(xmin,focus.x.min()), max(xmax,focus.x.max()),\
            #                         min(ymin,focus.y.min()), max(ymax,focus.y.max())
            #self.figlimits = {'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax}
            if self.figlimits == {}:
                self.figlimits = {'xmin':5e-1, 'xmax':1e3, 'ymin':1e-50, 'ymax':1e-43}
            label = row["label"]
            #Plot area & neutrino background /testing
            #Plot Labels & slider /testing
            if row['category']  == "Background":
                bgareaplots[label]=self.fig.varea(x = 'x', y1 = 'y', y2 =1e-50,fill_color="yellow",fill_alpha=0.4,name=label,source = ColumnDataSource(rowxy))
                bgplots[label]=self.fig.line(x = 'x', y = 'y',line_width=1,line_color="yellow",line_alpha=0.8,name=label,source = ColumnDataSource(rowxy),line_dash="dashed")
                labels[label] = Label(x=0.6,y=1e-49, text=label,x_offset=0, y_offset=0,
                 text_font='arial',text_font_size='12pt',text_color="black",text_font_style="bold",render_mode='canvas')
            elif row['category']  == "Limit":    
                areaplots["Area"+label]=self.fig.varea(x = 'x', y1 = 'y', y2 =1e-10,fill_color=(232,243,226),fill_alpha=1,name=label,source = ColumnDataSource(rowxy))
                areaplots["Area"+label].level= 'underlay'
                lineplots[label]=self.fig.line(x = 'x', y = 'y', line_width=2,line_color=palette[icolor%nbcolors],name=label,source = ColumnDataSource(rowxy))
            elif row['category']  == "Sensitivity":
                lineplots[label]=self.fig.line(x = 'x', y = 'y', line_width=2,line_color=palette[icolor%nbcolors],name=label,source = ColumnDataSource(rowxy), line_dash='dashed')

            #Adding Sliders
            #slider[label]=Slider(start=0.5*focus.x.min(),end=2*focus.x.max(),value=focus.x.max(),step=-0.05*(focus.x.min()-focus.x.max()),title=label)
            slider[label]=Slider(start=1,end=len(rowxy['x']),value=len(rowxy['x']),step=1,title=label, sizing_mode="stretch_both")
            #Adding Labels
            labels[label] = Label(x=max(rowxy['x']),y=(rowxy['y'][-1]), text=label,x_offset=0, y_offset=0, text_font='arial',text_font_style="bold",text_color=palette[icolor%nbcolors],text_font_size='12pt', angle=theta,render_mode='canvas',text_align="left")
            #Adding Link/Call back
            labels[label].text_align = "right"
            callback[label]=CustomJS(args=dict(source=ColumnDataSource(rowxy),xposition=slider[label],lable=labels[label],plot=self.fig),
                                     code = """
                const data = source.data;
                var idx = xposition.value;
                var x = data['x'][idx];
                var y = data['y'][idx];
                var angle = Math.atan2(Math.log10(data['y'][idx])-Math.log10(data['y'][idx-1]),Math.log10(data['x'][idx])-Math.log10(data['x'][idx-1]));
                lable['angle'] = 0; //angle/3;
                lable['x'] = 0.85*x;
                lable['y'] = 0.85*y;
//                lable['x'] = x;
//                lable['y'] = y;
//              lable['x_offset']=0.1*data['x'][idx];
//              lable['y_offset']=0.1*data['y'][idx];
                lable.change.emit();
                """
            )
            slider[label].js_on_change('value', callback[label])


            #allplots = dict(areaplots.items()|lineplots.items()|bgplots.items()|bgareaplots.items())
            allplots = dict(lineplots.items()|bgplots.items())
            
            

            #Add labels /testing
            self.fig.add_layout(labels[label])
            icolor = icolor + 1
            
        self.draw(allplots,slider,massunit)

    def draw(self,dico={},slider={},massunit="GeV"):
        fig = self.fig
        fig.x_range=Range1d(self.figlimits['xmin'], self.figlimits['xmax'])
        fig.y_range=Range1d(self.figlimits['ymin'], self.figlimits['ymax'])
        fig.extra_y_ranges = {"pb": Range1d(1e36*self.figlimits['ymin'], 1e36*self.figlimits['ymax'])} #Second y Aixs
       
        fig.yaxis.axis_label = r"WIMP-Nucleon Cross Section [cm²]"
        fig.xaxis.axis_label = f"WIMP Mass [{massunit}/c²]"
        fig.add_layout(LogAxis(y_range_name="pb",axis_label=r"WIMP-Nucleon Cross Section [pb]"),'right')
        #fig.yaxis.major_label_orientation = "vertical"        
        fig.axis.axis_label_text_font = 'times' #aixs label font
        fig.axis.axis_label_text_font_size = '16pt'#axis label font size
        fig.axis.axis_label_text_font_style = 'bold' #axis label font style
        fig.axis.major_label_text_font_size = '15pt' #Tick label size
        fig.xaxis.ticker = FixedTicker(ticks=[0.1,0.2,0.5,1,2,3,4,5,10,100,1000])
        
        #Plot Legend
        legend_it=[]
        for k,v in dico.items():
            legend_it.append((k, [v]))
        legend = Legend(items=legend_it)
        legend.click_policy="hide"
        fig.add_layout(legend, 'right')

        ''' #Olivier's Code
        #curdoc().theme = Theme(filename="./theme.yml")

        #checkbox = CheckboxGroup(labels=list(dico.keys()), active=list(range(len(dico))), width=100)
        #callback = CustomJS(args=dict(lines=list(dico.values()), checkbox=checkbox),
        #code="""
        #        for(var i=0; i<lines.length; i++){
        #            lines[i].visible = checkbox.active.includes(i);
        #    }
        #""")
        
        #checkbox.js_on_change('active', callback)
        #curdoc().theme = Theme(filename="./theme.yml")
        #layout = row(fig,checkbox)
        # 

        slider = Slider(start=0, end=10, value=1, step=.1, title="Stuff")
        slider.js_on_change("value", CustomJS(code="""
        console.log('slider: value=' + this.value, this.toString())
            """))
            

        layout =row(fig,slider)

        layout=fig
        
        show(column(fig,column(slider, width=100)))
        '''
        sliders=[]
        for key in slider:
            sliders.append(slider[key])
        fig = row(fig,column(sliders,sizing_mode="fixed", height=600, width=100),sizing_mode="stretch_both")

        output_file(filename="DarkPlotter.html", title="WIMP Exclusion Plot")
        show(fig)
        save(fig)
