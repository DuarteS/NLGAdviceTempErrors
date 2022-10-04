import pickle

import openai


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

    def calculate(self):
        self.result = generate_result(self.annotation_type, self.temp_status, self.value)
        if self.result <= 3:
            self.text = generate_text(self.annotation_type, self.temp_status, self.result)
        else:
            self.text = ''

    def is_error(self):
        return True if 3 >= self.result else False

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def compare_basic(self, other):
        if self.temp_status == other.temp_status \
                and self.value == other.value \
                and self.temp == other.temp \
                and self.start_time == other.start_time \
                and self.end_time == other.end_time \
                and self.annotation_type == other.annotation_type:
            return True
        else:
            return False


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
