
import taipy as tp
import pandas as pd


# Create a dataframe with sample data
data = {'Year': [2015, 2016, 2017, 2018, 2019],
        'Sales': [100, 150, 200, 180, 250],
        'Profit': [50, 75, 100, 90, 120]}
df = pd.DataFrame(data)

# Create a line chart using Taipy
tp.line_chart(df, x='Year', y='Sales')

# Display the dashboard
tp.show()
