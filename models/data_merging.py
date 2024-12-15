# -*- coding: utf-8 -*-
"""Data_merging.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16qZJ39H2k_TsWAjaYA9taoco5sNWBwfZ
"""

url_races = 'https://raw.githubusercontent.com/HeedfulMoss/ML-F1-Prediction-Project/0828f7ef1779252138bb78445c191978893a005c/processing/formatted_races_data.csv'
url_results = 'https://raw.githubusercontent.com/HeedfulMoss/ML-F1-Prediction-Project/0828f7ef1779252138bb78445c191978893a005c/processing/formatted_results_data.csv'
url_qualifying = 'https://raw.githubusercontent.com/HeedfulMoss/ML-F1-Prediction-Project/0828f7ef1779252138bb78445c191978893a005c/processing/formatted_qualifying.csv'
url_driver_standings = 'https://raw.githubusercontent.com/HeedfulMoss/ML-F1-Prediction-Project/0828f7ef1779252138bb78445c191978893a005c/processing/formatted_driver_standings.csv'
url_constructor_standings = 'https://raw.githubusercontent.com/HeedfulMoss/ML-F1-Prediction-Project/0828f7ef1779252138bb78445c191978893a005c/processing/formatted_constructor_standings.csv'
url_weather = 'https://raw.githubusercontent.com/HeedfulMoss/ML-F1-Prediction-Project/5a3e97ca0775cf78343855ac44b5150896726774/processing/formatted_weather_df.csv'

import pandas as pd
import numpy as np

formatted_races_data_df = pd.read_csv(url_races)
formatted_results_data_df = pd.read_csv(url_results)
formatted_driver_standings_df= pd.read_csv(url_driver_standings)
formatted_constructor_standings_df = pd.read_csv(url_constructor_standings)
formatted_qualifying_df = pd.read_csv(url_qualifying)
formatted_weather_df = pd.read_csv(url_weather)

formatted_results_data_df

formatted_weather_df = formatted_weather_df.drop(['lat', 'lng','country'],
                                                          axis = 1)

formatted_races_data_df = formatted_races_data_df.drop(['lat', 'lng','country','url'],
                                                          axis = 1)

df1 = pd.merge(formatted_races_data_df, formatted_weather_df, how='inner',
               on=['year', 'round', 'circuitId'])

df1 = df1.drop(['date_y'],axis = 1).rename(columns={'date_x': 'date'})

print(df1.columns)

df2 = pd.merge(df1, formatted_results_data_df, how='inner', on=['year', 'round', 'circuitId'])

df2 = df2.drop(['url','status','time','points'],axis = 1)

df2.columns

df3 = pd.merge(df2, formatted_driver_standings_df, how='left',
               on=['year', 'round', 'driverRef'])

df3 = df3.drop(['position_y'],axis = 1).rename(columns={'position_x': 'position'})

df3.columns

df4 = pd.merge(df3, formatted_constructor_standings_df, how='left',
               on=['year', 'round', 'constructor']) #from 1958

df4.columns

final_df = pd.merge(df4, formatted_qualifying_df, how='inner',
                    on=['year', 'round', 'grid'])

final_df.columns

final_df = final_df.drop(['constructor_y'],axis = 1).rename(columns={'constructor_x': 'constructor'})

final_df = final_df.drop(['driverRef_y'],axis = 1).rename(columns={'driverRef_x': 'driverRef'})

# calculate age of drivers

from dateutil.relativedelta import *
final_df['date'] = pd.to_datetime(final_df.date)
final_df['date_of_birth'] = pd.to_datetime(final_df.date_of_birth)
final_df['driver_age'] = final_df.apply(lambda x:
                                        relativedelta(x['date'], x['date_of_birth']).years, axis=1)
final_df.drop(['date', 'date_of_birth'], axis = 1, inplace = True)

# fill/drop nulls

for col in ['driver_points', 'driver_wins', 'driver_standings_pos', 'constructor_points',
            'constructor_wins' , 'constructor_standings_pos']:
    final_df[col].fillna(0, inplace = True)
    final_df[col] = final_df[col].map(lambda x: int(x))

final_df.dropna(inplace = True )

# convert to boolean to save space

for col in ['weather_warm', 'weather_cold','weather_dry', 'weather_wet', 'weather_cloudy']:
    final_df[col] = final_df[col].map(lambda x: bool(x))

# calculate difference in qualifying times
final_df['qualifying_time'] = final_df.qualifying_time.map(lambda x: 0 if str(x) == '00.000'
                             else(float(str(x).split(':')[1]) +
                                  (60 * float(str(x).split(':')[0])) if x != 0 else 0))
final_df = final_df[final_df['qualifying_time'] != 0]
final_df.sort_values(['year', 'round', 'grid'], inplace = True)
final_df['qualifying_time_diff'] = final_df.groupby(['year', 'round']).qualifying_time.diff()
final_df['qualifying_time'] = final_df.groupby(['year',
                                                'round']).qualifying_time_diff.cumsum().fillna(0)
final_df.drop('qualifying_time_diff', axis = 1, inplace = True)


# get dummies

df_dum = pd.get_dummies(final_df, columns = ['circuit_id', 'nationality', 'constructor'] )

for col in df_dum.columns:
    if 'nationality' in col and df_dum[col].sum() < 140:
        df_dum.drop(col, axis = 1, inplace = True)

    elif 'constructor' in col and df_dum[col].sum() < 140:
        df_dum.drop(col, axis = 1, inplace = True)

    elif 'circuit_id' in col and df_dum[col].sum() < 70:
        df_dum.drop(col, axis = 1, inplace = True)

    else:
        pass