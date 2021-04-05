# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 13:23:16 2020

@author: KyleP
"""

import time
import pandas as pd
import os
import numpy as np
import geopandas as gpd
from geopy.distance import geodesic
import matplotlib.pyplot as plt


    
pd.set_option('display.max_columns', 15,'max_colwidth',70,'display.width', 500, 'display.max_rows',100)
pd.set_option('mode.sim_interactive', True)
pd.set_option('expand_frame_repr', True)
# os.getcwd()

# os.listdir()
cols_needed = ['Title','Address','City','State','PostalCode','Units','Target Open Date','Phase','Latitude','Longitude','distance','sort']
cols_exist = ['StarID','Property','Address','City','State','postalcode','Rooms','OpenDate','Latitude','Longitude','distance']




def newsupply(STR,radius=7,filter_by = 'radius'):
    # STR = int(input('Enter the Subject Property STR Number?: '))
    # radius = 40.0
    dodge_pipeline = pd.read_csv('pipeline.csv')
    dodge_census = pd.read_pickle('census.csv')
    phases = ['Underway','Planning','Final Planning']
    if (dodge_census[dodge_census['StarID'] == STR]).any(axis=None) == True:
        prop_name = dodge_census['Property'][dodge_census['StarID'] == STR].iloc[:,].item()
        prop_city = dodge_census['City'][dodge_census['StarID'] == STR].iloc[:,].item()
        coords_subj = str(dodge_census.iloc[:,38][dodge_census['StarID'] == STR].iloc[:,].item()),str(dodge_census.iloc[:,39][dodge_census['StarID'] == STR].iloc[:,].item())
        phase_sort = {phases[0]:0,phases[1]:2,phases[2]:1}
        SubTract = dodge_census['Submarket'].loc[dodge_census['StarID'] == STR].iloc[:,].item()
        SubMkt = dodge_census['Market'].loc[dodge_census['StarID'] == STR].iloc[:,].item()
        new_supply = dodge_pipeline.loc[(dodge_pipeline['Phase'].isin(list(phases)))].dropna(subset=['Latitude','Longitude'])
        new_supply['Lat,Lon'] = list(zip(new_supply['Latitude'],new_supply['Longitude']))
        new_supply['Lat,Lon'].to_clipboard()
        new_supply['distance'] = [geodesic(coords_subj,new_supply['Lat,Lon'].loc[new_supply.index == x]).miles for x in new_supply.index]
        new_supply.to_clipboard()
        filter_input = filter_by
        if filter_input == 'radius':
            new_supply.query('distance <= @radius',inplace= True)
            output_text = str(f'Within a {radius} mile radius of {prop_name}:')
        elif filter_input == 'city':
            new_supply = new_supply.query('City == @prop_city & Submarket == @SubTract')
            output_text = str(f"Based on {prop_city}'s (city) pipeline of {prop_name}: ")
        elif filter_input == 'market':
            new_supply = new_supply.query('Market == @SubMkt')
            output_text = str(f'Based on the {SubMkt} (market) pipeline of {prop_name}:')
        elif filter_input == 'tract':    
            new_supply = new_supply.query('Submarket == @SubTract')
            output_text = str(f'Based on the {SubTract} pipeline of {prop_name}:')
        new_supply['sort'] = new_supply['Phase'].map(phase_sort)
        new_supply.columns
        output_ns = new_supply[cols_needed]
        output_ns.sort_values('sort',ascending = True,inplace=True)
        if output_ns.empty:
            print('There are no incoming properties. Thank you')
        else:
            print('Mean: \n',new_supply[['Units','Phase']].groupby('Phase').mean(),'\n',"TOTAL                 ",int(new_supply['Units'].dropna().sum()),'\n\n')
            print('Total: \n',new_supply[['Title','Phase']].groupby('Phase').count(),'\n',"AVERAGE               ",int(new_supply['Units'].isnull().count()),'\n\n')
            print(output_ns.iloc[:,:-1],'\n\n')
            time.sleep(1)
            # output_ns.groupby(['Phase'],sort=False)['Units'].sum().astype('int').to_clipboard(sep=',',header = None,index= True)
            # print('      ',output_text,'\n')
            print('                Total Incoming Properties: ',new_supply['Units'].count(
                ),'\n                Total Incoming Rooms: ',int(new_supply['Units'].sum()),'\n\n')
            # root.bell()
            time.sleep(1)
        output_ns.to_clipboard(sep=",",header = False,index =False)
        print(f'{prop_name} new supply is now in your clipboard, {output_text}')
        # return output_ns
    else:
        print('Property not found')
        pass
    return output_ns
        


