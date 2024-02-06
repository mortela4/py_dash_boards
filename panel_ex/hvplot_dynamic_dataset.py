import panel as pn
import hvplot.pandas
import param

# Load Data
from bokeh.sampledata.autompg import autompg_clean as df

# create a self-contained dashboard class
class InteractiveDashboard(param.Parameterized):
    cylinders =  param.Integer(label='Cylinders', default=4, bounds=(4, 8))
    mfr = param.ListSelector(
        label='MFR',
        default=['ford', 'chevrolet', 'honda', 'toyota', 'audi'], 
        objects=['ford', 'chevrolet', 'honda', 'toyota', 'audi'], precedence=0.5)
    yaxis = param.Selector(label='Y axis', objects=['hp', 'weight'])

    
    @param.depends('cylinders', 'mfr', 'yaxis')
    def plot(self):
        return (
            df[
                (df.cyl == self.cylinders) & 
                (df.mfr.isin(self.mfr))
            ]
            .groupby(['origin', 'mpg'])[self.yaxis].mean()
            .to_frame()
            .reset_index()
            .sort_values(by='mpg')  
            .reset_index(drop=True)
            .hvplot(x='mpg', y=self.yaxis, by='origin', color=["#ff6f69", "#ffcc5c", "#88d8b0"], line_width=6, height=400)
        )
dashboard = InteractiveDashboard()

# Layout using Template
template = pn.template.FastListTemplate(
    title="Interactive DataFrame Dashboards with param.depends", 
    sidebar=[pn.Param(dashboard.param, widgets={'mfr': pn.widgets.ToggleGroup,'yaxis': pn.widgets.RadioButtonGroup})],
    main=[dashboard.plot],
    accent_base_color="#88d8b0",
    header_background="#88d8b0",
)

template.servable()

template.show()
