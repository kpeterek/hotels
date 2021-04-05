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




def update_dodge():
    os.chdir(r"C:\Users\KyleP\Box\YB Hotels\CBRE Hotels Pipeline Data\Dodge Data")
    dodge_census = pd.read_excel(r"Hotel Census and Pipeline US and Canada.xlsx", sheet_name = 'Census')
    dodge_pipeline = pd.read_excel(r"Hotel Census and Pipeline US and Canada.xlsx", sheet_name = 'Pipeline')
    dodge_pipeline = dodge_pipeline.to_pickle('pipeline.pkl')
    dodge_census = dodge_census.to_pickle('census.pkl')



def get_dodge_data_new_supply():
    dodge_pipeline = pd.read_pickle(r'C:\Users\KyleP\Box\YB Hotels\CBRE Hotels Pipeline Data\Dodge Data\pipeline.pkl')
    cols_needed = ['Title','Address','City','State','PostalCode','Market','Submarket','Units','Target Open Date','Phase','Latitude','Longitude']
    return dodge_pipeline[cols_needed]
    
    
def get_dodge_data_census():
    dodge_census = pd.read_pickle(r'C:\Users\KyleP\Box\YB Hotels\CBRE Hotels Pipeline Data\Dodge Data\census.pkl')
    cols_exist = ['StarID','Property','Address','City','State','postalcode','Market','Submarket','Rooms','OpenDate','Latitude','Longitude']
    return dodge_census[cols_exist]

    # =============================================================================
# Testing Radius function
# =============================================================================

def newsupply(STR,radius=7,filter_by = 'radius'):
    # STR = int(input('Enter the Subject Property STR Number?: '))
    # radius = 40.0
    dodge_pipeline = pd.read_csv('pipeline.csv')
    dodge_census = pd.read_csv('census.csv')
    phases = ['Underway','Planning','Final Planning']
    if (dodge_census[dodge_census['StarID'] == STR]).any(axis=None) == True:
        prop_name = dodge_census['Property'][dodge_census['StarID'] == STR].iloc[:,].item()
        prop_city = dodge_census['City'][dodge_census['StarID'] == STR].iloc[:,].item()
        coords_subj = str(dodge_census['Latitude'][dodge_census['StarID'] == STR].iloc[:,].item()),str(dodge_census['Longitude'][dodge_census['StarID'] == STR].iloc[:,].item())
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
    return output_ns
        




def str_comps():
    cols_exist = ['StarID','Property','Address','City,St','postalcode','Rooms','OpenDate','Latitude','Longitude']
    props = input('lookup: ')
    dodge_census = pd.read_pickle(r"C:\Users\KyleP\Box\YB Hotels\CBRE Hotels Pipeline Data\Dodge Data\census.pkl")
    lst_prop = props.split()
    df = pd.DataFrame()
    df = dodge_census[dodge_census['StarID'].isin(lst_prop)]    
    df['City,St'] = df[['City','State']].apply(lambda x: ', '.join(x), axis = 1)
    df[cols_exist].to_clipboard(sep=",",header = True,index =False)   

def str_city():
    prop = input('lookup: ')
    # prop_city = dodge_census['City'][dodge_census['StarID'] == prop].iloc[:,].item()
    dodge_census = pd.read_pickle(r"C:\Users\KyleP\Box\YB Hotels\CBRE Hotels Pipeline Data\Dodge Data\census.pkl")
    df = pd.DataFrame()
    df = dodge_census[dodge_census['City'] == dodge_census['City'][dodge_census['StarID'] == prop].iloc[:,].item()]  
    df[cols_exist].to_clipboard(sep=",",header = True,index =False)      
    
    

def str_search():
    search = str(input('what would you like to search: '))
    ret_df = dodge_census[['StarID','Property','Address','City','State','Rooms','OpenDate']]
    ret_df['Property']
    ret_df = ret_df[(ret_df['Property'].str.contains(search,case=False)) | (ret_df['Address'].str.contains(search,case=False))]
    ret_df.to_clipboard(sep = ',', header = None)
    print(ret_df)
    
    
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
    output_df.to_clipboard()
    if output_df.empty:
        print('There are no incoming properties. Thank you')
    else:
        # print('Mean: \n',new_supply[['Units','Phase']].groupby('Phase').mean(),'\n',"TOTAL                 ",int(new_supply['Units'].dropna().sum()),'\n\n')
        # print('Total: \n',new_supply[['Title','Phase']].groupby('Phase').count(),'\n',"AVERAGE               ",int(new_supply['Units'].isnull().count()),'\n\n')
        print(output_df.iloc[:,:-1],'\n\n')
        time.sleep(1)
        output_df.groupby(['Phase'],sort=False)['Units'].sum().astype('int').to_clipboard(sep=',',header = None,index= True)
        print('      ',output_text,'\n')
        print('                Total Incoming Properties: ',distance_df['Units'].count(
            ),'\n                Total Incoming Rooms: ',int(distance_df['Units'].sum()),'\n\n')
        # root.bell()
        time.sleep(1)
        
  
