import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




def testingPlot(time,values):
    year = time
    print(year)
    unemployment_rate = values

    def create_plot(year, unemployment_rate):
        plt.plot(year, unemployment_rate, color='red', marker='o')
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