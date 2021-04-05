# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 15:08:30 2021

@author: KyleP
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck
import os
import geopandas as gpd
from geopy.distance import geodesic
import time

cols_needed = ['Title','Address','City','State','PostalCode','Units','Target Open Date','Phase','Latitude','Longitude','distance','sort']
cols_exist = ['StarID','Property','Address','City','State','postalcode','Rooms','OpenDate','Latitude','Longitude','distance']


def newsupply(STR,radius=7,filter_by = 'radius'):
    # STR = int(input('Enter the Subject Property STR Number?: '))
    # radius = 40.0
    dodge_pipeline = pd.read_csv('pipeline.csv')
    dodge_census = pd.read_csv('census.csv')
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

st.title('Explore Your Hotels!!!')



st.write('''
         
         All the hotel data you can handle bro!''')
         


dodge_pipeline = pd.read_csv('pipeline.csv')
dodge_census = pd.read_csv('census.csv')

states = dodge_pipeline.State.str.replace(" ","").dropna().unique()

# markets = 1
# brands= dodge_pipeline.Chain.dropna().unique()

# stars = dodge_census.StarID.dropna().unique()

# state = st.sidebar.selectbox('Select State',states)

# market = st.sidebar.selectbox('Select Market',dodge_pipeline[dodge_pipeline.State == state]['Submarket'].dropna().unique())

# brand = st.sidebar.selectbox('Select brand',brands)


# st.write(state)
# st.write(brand)

data = dodge_pipeline[['Title','Address','City','State','PostalCode','Units','Target Open Date','Phase','Latitude','Longitude']]




star = int(st.sidebar.text_input('Enter Star ID'))
filter_by = st.sidebar.selectbox('Filter by?', ['radius','tract','city'])
radius = int(st.sidebar.text_input('Radius?'))

submit = st.sidebar.button('run new supply')
if submit:
    data = newsupply(int(star),radius,filter_by)
    
    
# st.write('run a radius sample',dd.newsupply(star))


st.write(data.dropna())

# button_clicked = st.sidebar.button("OK")

data.rename(columns = {'Latitude':'lat','Longitude':'lon'},inplace=True)
data.dropna(inplace=True)

st.map(data)
             
