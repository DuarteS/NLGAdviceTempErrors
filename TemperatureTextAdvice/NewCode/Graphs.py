import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def plot_online_errors(df, annotations):
    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = px.line(df, x='local_time', y=['onderbuis', 'wind_zijde_raamstand', 'energiedoek'])
    fig2 = px.line(df, x='local_time', y=['kastemperatuur', 'temperatuur_hoog', 'temperatuur_laag'])

    fx = np.array([])
    fy = np.array([])
    ft = np.array([])

    for annotation in annotations:
        if annotation.is_error() and annotation.text != "":
            fx = np.append(fx, annotation.start_time)
            fy = np.append(fy, annotation.value)
            ft = np.append(ft, annotation.text + ' ' + str(annotation.result))

    fig.add_trace(go.Scatter(
        x=fx,
        y=fy,
        mode="markers+text",
        name="Annotations",
        text=ft,
        textposition="bottom center"
    ))

    fig2.update_traces(yaxis="y2")

    subfig.add_traces(fig.data + fig2.data)
    subfig.layout.xaxis.title = "Time"
    subfig.layout.yaxis.title = "Reasons values"
    subfig.layout.yaxis2.type = "log"
    subfig.layout.yaxis2.title = "Temperature"

    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()
