from datetime import timedelta
import pandas as pd
from datetime import datetime, timedelta
import pandas as pd
from plottesting import testingPlot


def getCSV():
    df = pd.read_csv('TempError.csv', sep=';').drop(['temperatuur_hoog', 'temperatuur_laag'], axis=1).dropna()
    # print(df)

    df2 = pd.read_csv('Reasons.csv', sep=';').drop(['kastemperatuur'], axis=1).dropna()
    # print(df2)

    df_Errors = pd.concat([df2.set_index('local_time'), df.set_index('local_time')], axis=1, join='inner').reset_index()
    df_Errors = df_Errors[df_Errors.status_temperatuur != 0]

    df_Errors['local_time'] = pd.to_datetime(df_Errors['local_time'], format='%d/%m/%Y %I:%M %p')
    df_Errors['local_time'] = pd.to_datetime(df_Errors['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')
    df_Errors[['buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek', 'kastemperatuur']] = df_Errors[
        ['buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek', 'kastemperatuur']].astype(float)

    # print(df_Errors)
    return df_Errors


def getConnectedErrors(df_Errors):
    df_temp = pd.DataFrame(
        columns=['local_time', 'buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek',
                 'status_temperatuur', 'kastemperatuur'])
    dictCount = 0
    dict_of_errors = {}

    time = df_Errors.iloc[0].local_time

    for row in df_Errors.iterrows():
        if time <= row[1].local_time:
            for row2 in df_Errors.iterrows():
                if row2[1].local_time == time + timedelta(minutes=5):
                    df_temp.loc[len(df_temp.index)] = row2[1]
                    time = row2[1].local_time
                elif row2[1].local_time > time + timedelta(minutes=5):
                    df_temp.loc[len(df_temp.index)] = row[1]
                    time = row2[1].local_time
                    break
        df_temp = df_temp.sort_values(by=['local_time'])
        if len(df_temp.index) >= 5:
            testingPlot(df_temp['local_time'].to_numpy(), df_temp['kastemperatuur'].to_numpy())
            dict_of_errors[dictCount] = df_temp
            dictCount += 1
        df_temp = df_temp[0:0]

    # print(dict_of_errors)
    return dict_of_errors


def getAverages(df):
    Avg_info = [df["local_time"].min(), df["local_time"].max(), df["kastemperatuur"].mean(),
                df["wind_zijde_raamstand"].mean(), df["onderbuis"].mean(),
                df["energiedoek"].mean()]
    # print(Avg_info)
    return Avg_info


def getValues():
    df_Errors = getCSV()
    split_errors = getConnectedErrors(df_Errors)
    values = []
    for group in split_errors:
        values.append(getAverages(split_errors[group]))
    return values
