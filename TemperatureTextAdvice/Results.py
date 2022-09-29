import pickle
import sklearn


# Array of errors should be sent [[start_time, end_time, temp, windows, pipes, shadows]]
def gen_results(array_of_errors):
    window_model = pickle.load(open('MLModels/Window_model.sav', 'rb'))
    pipe_model = pickle.load(open('MLModels/Pipe_model.sav', 'rb'))
    shadow_model = pickle.load(open('MLModels/Shadow_model.sav', 'rb'))

    results = []
    for value in array_of_errors:
        windowResult = window_model.predict([[int(value[2]), int(value[3])]])[0]
        pipeResult = pipe_model.predict([[int(value[2]), int(value[4])]])[0]
        shadowResult = shadow_model.predict([[int(value[2]), int(value[5])]])[0]

        result = [value[0], value[1], value[2], windowResult, pipeResult, shadowResult]
        print([value[0], value[1], value[2], windowResult, pipeResult, shadowResult])

        results.append(result)

    return results
