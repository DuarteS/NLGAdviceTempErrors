import PySimpleGUI as sg

from CreateText import create_Text
from Reasons import getValues
from Results import gen_results

# for result in create_Text(gen_results(getValues())):
#     print(result[0], ' - ', result[1], result[2], '  #  ', result[3], '  #  ', result[4])


# Layout for GUI :pysimplegui
layout = [[sg.Button('Gen - Avg'), sg.Button('Gen - Results'), sg.Button('Gen - Text'), sg.Cancel()],
          [sg.Multiline("", size=(55, 10), key='text')]]

# Start GUI
window = sg.Window('NLG RTR advice', layout)

# Event Loop
while True:
    event, values = window.Read()
    if event in (None, 'Exit'):
        break
    if event == 'Gen - Avg':
        values = getValues()
        display = ''
        for value in values:
            display = display + "Start time: " + str(value[0]) + ". End time: " + str(
                value[1]) + " Temp: " + "{:.2f}".format(value[2]) + " Windows: " + "{:.2f}".format(
                value[3]) + " Pipes: " + "{:.2f}".format(value[4]) + " Screens: " + "{:.2f}".format(value[5]) + "\n\n"
        window.Element("text").update(display)
    if event == 'Gen - Results':
        results = gen_results(getValues())
        display = ''
        for value in results:
            display = display + "Start time: " + str(value[0]) + ". End time: " + str(
                value[1]) + " Temp: " + "{:.2f}".format(value[2]) + " Windows: " + "{:.2f}".format(
                value[3]) + " Pipes: " + "{:.2f}".format(value[4]) + " Screens: " + "{:.2f}".format(value[5]) + "\n\n"

        window.Element("text").update(display)
    if event == 'Gen - Text':
        text = create_Text(gen_results(getValues()))
        display = ''
        for value in text:
            display = display + "Start time: " + str(value[0]) + ". End time: " + str(
                value[1]) + " Windows: " + value[2] + " Pipes: " + value[3] + " Screens: " + value[4] + "\n\n"

        window.Element("text").update(display)
    # window.Element("text").update('Windows: ' + responseW + '\nPipes: ' + responseP + '\nShadows: ' + responseS)

window.close()
