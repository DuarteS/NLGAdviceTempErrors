import PySimpleGUI as sg

from CreateText import create_Text
from Reasons import getValues, getSplitDF, getCSV
from Results import gen_results
from plottesting import testingPlot, plotOnline

# for result in create_Text(gen_results(getValues())):
#     print(result[0], ' - ', result[1], result[2], '  #  ', result[3], '  #  ', result[4])


# Layout for GUI :pysimplegui
layout = [[sg.Button('Gen - Avg'), sg.Button('Gen - Results'), sg.Button('Gen - Text'), sg.Button('Gen - Graph'), sg.Cancel()],
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
                value[1]) + " Windows: " + value[3] + " Pipes: " + value[4] + " Screens: " + value[5] + "\n\n"

        window.Element("text").update(display)
    if event == 'Gen - Graph':
        df_temp = getCSV()
        text = create_Text(gen_results(getValues()))
        #plotOnline(df_temp['local_time'].to_numpy(), df_temp['kastemperatuur'].to_numpy(), text)
        plotOnline(df_temp, text)
    #
    #     text = create_Text(gen_results(getValues()))
    #
    #     df_temp = getCSVa()
    #     testingPlot(df_temp['local_time'].to_numpy(), df_temp['kastemperatuur'].to_numpy(),"12233")
    #     # for x in df_errors:
    #     #     print(df_errors[x])
    #     #     df_temp = df_errors[x]
    #     #     testingPlot(df_temp['local_time'].to_numpy(), df_temp['kastemperatuur'].to_numpy(),text[x])


window.close()
