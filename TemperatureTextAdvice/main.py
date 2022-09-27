from CreateText import create_Text
from Reasons import getValues
from Results import gen_results

for result in create_Text(gen_results(getValues())):
    print(result[0], ' - ', result[1], result[2], '  #  ', result[3], '  #  ', result[4])
