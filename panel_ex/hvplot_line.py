

#import hvplot.pandas
from bokeh.sampledata.degrees import data as deg


deg.head()

deg.plot.line(
    x='Year', 
    y=['Art and Performance', 'Business', 'Biology', 'Education', 'Computer Science'], 
    #label="Percent of Degrees Earned by Women", 
    legend='top', 
    height=500, 
    width=620
)


