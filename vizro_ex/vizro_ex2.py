import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import pandas as pd

# Read structured data:
df = pd.read_csv("~/Documents/div/7s/VV/test_data/vibration_test_data.csv", dtype={"Time": float, "Amplitude": float})

print(df.columns)

page = vm.Page(
    title="Vibration-Analysis Dashboard",
    components=[
        vm.Graph(id="line_plot", figure=px.line(df, x="Time", y="Amplitude")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="Amplitude")),
        vm.Graph(id="freq_dist", figure=px.fft(df)),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
