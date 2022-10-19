from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

max_var_hour = 5
shock_time = 60
TEMP_FILE = "../TempShock/TotalData.csv"
SHOCK_TYPE = "kastemperatuur"  # "absoluut vochtgehalte meetbox onder" / "kastemperatuur"


def _get_temp_data(temp_csv):
    headers = ['buitentemperatuur', 'energiedoek', 'absoluut vochtgehalte kaslucht boven doek', 'kastemperatuur',
               'absoluut vochtgehalte meetbox onder', 'kastemperatuur meetbox onder', 'kastemperatuur boven doek']
    try:
        i = headers.index(SHOCK_TYPE)
        del headers[i]
    except ValueError:
        print("not found")

    df_temperature = pd.read_csv(temp_csv, sep=',').drop(headers, axis=1).dropna()

    df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'], format='%d/%m/%Y %H:%M')
    df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')

    df_temperature[SHOCK_TYPE] = df_temperature[SHOCK_TYPE].astype(float)
    return df_temperature


def _find_shock_connections(df_temp):
    dif_p_5m = (max_var_hour / shock_time) * 5
    df_temp_shock = pd.DataFrame(columns=['start_index', 'end_index'])

    for curr_row in df_temp.iterrows():
        test_row = curr_row
        break

    for curr_row in df_temp.iterrows():
        test_temp = test_row[1][SHOCK_TYPE]
        curr_temp = curr_row[1][SHOCK_TYPE]
        temp_increase = 0

        if curr_temp >= test_temp:
            temp_increase = curr_temp - test_temp
        elif test_temp > curr_temp:
            temp_increase = test_temp - curr_temp

        if temp_increase >= dif_p_5m:
            EndIndex = curr_row[0]
            StartIndex = df_temp[
                df_temp['local_time'] == curr_row[1].local_time - timedelta(hours=00, minutes=shock_time)].index.values
            time = shock_time
            while not StartIndex:
                time = time - 5
                StartIndex = df_temp[df_temp['local_time'] == curr_row[1].local_time -
                                     timedelta(hours=00, minutes=time)].index.values
            StartIndex = StartIndex[0]

            time_group = df_temp.iloc[StartIndex: EndIndex]

            max_var = time_group[SHOCK_TYPE].max()
            min_var = time_group[SHOCK_TYPE].min()

            added = False

            if max_var - min_var >= max_var_hour:

                for temp_row in df_temp_shock.iterrows():
                    test_start_time = temp_row[1].start_index
                    test_end_time = temp_row[1].end_index

                    if test_start_time < StartIndex < test_end_time:
                        df_temp_shock.loc[temp_row[0], 'end_index'] = EndIndex

                        added = True
                        break

                if not added:
                    df_temp_shock.loc[df_temp_shock.shape[0]] = [StartIndex, EndIndex]

        test_row = curr_row

    print(df_temp_shock.head(20))
    return df_temp_shock


def _get_shock_plot_data(df_temp, df_shock_connected):
    df_shock_plot_data = pd.DataFrame(columns=['start_time', 'end_time', 'max_var', 'min_var'])
    for curr_row in df_shock_connected.iterrows():
        time_group = df_temp.iloc[curr_row[1].start_index: curr_row[1].end_index]

        print(time_group)
        start_time = time_group['local_time'].min()
        end_time = time_group['local_time'].max()

        max_var = time_group[SHOCK_TYPE].max()
        min_var = time_group[SHOCK_TYPE].min()

        df_shock_plot_data.loc[df_shock_plot_data.shape[0]] = [start_time, end_time, max_var, min_var]

    return df_shock_plot_data


def plot_online_shock(df_data, df_shock):
    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = px.line(df_data, x='local_time', y=SHOCK_TYPE)

    subfig.add_traces(fig.data)
    subfig.layout.xaxis.title = "Time"
    subfig.layout.yaxis.title = SHOCK_TYPE

    for shock in df_shock.iterrows():
        subfig.add_shape(type="rect",
                         x0=shock[1]["start_time"], y0=shock[1]["min_var"] - 0.5, x1=shock[1]["end_time"],
                         y1=shock[1]["max_var"] + 0.5,
                         line=dict(color="Red"),
                         )
    subfig.update_shapes(dict(xref='x', yref='y'))

    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()


def text_generation(prompt):
    response = openai.Completion.create(
        model="davinci:ft-personal:shockmove-2022-10-18-15-22-14",
        prompt=prompt + "\n-",
        temperature=1,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["[]"]
    )["choices"][0]['text']
    return response


df = _get_temp_data(TEMP_FILE)
shock_connections = _find_shock_connections(df)
shock_plot_data = _get_shock_plot_data(df, shock_connections)
plot_online_shock(df, shock_plot_data)
