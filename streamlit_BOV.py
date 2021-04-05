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
import DodgeData as dd

cols_needed = ['Title','Address','City','State','PostalCode','Units','Target Open Date','Phase','Latitude','Longitude','distance','sort']
cols_exist = ['StarID','Property','Address','City','State','postalcode','Rooms','OpenDate','Latitude','Longitude','distance']
dodge_pipeline = pd.read_csv('pipeline.csv')
dodge_census = pd.read_csv('census.csv')

st.title('Explore Your Hotels!!!')



st.write('''
         
         All the hotel data you can handle bro!''')

name_str = pd.DataFrame(dodge_census[['Property','StarID']])

                
# markets = 1
# brands= dodge_pipeline.Chain.dropna().unique()

# stars = dodge_census.StarID.dropna().unique()

hotel = st.sidebar.selectbox('Select Hotel',name_str['Property'])
st.sidebar.write(hotel, ' has the StarID of ',name_str[name_str.Property == hotel]['StarID'].item())
# market = st.sidebar.selectbox('Select Market',dodge_pipeline[dodge_pipeline.State == state]['Submarket'].dropna().unique())

# brand = st.sidebar.selectbox('Select brand',brands)


# st.write(state)
# st.write(brand)

data = dodge_pipeline[['Title','Address','City','State','PostalCode','Units','Target Open Date','Phase','Latitude','Longitude']]

star = st.sidebar.text_input('Enter Star ID')
st_filter = st.sidebar.selectbox('Filter by?', ['radius','tract','city'])
radius = st.sidebar.text_input('Radius?')

submit = st.sidebar.button('run new supply')
if submit:
    data = dd.newsupply(float(star),float(radius),st_filter)
    

# st.write('run a radius sample',dd.newsupply(star))


st.write(data.dropna())

# button_clicked = st.sidebar.button("OK")


data.rename(columns = {'Latitude':'lat','Longitude':'lon'},inplace=True)
data.dropna(inplace=True)

st.map(data)
