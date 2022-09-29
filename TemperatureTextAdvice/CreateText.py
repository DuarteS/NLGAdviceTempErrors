import openai

def create_Text(array_of_results):
    responses = []
    for value in array_of_results:

        text = get_Text(value)
        responses.append([value[0], value[1], value[2], text[0], text[1], text[2]])
    return responses

def get_Text(result):
    promptWindows = 'Temp ' + str(result[0]) + ', Item:  Windows, Value:' + str(result[1]) + '\n\n---\n\n'
    promptShadows = 'Temp ' + str(result[0]) + ', Item:  Shadows, Value:' + str(result[2]) + '\n\n---\n\n'
    promptPipes = 'Temp ' + str(result[0]) + ', Item:  Pipes, Value:' + str(result[3]) + '\n\n---\n\n'

    responseW = GenText(promptWindows, "davinci:ft-personal:gpt-3-davinci-gpttempwindows-small-2022-09-20-06-37-58")#'windows'#
    responseS = GenText(promptShadows, "davinci:ft-personal:gpt-3-davinci-gpttempshadows-small-2022-09-20-06-43-46")#'shadows'#
    responseP = GenText(promptPipes, "davinci:ft-personal:gpt-3-davinci-gpttemppipes-small-2022-09-20-06-59-50") #'pipes'#

    responses = [responseW, responseP, responseS]

    return responses


def GenText(prompt, model):
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
