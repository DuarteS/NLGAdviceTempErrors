from CreateText import create_Text
from Reasons import getValues, getCSVa
from Results import gen_results
from plottesting import plotOnlineErrors

values = getValues()
results = gen_results(values)
text = create_Text(results)

print(values)
print(results)
print(text)

windows = []
pipes = []
shadows = []

for x in range(len(values)):
    windows.append([values[x][0],values[x][2],values[x][3],results[x][3],text[x][3]])
    pipes.append([values[x][0], values[x][2], values[x][4], results[x][4], text[x][4]])
    shadows.append([values[x][0], values[x][2], values[x][5], results[x][5], text[x][5]])

print(windows)
print(pipes)
print(shadows)

df_temp = getCSVa()
plotOnlineErrors(df_temp,windows,pipes,shadows)
