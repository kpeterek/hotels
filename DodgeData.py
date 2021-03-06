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
import re
import more_itertools
from itertools import permutations
import math
import streamlit as st


cols_needed = ['Title','Address','City','State','PostalCode','Units','Open Date','Phase','Latitude','Longitude','distance','sort']
cols_exist = ['StarID','Property','Address','City','State','postalcode','Rooms','Latitude','Longitude','distance']
str_census = pd.read_csv('str_census_small.csv')
str_pipeline = pd.read_csv('pipeline.csv')


def newsupply(STR,radius=7,filter_by = 'radius'):
    # STR = int(input('Enter the Subject Property STR Number?: '))
    # radius = 40.0
    dodge_pipeline = pd.read_csv('pipeline.csv')
    dodge_census = pd.read_csv('census.csv')
    phases = ['In Construction','Planning','Final Planning']
    try:
        if (dodge_census[dodge_census['StarID'] == STR]).any(axis=None) == True:
            prop_name = dodge_census['Property'][dodge_census['StarID'] == STR].iloc[:,].item()
            prop_city = dodge_census['City'][dodge_census['StarID'] == STR].iloc[:,].item()
            coords_subj = str(dodge_census['Latitude'][dodge_census['StarID'] == STR].iloc[:,].item()),str(dodge_census['Longitude'][dodge_census['StarID'] == STR].iloc[:,].item())
            phase_sort = {phases[0]:0,phases[1]:2,phases[2]:1}
            SubTract = dodge_census['Submarket'].loc[dodge_census['StarID'] == STR].iloc[:,].item()
            SubMkt = dodge_census['Market'].loc[dodge_census['StarID'] == STR].iloc[:,].item()
            new_supply = dodge_pipeline.loc[(dodge_pipeline['Phase'].isin(list(phases)))].dropna(subset=['Latitude','Longitude'])
            new_supply['Lat,Lon'] = list(zip(new_supply['Latitude'],new_supply['Longitude']))
            new_supply['distance'] = [geodesic(coords_subj,new_supply['Lat,Lon'].loc[new_supply.index == x]).miles for x in new_supply.index]
            filter_input = filter_by
            if filter_input == 'radius':
                new_supply.query('distance <= @radius',inplace= True)
                output_text = str(f'Within a {radius} mile radius of {prop_name}:')
            elif filter_input == 'city':
                new_supply = new_supply.query('City == @prop_city')
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
        return output_ns
    except:
        return pd.DataFrame()

 

    

def compset(STR,radius):
    STR = int(input('Enter the Subject Property STR Number?: '))
    radius = 10.0
    prop_name = dodge_census['Property'][dodge_census['StarID'] == STR].iloc[:,].item()
    prop_city = dodge_census['City'][dodge_census['StarID'] == STR].iloc[:,].item()
    coords_subj = str(dodge_census.iloc[:,38][dodge_census['StarID'] == STR].iloc[:,].item()),str(dodge_census.iloc[:,39][dodge_census['StarID'] == STR].iloc[:,].item())
    SubTract = dodge_census['Submarket'].loc[dodge_census['StarID'] == STR].iloc[:,].item()
    SubMkt = dodge_census['Market'].loc[dodge_census['StarID'] == STR].iloc[:,].item()
    distance_df = dodge_census.dropna(subset=['Latitude','Longitude'])
    distance_df['Lat,Lon'] = list(zip(distance_df['Latitude'],distance_df['Longitude']))
    distance_df['Lat,Lon'].to_clipboard()
    distance_df['distance'] = [geodesic(coords_subj,distance_df['Lat,Lon'].loc[distance_df.index == x]).miles for x in distance_df.index]
    distance_df.to_clipboard()
    filter_input = input("Filter by ('radius','city','market','tract'): ")
    if filter_input == 'radius':
        distance_df.query('distance <= @radius',inplace= True)
        output_text = str(f'Within a {radius} mile radius of {prop_name}:')
    elif filter_input == 'city':
        distance_df = distance_df.query('City == @prop_city & Submarket == @SubTract')
        output_text = str(f"Based on {prop_city}'s (city) pipeline of {prop_name}: ")
    elif filter_input == 'market':
        distance_df = distance_df.query('Market == @SubMkt')
        output_text = str(f'Based on the {SubMkt} (market) pipeline of {prop_name}:')
    elif filter_input == 'tract':    
        distance_df = distance_df.query('Submarket == @SubTract')
        output_text = str(f'Based on the {SubTract} pipeline of {prop_name}:')
    distance_df.columns
    output_df = distance_df[cols_exist]
    output_df.sort_values('distance',ascending = True,inplace=True)
    return output_df


def str_lookup(keys):
    keys = re.sub('[^0-9a-zA-Z]+', ' ',keys)
    keywords = list(keys.lower().split(' '))
    perms = list(set(map(' '.join, more_itertools.powerset(keywords))))
    candidates = []
    df_op = pd.read_csv('str_census_small.csv')
    #keywords = list(input('Enter Hotel Name Keywords:').lower().split(' '))
    for word in perms:
        if len(df_op[df_op['Hotel Name'].str.lower().str.contains(word)]) > 0:
            df_op = df_op[df_op['Hotel Name'].str.lower().str.contains(word)]
            cand_temp_list = df_op['Hotel Name'] + ' - ' + df_op['STR Number'].astype(str)
            candidates.extend(cand_temp_list)
    return pd.Series(candidates).value_counts().head(20)



def nearby_comps_str(STR,radius=7):
    R = 3958.756
    prop_name = str_census['Hotel Name'][str_census['STR Number'] == STR].iloc[:,].item()
    prop_city = str_census['City'][str_census['STR Number'] == STR].iloc[:,].item()
    coords_subj = str(str_census.iloc[:,27][str_census['STR Number'] == STR].iloc[:,].item()),str(str_census.iloc[:,28][str_census['STR Number'] == STR].iloc[:,].item())
    lat_min,lat_max = math.degrees(math.radians(float(coords_subj[0]))-radius/R),math.degrees(math.radians(float(coords_subj[0]))+radius/R)
    lon_min,lon_max = math.degrees(math.radians(float(coords_subj[1]))-math.asin(math.sin(radius/R)/math.cos(math.radians(float(coords_subj[0]))))),math.degrees(math.radians(float(coords_subj[1]))+math.asin(math.sin(radius/R)/math.cos(math.radians(float(coords_subj[0])))))
    distance_census = str_census.dropna(subset=['Latitude','Longitude'])[(str_census.Latitude.between(lat_min,lat_max))&(str_census.Longitude.between(lon_min,lon_max))]
    distance_census["Lat,Lon"] = list(zip(distance_census['Latitude'],distance_census['Longitude']))
    distance_census ['distance'] = [geodesic(coords_subj,distance_census['Lat,Lon'].loc[distance_census.index == x]).miles for x in distance_census.index]
    print(prop_name, prop_city, coords_subj)
    return distance_census

def str_find(star):
    str_census = pd.read_csv('str_census_small.csv')
    ret_df = str_census[str_census['STR Number'] == int(star)]
    return ret_df.T
