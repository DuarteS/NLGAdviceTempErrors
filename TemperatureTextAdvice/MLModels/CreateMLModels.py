# make predictions
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import pickle

Models = ['Window', 'Pipe', 'Shadow']
for type in Models:
    # Load dataset
    names = ['temp', 'value', 'result']
    dataset = read_csv(type + 'DataML.csv', names=names)
    # Split-out validation dataset
    array = dataset.values
    X = array[:, 0:2]
    y = array[:, 2]
    X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.05, random_state=1)
    # Make predictions on validation dataset
    model = DecisionTreeClassifier()
    model.fit(X_train, Y_train)
    print(X_validation)

    pickle.dump(model, open(type + '_model.sav', 'wb'))

    loaded_model = pickle.load(open(type + '_model.sav', 'rb'))
    predictions = loaded_model.predict(X_validation)
    print(predictions)
    # Evaluate predictions
    print(accuracy_score(Y_validation, predictions))
    print(confusion_matrix(Y_validation, predictions))
    print(classification_report(Y_validation, predictions))
