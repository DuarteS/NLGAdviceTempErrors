import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def testingPlot(time, values, text):
    year = time
    print(year)
    unemployment_rate = values
    print(unemployment_rate)
    print(text)

    def create_plot(year, unemployment_rate):
        plt.clf()
        plt.plot(year, unemployment_rate, color='red', marker='o')
        plt.annotate(text[3], xy =(year[1], unemployment_rate[1]),
                xytext =(year[2], unemployment_rate[1]),
                arrowprops = dict(facecolor ='green',
                                  shrink = 0.05),)
        plt.title('Unemployment Rate Vs Year', fontsize=14)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Unemployment Rate', fontsize=14)
        plt.grid(True)
        return plt.gcf()

    layout = [[sg.Text('Line Plot')],
              [sg.Canvas(size=(1000, 1000), key='-CANVAS-')],
              [sg.Exit()]]

    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', layout, finalize=True,
                       element_justification='center')

    draw_figure(window['-CANVAS-'].TKCanvas, create_plot(year, unemployment_rate))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

def plotOnline(df, text):
    # plt.clf()
    # plt.plot(time, values, color='red', marker='o')
    # for x in text:
    #     plt.annotate(x[3], xy=(x[0], x[2]),
    #                  xytext=(x[0], x[2]),
    #                  arrowprops=dict(facecolor='green',
    #                                  shrink=0.05), )
    # plt.title('Unemployment Rate Vs Year', fontsize=14)
    # plt.xlabel('Year', fontsize=14)
    # plt.ylabel('Unemployment Rate', fontsize=14)
    # plt.show()

    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = px.line(df, x='local_time', y=['onderbuis', 'wind_zijde_raamstand', 'energiedoek'])
    fig2 = px.line(df, x='local_time', y=['kastemperatuur'])
    fx = np.array([])
    fy = np.array([])
    ftw = np.array([])
    ftp = np.array([])
    fts = np.array([])
    for i in text:
        fx = np.append(fx, i[1])
        fy = np.append(fy, i[2])
        ftw = np.append(ftw, i[3])
        ftp = np.append(ftp, i[4])
        fts = np.append(fts, i[5])
    fig2.add_trace(go.Scatter(
        x=fx,
        y=fy,
        mode="markers+text",
        name="Windows",
        text=ftw,
        textposition="bottom center"
    ))
    fy = fy+1
    fig2.add_trace(go.Scatter(
        x=fx,
        y=fy,
        mode="markers+text",
        name="Pipes",
        text=ftp,
        textposition="bottom center"
    ))
    fy = fy+1
    fig2.add_trace(go.Scatter(
        x=fx,
        y=fy,
        mode="markers+text",
        name="Screens",
        text=fts,
        textposition="bottom center"
    ))
    fig2.update_traces(yaxis="y2")

    # create list of outlier_dates
    # outlier_dates = iforest_results[iforest_results['Anomaly'] == 1].index
    # # obtain y value of anomalies to plot
    # y_values = [iforest_results.loc[i]['value'] for i in outlier_dates]


    subfig.add_traces(fig.data + fig2.data)
    subfig.layout.xaxis.title = "Time"
    subfig.layout.yaxis.title = "Reasons values"
    subfig.layout.yaxis2.type = "log"
    subfig.layout.yaxis2.title = "Temperature"

    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()

def plotOnlineErrors(df, Windows, Pipes, Shadows):
    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = px.line(df, x='local_time', y=['onderbuis', 'wind_zijde_raamstand', 'energiedoek'])
    fig2 = px.line(df, x='local_time', y=['kastemperatuur'])

    fxw = []
    fyw = []
    ftw = []

    for x in range(len(Windows)):
        if Windows[x][3] <= 5:
            fxw.append(Windows[x][0])
            fyw.append(Windows[x][1])
            ftw.append(Windows[x][4])

    fig2.add_trace(go.Scatter(
        x=fxw,
        y=fyw,
        mode="markers+text",
        name="Windows",
        text=ftw,
        textposition="bottom center"
    ))

    fxw = []
    fyw = []
    ftw = []

    for x in range(len(Pipes)):
        if Pipes[x][3] <= 5:
            fxw.append(Pipes[x][0])
            fyw.append(Pipes[x][1]+2)
            ftw.append(Pipes[x][4])

    fig2.add_trace(go.Scatter(
        x=fxw,
        y=fyw,
        mode="markers+text",
        name="Pipes",
        text=ftw,
        textposition="bottom center"
    ))

    fxw = []
    fyw = []
    ftw = []

    for x in range(len(Shadows)):
        if Shadows[x][3] <= 5:
            fxw.append(Shadows[x][0])
            fyw.append(Shadows[x][1]+1)
            ftw.append(Shadows[x][4])

    fig2.add_trace(go.Scatter(
        x=fxw,
        y=fyw,
        mode="markers+text",
        name="Shadows",
        text=ftw,
        textposition="bottom center"
    ))

    fig2.update_traces(yaxis="y2")

    # create list of outlier_dates
    # outlier_dates = iforest_results[iforest_results['Anomaly'] == 1].index
    # # obtain y value of anomalies to plot
    # y_values = [iforest_results.loc[i]['value'] for i in outlier_dates]


    subfig.add_traces(fig.data + fig2.data)
    subfig.layout.xaxis.title = "Time"
    subfig.layout.yaxis.title = "Reasons values"
    subfig.layout.yaxis2.type = "log"
    subfig.layout.yaxis2.title = "Temperature"

    subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    subfig.show()
