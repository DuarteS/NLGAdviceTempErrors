from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

CSV_FILE = "../Coldfall/TotalData.csv"


def _get_dew_data(csv):
    df_temperature = pd.read_csv(csv, sep=',').drop(
        ['buitentemperatuur', 'absoluut vochtgehalte kaslucht boven doek','kastemperatuur meetbox onder', 'kastemperatuur boven doek'],
        axis=1).dropna()

    df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'], format='%d/%m/%Y %H:%M')
    df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')

    df_temperature[['energiedoek', 'kastemperatuur', 'kastemperatuur meetbox onder', 'kastemperatuur boven doek']] = df_temperature[['energiedoek', 'kastemperatuur', 'kastemperatuur meetbox onder', 'kastemperatuur boven doek']].astype(float)
    return df_temperature

