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


def _get_data(data_csv):
    headers = ['buitentemperatuur', 'energiedoek', 'absoluut vochtgehalte kaslucht boven doek', 'kastemperatuur',
               'absoluut vochtgehalte meetbox onder', 'kastemperatuur meetbox onder', 'kastemperatuur boven doek']
    try:
        i = headers.index(SHOCK_TYPE)
        del headers[i]
    except ValueError:
        print("not found")

    df_data = pd.read_csv(data_csv, sep=',').drop(headers, axis=1).dropna()

    df_data['local_time'] = pd.to_datetime(df_data['local_time'], format='%d/%m/%Y %H:%M')
    df_data['local_time'] = pd.to_datetime(df_data['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')

    df_data[SHOCK_TYPE] = df_data[SHOCK_TYPE].astype(float)
    return df_data


def _find_shock_connections(df_data):
    dif_p_5m = (max_var_hour / shock_time) * 5
    df_data_shock = pd.DataFrame(columns=['start_index', 'end_index'])

    for curr_row in df_data.iterrows():
        test_row = curr_row
        break

    for curr_row in df_data.iterrows():
        test_temp = test_row[1][SHOCK_TYPE]
        curr_temp = curr_row[1][SHOCK_TYPE]

        temp_increase = abs(test_temp-curr_temp)

        if temp_increase >= dif_p_5m:
            EndIndex = curr_row[0]
            StartIndex = df_data[
                df_data['local_time'] == curr_row[1].local_time - timedelta(hours=00, minutes=shock_time)].index.values
            time = shock_time
            while not StartIndex:
                time = time - 5
                StartIndex = df_data[df_data['local_time'] == curr_row[1].local_time -
                                     timedelta(hours=00, minutes=time)].index.values
            StartIndex = StartIndex[0]

            time_group = df_data.iloc[StartIndex: EndIndex]

            max_var = time_group[SHOCK_TYPE].max()
            min_var = time_group[SHOCK_TYPE].min()

            added = False

            if max_var - min_var >= max_var_hour:

                for temp_row in df_data_shock.iterrows():
                    test_start_time = temp_row[1].start_index
                    test_end_time = temp_row[1].end_index

                    if test_start_time < StartIndex < test_end_time:
                        df_data_shock.loc[temp_row[0], 'end_index'] = EndIndex
                        added = True

                if not added:
                    df_data_shock.loc[df_data_shock.shape[0]] = [StartIndex, EndIndex]

        test_row = curr_row

    return df_data_shock


def _get_shock_plot_data(df_temp, df_shock_connected):
    df_shock_plot_data = pd.DataFrame(columns=['start_time', 'end_time', 'max_var', 'min_var'])

    for curr_row in df_shock_connected.iterrows():
        time_group = df_temp.iloc[curr_row[1].start_index: curr_row[1].end_index]

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


def _get_shock_analytics_data(df_temp, df_shock_connected):
    for curr_row in df_shock_connected.iterrows():
        time_group = df_temp.iloc[curr_row[1].start_index: curr_row[1].end_index]
        max_var = time_group[SHOCK_TYPE].max()
        min_var = time_group[SHOCK_TYPE].min()
        start_time = time_group['local_time'].min()
        end_time = time_group['local_time'].max()

        duration_hours = (end_time-start_time) / pd.timedelta(hours=1)
        duration_minutes = (end_time - start_time) / pd.timedelta(minutes=1)

        min_max_differance = max_var - min_var

        avg_change_p5m = (min_max_differance / duration_minutes) * 5

        if min_var == 0:
            sensors_down = True
        else:
            sensors_down = False

        overall_differance = 0
        peaks = 0
        curr_direction = "none"

        cal_temp = time_group[SHOCK_TYPE].iat[0]
        for timegroup_row in time_group.iterrows():
            row_temp = timegroup_row[1][SHOCK_TYPE]

            overall_differance = overall_differance + abs(cal_temp-row_temp)

            if cal_temp-0.5 > row_temp:
                curr_direction = "down"
            elif cal_temp+0.5 < row_temp and (curr_direction == "down" or curr_direction == "none"):
                peaks = peaks + 1
                curr_direction = "up"

            # Add short time raise

            cal_temp = row_temp

        print(peaks)


df = _get_data(TEMP_FILE)
shock_connections = _find_shock_connections(df)
_get_shock_analytics_data(df, shock_connections)
# shock_plot_data = _get_shock_plot_data(df, shock_connections)
# plot_online_shock(df, shock_plot_data)
