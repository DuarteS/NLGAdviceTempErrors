import os
import pickle
from datetime import timedelta
import pandas as pd
import openai
import myconstants

from TempAdvice.AnnotationClass import Annotation
from TempAdvice.Graphs import plot_online_errors

annotations = []


def _get_temp_reason_data(temp_csv, reason_csv):
    df = pd.read_csv(temp_csv, sep=',').dropna()
    print(df.head())

    df2 = pd.read_csv(reason_csv, sep=',').drop(['kastemperatuur'], axis=1).dropna()
    print(df2.head())
    df_errors = pd.concat([df2.set_index('local_time'), df.set_index('local_time')], axis=1, join='inner').reset_index()

    df_errors['kastemperatuur_status'] = df_errors['kastemperatuur']
    # df_errors['local_time'] = pd.to_datetime(df_errors['local_time'], format='%d/%m/%Y %I:%M %p')
    df_errors['local_time'] = pd.to_datetime(df_errors['local_time'], format='%d/%m/%Y %H:%M')
    df_errors['local_time'] = pd.to_datetime(df_errors['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')

    df_errors.loc[df_errors['kastemperatuur'] < df_errors['temperatuur_laag'], 'kastemperatuur_status'] = 0
    df_errors.loc[df_errors['kastemperatuur'] > df_errors['temperatuur_hoog'], 'kastemperatuur_status'] = 1

    df_errors[
        ['buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek', 'kastemperatuur']] = df_errors[
        ['buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek', 'kastemperatuur']].astype(float)
    return df_errors


def _getConnectedErrors(df_Errors):
    df_temp = pd.DataFrame(
        columns=['local_time', 'buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek',
                 'status_temperatuur', 'kastemperatuur', 'kastemperatuur_status'])
    df_Errors = df_Errors[df_Errors.status_temperatuur != 0]

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
            dict_of_errors[dictCount] = df_temp
            dictCount += 1
        df_temp = df_temp[0:0]

    return dict_of_errors


def _get_averages(temp_csv, reason_csv):
    connected_reason = _get_temp_reason_data(temp_csv, reason_csv)
    connected_errors = _getConnectedErrors(connected_reason)

    values = []

    for i in connected_errors:
        df = connected_errors[i]
        avg_info = [df["local_time"].min(), df["local_time"].max(), df["kastemperatuur"].mean(),
                    df["kastemperatuur_status"].mean(), df["wind_zijde_raamstand"].mean(), df["onderbuis"].mean(),
                    df["energiedoek"].mean()]
        values.append(avg_info)
    return values


def create_annotations(temp_csv, reason_csv):
    loaded_annotations = _load_annotations(myconstants.ANNOTATION_FILE)
    new_annotations = []

    averages = _get_averages(temp_csv, reason_csv)

    for avg in averages:
        new_annotations.append(Annotation(avg[0], avg[1], 'window', avg[2], avg[3], avg[4]))
        new_annotations.append(Annotation(avg[0], avg[1], 'pipe', avg[2], avg[3], avg[5]))
        new_annotations.append(Annotation(avg[0], avg[1], 'screen', avg[2], avg[3], avg[6]))

    existed = False
    for new_annotation in new_annotations:
        for load_annotation in loaded_annotations:
            if new_annotation.compare_basic(load_annotation):
                existed = True
                annotations.append(load_annotation)
                print("load")
        if not existed:
            new_annotation.calculate()
            annotations.append(new_annotation)
            existed = False
            print("create")

    for annotation in annotations:
        if annotation not in loaded_annotations:
            loaded_annotations.append(annotation)

    for anno in annotations:
        print(anno.__dict__)

    pickle.dump(loaded_annotations, open(myconstants.ANNOTATION_FILE, 'wb'))


def _load_annotations(file):
    loaded_annotations = []
    if os.path.exists(myconstants.ANNOTATION_FILE):
        pickle_load = pickle.load(open(file, 'rb'))
        for load in pickle_load:
            loaded_annotations.append(load)
        return loaded_annotations
    else:
        return []


def create_graph():
    create_annotations(myconstants.TEMPFILE, myconstants.REASONFILE)
    plot_online_errors(_get_temp_reason_data(myconstants.TEMPFILE, myconstants.REASONFILE), annotations)


create_graph()
