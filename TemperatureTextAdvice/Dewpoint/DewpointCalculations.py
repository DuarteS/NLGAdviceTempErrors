from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

TEMP_DIFF = 0.5
CSV_FILE = "../Dewpoint/Dewpoint.csv"


def _get_dew_data(csv):
    df_dew = pd.read_csv(csv, sep=',').dropna()

    df_dew['local_time'] = pd.to_datetime(df_dew['local_time'], format='%d/%m/%Y %I:%M %p')
    df_dew['local_time'] = pd.to_datetime(df_dew['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')

    df_dew[['dauwpuntstemp', 'kastemperatuur', 'plant']] = df_dew[['dauwpuntstemp', 'kastemperatuur', 'plant']].astype(
        float)
    return df_dew


def _find_errors(df_dewpoints):
    df_dew_errors = pd.DataFrame(columns=['start_time', 'end_time', 'type', 'start_type', 'start_dew'])

    for points in df_dewpoints.iterrows():
        dewpoint = points[1]["dauwpuntstemp"]
        kastemp = points[1]["kastemperatuur"]
        planttemp = points[1]["plant"]
        time = points[1]["local_time"]

        updated = False

        if kastemp - dewpoint <= TEMP_DIFF:

            for value in df_dew_errors.iterrows():
                if value[1]['type'] == "kas" and value[1]['start_time'] < time <= value[1]['end_time']:
                    df_dew_errors.loc[value[0], "end_time"] = time + timedelta(hours=00, minutes=5)

                    nparray = np.append([df_dew_errors.at[value[0], 'start_type']], kastemp)
                    df_dew_errors.at[value[0], 'start_type'] = [nparray]

                    nparray = np.append([df_dew_errors.at[value[0], 'start_dew']], dewpoint)
                    df_dew_errors.at[value[0], 'start_dew'] = [nparray]

                    updated = True
            if not updated:
                df_dew_errors.loc[df_dew_errors.shape[0]] = [time, time + timedelta(hours=00, minutes=5),
                                                             "kas", [np.array(kastemp)], [np.array(dewpoint)]]

        if planttemp - dewpoint <= TEMP_DIFF:

            for value in df_dew_errors.iterrows():
                if value[1]['type'] == "plant" and value[1]['start_time'] < time <= value[1]['end_time']:
                    df_dew_errors.loc[value[0], "end_time"] = time + timedelta(hours=00, minutes=5)

                    nparray = np.append([df_dew_errors.at[value[0], 'start_type']], planttemp)
                    df_dew_errors.at[value[0], 'start_type'] = nparray

                    nparray = np.append([df_dew_errors.at[value[0], 'start_dew']], dewpoint)
                    df_dew_errors.at[value[0], 'start_dew'] = nparray

                    updated = True
            if not updated:
                df_dew_errors.loc[df_dew_errors.shape[0]] = [time, time + timedelta(hours=00, minutes=5),
                                                             "plant", np.array([planttemp]), np.array([dewpoint])]


    return df_dew_errors


def plot_online_shock(df_data, df_dew):
    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = px.line(df_data, x='local_time', y=['dauwpuntstemp', 'kastemperatuur', 'plant'])

    subfig.add_traces(fig.data)
    subfig.layout.xaxis.title = "Time"
    subfig.layout.yaxis.title = "Temperature"

    for shock in df_dew.iterrows():
        print(shock[1]["start_dew"])
        subfig.add_shape(type="rect",
                         x0=shock[1]["start_time"], y0=shock[1]["start_dew"][0] - 1, x1=shock[1]["end_time"],
                         y1=shock[1]["start_type"][0] + 1,
                         line=dict(color="Red"),
                         )
    subfig.update_shapes(dict(xref='x', yref='y'))

    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()


df = _get_dew_data(CSV_FILE)
plot_online_shock(df, _find_errors(df))
