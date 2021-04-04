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

import DodgeData as dd


st.title('Explore Your Hotels!!!')



st.write('''
         
         All the hotel data you can handle bro!''')
         


dodge_pipeline = pd.read_pickle('pipeline.pkl')
dodge_census = pd.read_pickle('census_light.pkl')

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




star = st.sidebar.text_input('Enter Star ID')
filter_by = st.sidebar.selectbox('Filter by?', ['radius','tract','city'])
radius = st.sidebar.text_input('Radius?')

submit = st.sidebar.button('run new supply')
if submit:
    data = dd.newsupply(int(star),radius=int(radius),filter_by=filter_by)
    
    
# st.write('run a radius sample',dd.newsupply(star))


st.write(data.dropna())

# button_clicked = st.sidebar.button("OK")

data.rename(columns = {'Latitude':'lat','Longitude':'lon'},inplace=True)
data.dropna(inplace=True)

st.map(data)
             
