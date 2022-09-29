import pickle
from datetime import timedelta
import pandas as pd
import openai

from NewCode.Graphs import plot_online_errors

annotations = []
TEMPFILE = '../BeunCode/TempError3.csv'
REASONFILE = '../BeunCode/Reasons3.csv'


class Annotation(object):
    def __init__(self, start_time, end_time, annotation_type, temp, temp_status, value, result, text):
        self.temp_status = temp_status
        self.text = text
        self.result = result
        self.value = value
        self.temp = temp
        self.start_time = start_time
        self.end_time = end_time
        self.annotation_type = annotation_type

    def __init__(self, start_time, end_time, annotation_type, temp, temp_status, value):
        self.temp_status = temp_status
        self.value = value
        self.temp = temp
        self.start_time = start_time
        self.end_time = end_time
        self.annotation_type = annotation_type
        self.result = generate_result(self.annotation_type, self.temp_status, self.value)
        if self.result <= 5:
            self.text = generate_text(self.annotation_type, self.temp_status, self.result)

    def is_error(self):
        return True if 3 >= self.result else False


def generate_result(annotation_type: str, temperature_higher: int, value: float):
    if annotation_type == 'window':
        model = pickle.load(open('../MLModels/Window_model.sav', 'rb'))
    elif annotation_type == 'pipe':
        model = pickle.load(open('../MLModels/Pipe_model.sav', 'rb'))
    elif annotation_type == 'screen':
        model = pickle.load(open('../MLModels/Shadow_model.sav', 'rb'))
    else:
        return False

    result = model.predict([[temperature_higher, value]])[0]
    return result


def generate_text(annotation_type: str, temperature_status: int, result: int):
    if annotation_type == 'window':
        model = "davinci:ft-personal:gpt-3-davinci-gpttempwindows-small-2022-09-20-06-37-58"
        return "window error"
    elif annotation_type == 'pipe':
        model = "davinci:ft-personal:gpt-3-davinci-gpttempshadows-small-2022-09-20-06-43-46"
        return "pipe error"
    elif annotation_type == 'screen':
        model = "davinci:ft-personal:gpt-3-davinci-gpttemppipes-small-2022-09-20-06-59-50"
        return "screen error"
    else:
        return False

    prompt = 'Temp ' + str(temperature_status) + ', Item: ' + annotation_type + ', Value:' + str(result) + '\n\n---\n\n'
    text = _gen_text(prompt, model)
    return text


def _gen_text(prompt, model):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0.4,
        max_tokens=30,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["END"]
    )["choices"][0]['text']
    return response


def _get_temp_reason_data(temp_csv, reason_csv):
    df = pd.read_csv(temp_csv, sep=';').dropna()

    df2 = pd.read_csv(reason_csv, sep=';').drop(['kastemperatuur'], axis=1).dropna()

    df_Errors = pd.concat([df2.set_index('local_time'), df.set_index('local_time')], axis=1, join='inner').reset_index()

    df_Errors['kastemperatuur_status'] = df_Errors['kastemperatuur']
    df_Errors['local_time'] = pd.to_datetime(df_Errors['local_time'], format='%d/%m/%Y %I:%M %p')
    df_Errors['local_time'] = pd.to_datetime(df_Errors['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')
    df_Errors[['buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek', 'kastemperatuur']] = df_Errors[
        ['buitentemperatuur', 'onderbuis', 'wind_zijde_raamstand', 'energiedoek', 'kastemperatuur']].astype(float)

    df_Errors.loc[df_Errors['kastemperatuur'] < df_Errors['temperatuur_laag'], 'kastemperatuur_status'] = 0
    df_Errors.loc[df_Errors['kastemperatuur'] > df_Errors['temperatuur_hoog'], 'kastemperatuur_status'] = 1

    return df_Errors


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


def get_averages(temp_csv, reason_csv):
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


def create_annotations():
    averages = get_averages(TEMPFILE, REASONFILE)

    for avg in averages:
        annotations.append(Annotation(avg[0], avg[1], 'window', avg[2], avg[3], avg[4]))
        annotations.append(Annotation(avg[0], avg[1], 'pipe', avg[2], avg[3], avg[5]))
        annotations.append(Annotation(avg[0], avg[1], 'screen', avg[2], avg[3], avg[6]))

    for anno in annotations:
        print(anno.__dict__)


def create_graph():
    create_annotations()
    plot_online_errors(_get_temp_reason_data(TEMPFILE, REASONFILE), annotations)


create_graph()
