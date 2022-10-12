from datetime import timedelta

import pandas as pd

max_temp_hour = 2
TEMP_FILE = "../TempShock/TotalData.csv"


def _get_temp_data(temp_csv):
    df_temperature = pd.read_csv(temp_csv, sep=';').drop(
        ['buitentemperatuur', 'energiedoek', 'absoluut vochtgehalte kaslucht boven doek',
         'absoluut vochtgehalte meetbox onder', 'kastemperatuur meetbox onder', 'kastemperatuur boven doek'],
        axis=1).dropna()

    # df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'], format='%d/%m/%Y %I:%M %p')
    df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'], format='%d/%m/%Y %H:%M')
    df_temperature['local_time'] = pd.to_datetime(df_temperature['local_time'].astype(str), format='%Y/%m/%d %H:%M:%S')

    df_temperature['kastemperatuur'] = df_temperature['kastemperatuur'].astype(float)
    return df_temperature


def _find_shock(df_temp):
    dif_p_5m = (max_temp_hour / 60) * 5
    df_temp_shock = pd.DataFrame(columns=['start_time', 'end_time', 'max_temp', 'min_temp'])

    for curr_row in df_temp.iterrows():
        test_row = curr_row
        break

    for curr_row in df_temp.iterrows():
        test_temp = test_row[1].kastemperatuur
        curr_temp = curr_row[1].kastemperatuur
        temp_increase = 0

        if curr_temp >= test_temp:
            temp_increase = curr_row[1].kastemperatuur - test_row[1].kastemperatuur
        elif test_temp > curr_temp:
            temp_increase = test_row[1].kastemperatuur - curr_row[1].kastemperatuur

        if temp_increase >= dif_p_5m:
            # print(temp_increase, curr_row[1].local_time)
            #
            start_time = curr_row[1].local_time - timedelta(hours=1, minutes=00)  # 1hour
            end_time = curr_row[1].local_time

            time_group = df_temp[(df_temp['local_time'] >= start_time) & (df_temp['local_time'] <= end_time)]

            max_temp = time_group['kastemperatuur'].max()
            min_temp = time_group['kastemperatuur'].min()

            added = False

            if max_temp - min_temp >= max_temp_hour:

                for temp_row in df_temp_shock.iterrows():
                    test_start_time = temp_row[1].start_time
                    test_end_time = temp_row[1].end_time
                    test_max = temp_row[1].max_temp
                    test_min = temp_row[1].min_temp

                    if test_start_time < start_time < test_end_time:
                        print(df_temp_shock.loc[temp_row[0], 'end_time'])
                        print(temp_row[0])
                        df_temp_shock.loc[temp_row[0], 'end_time'] = end_time
                        if max_temp > test_max:
                            df_temp_shock.loc[temp_row[0], 'max_temp'] = max_temp
                        if min_temp < test_min:
                            df_temp_shock.loc[temp_row[0], 'min_temp'] = min_temp

                        added = True
                        break

                if not added:
                    df_temp_shock.loc[df_temp_shock.shape[0]] = [start_time, end_time, max_temp, min_temp]

        test_row = curr_row

    print(df_temp_shock.head(20))


_find_shock(_get_temp_data(TEMP_FILE))
