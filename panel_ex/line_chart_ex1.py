import pandas as pd
import panel as pn
import hvplot.pandas

# Create a sample dataframe
data = {'Year': [2015, 2016, 2017, 2018, 2019],
        'Sales': [100, 150, 200, 180, 250]}
df = pd.DataFrame(data)

# Create a line chart using hvplot
line_chart = df.hvplot.line(x='Year', y='Sales')

# Create a Panel dashboard
dashboard = pn.Column(line_chart)

# Display the dashboard
dashboard.show()

