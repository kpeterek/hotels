# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 12:22:56 2021

@author: KyleP
"""

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
from typing import Dict
import base64
from pandas.tseries.offsets import MonthEnd
import zipfile
import xlrd
import matplotlib.pyplot as plt


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
if radius.isnumeric():
    pass
else:
    radius = 0.0

submit = st.sidebar.button('run new supply')
if submit:
    data = dd.newsupply(float(star),float(radius),st_filter)
    

# st.write('run a radius sample',dd.newsupply(star))


st.write(data.dropna())

# button_clicked = st.sidebar.button("OK")


data.rename(columns = {'Latitude':'lat','Longitude':'lon'},inplace=True)
data.dropna(inplace=True)

st.map(data)

st.header("File Download")

csv = data.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
st.markdown(href, unsafe_allow_html=True)

def star_data_input(files):
	cols = [0,1,2,3,5,6,7,8,12,13,14,15,17,18,19,20,24,25,26,27,29,30,31,32,34]
	star_df = pd.DataFrame()
	comp_set = pd.DataFrame()
	for path in files:
		try:
			if 'Monthly STAR Report' in pd.read_excel(xlfile,sheet_name='Table of Contents',skiprows=2,usecols='B',header=0,nrows=0).columns[0]:
				date = pd.to_datetime(pd.read_excel(xlfile,sheet_name='Glance',skiprows=4).iloc[0,1],infer_datetime_format=True)+MonthEnd(1)
				comps = pd.read_excel(xlfile,sheet_name='Response',skiprows=21,usecols='C:L',header=0).dropna(axis=0,how = 'all').dropna(axis=1,how='all').dropna(subset=['Name'])
				star = pd.read_excel(xlfile,sheet_name='Comp',skiprows=18,usecols='B:T',nrows=34,header=1,index_col=0,parse_dates=True).T
				star.index = pd.date_range(end=date,periods = 18,freq='M')
				sub_prop = comps.iloc[0,0]
				star['STARID'] = sub_prop
				star_df = star_df.append(star).drop_duplicates().sort_index(ascending=True)
				comps['Subj_prop'] = sub_prop
				comp_set = comp_set.append(comps).drop_duplicates().sort_index(ascending=True)
		except ValueError:
			pass
	print(star_df.info())
	star_df = star_df.iloc[:,cols]
	# star_df['StarID'] = sub_prop
	# star_df.columns = ['RevPAR_my_prop','RevPAR_comp','ADR_my_prop','ADR_comp','OCC_my_prop','OCC_comp','StarID']
	star_df.iloc[:,4:6] = star_df.iloc[:,4:6]/100
	star_df=star_df[~star_df.index.duplicated(keep='last')]
	comp_set = comp_set[~comp_set['STR#'].duplicated(keep='last')]
	#star_df.to_clipboard(header=False)
	star_df.columns = ['OCC_my_prop','OCC_comp','OCC_Index','OCC_Rank', 'OCC_per_chg_my_prop','OCC_per_chg_comp','OCC_per_chg_index','OCC_per_chg_rank','ADR_my_prop','ADR_comp','ADR_Index','ADR_Rank','ADR_per_chg_my_prop','ADR_per_chg_comp','ADR_per_chg_index','ADR_per_chg_rank','RevPAR_my_prop','RevPAR_comp','RevPAR_Index','RevPAR_Rank','RevPAR_per_chg_my_prop','RevPAR_per_chg_comp','RevPAR_per_chg_index','RevPAR_per_chg_rank','STARID']
	# star_df.drop_duplicates(subset=['OCC_my_prop','ADR_my_prop','RevPAR_my_prop'],inplace=True)
	print(comp_set)
	return star_df,comp_set

                  
def star_data_input_zip(files):
	cols = [0,1,2,3,5,6,7,8,12,13,14,15,17,18,19,20,24,25,26,27,29,30,31,32,34]
	star_df = pd.DataFrame()
	comp_set = pd.DataFrame()
	archive = zipfile.ZipFile(files, 'r')
	with zipfile.ZipFile(files, "r") as f:
		for file in f.namelist():
			xlfile = archive.open(file)
			if file.endswith('.xlsx'):
				print(file)
				try:
					if 'Monthly STAR Report' in pd.read_excel(xlfile,sheet_name='Table of Contents',skiprows=2,usecols='B',header=0,nrows=0).columns[0]:
						date = pd.to_datetime(pd.read_excel(xlfile,sheet_name='Glance',skiprows=4).iloc[0,1],infer_datetime_format=True)+MonthEnd(1)
						comps = pd.read_excel(xlfile,sheet_name='Response',skiprows=21,usecols='C:L',header=0).dropna(axis=0,how = 'all').dropna(axis=1,how='all').dropna(subset=['Name'])
						star = pd.read_excel(xlfile,sheet_name='Comp',skiprows=18,usecols='B:T',nrows=34,header=1,index_col=0,parse_dates=True).T
						star.index = pd.date_range(end=date,periods = 18,freq='M')
						sub_prop = comps.iloc[0,0]
						star['STARID'] = sub_prop
						star_df = star_df.append(star).drop_duplicates().sort_index(ascending=True)
						comps['Subj_prop'] = sub_prop
						comp_set = comp_set.append(comps).drop_duplicates().sort_index(ascending=True)
				except ValueError:
					pass
	print(star_df.info())
	star_df = star_df.iloc[:,cols]
	# star_df['StarID'] = sub_prop
	# star_df.columns = ['RevPAR_my_prop','RevPAR_comp','ADR_my_prop','ADR_comp','OCC_my_prop','OCC_comp','StarID']
	star_df.iloc[:,4:6] = star_df.iloc[:,4:6]/100
	star_df=star_df[~star_df.index.duplicated(keep='last')]
	comp_set = comp_set[~comp_set['STR#'].duplicated(keep='last')]
	#star_df.to_clipboard(header=False)
	star_df.columns = ['OCC_my_prop','OCC_comp','OCC_Index','OCC_Rank', 'OCC_per_chg_my_prop','OCC_per_chg_comp','OCC_per_chg_index','OCC_per_chg_rank','ADR_my_prop','ADR_comp','ADR_Index','ADR_Rank','ADR_per_chg_my_prop','ADR_per_chg_comp','ADR_per_chg_index','ADR_per_chg_rank','RevPAR_my_prop','RevPAR_comp','RevPAR_Index','RevPAR_Rank','RevPAR_per_chg_my_prop','RevPAR_per_chg_comp','RevPAR_per_chg_index','RevPAR_per_chg_rank','STARID']
	# star_df.drop_duplicates(subset=['OCC_my_prop','ADR_my_prop','RevPAR_my_prop'],inplace=True)
	print(comp_set)
	return star_df.reset_index(),comp_set


def excel_file_merge(zip_file_name):
	df = pd.DataFrame()
	archive = zipfile.ZipFile(zip_file_name, 'r')
	with zipfile.ZipFile(zip_file_name, "r") as f:
		for file in f.namelist():
			xlfile = archive.open(file)
			if file.endswith('.xlsx'):
				# Add a note indicating the file name that this dataframe originates from
				df_xl = pd.read_excel(xlfile, engine='openpyxl')
				df_xl['Note'] = file
				# Appends content of each Excel file iteratively
				df = df.append(df_xl, ignore_index=True)
	return df

# Upload CSV data
with st.sidebar.header('1. Upload your ZIP file'):
    uploaded_file = st.sidebar.file_uploader("Excel-containing ZIP file", type=["zip"])
    st.sidebar.markdown("""
[Example ZIP input file](https://github.com/dataprofessor/excel-file-merge-app/raw/main/nba_data.zip)
""")

# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="merged_file.csv">Download Merged File as CSV</a>'
    return href

def xldownload(df):
    df.to_excel('data.xlsx', index=False)
    data = open('data.xlsx', 'rb').read()
    b64 = base64.b64encode(data).decode('UTF-8')
    #b64 = base64.b64encode(xl.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/xls;base64,{b64}" download="merged_file.xlsx">Download Merged File as XLSX</a>'
    return href

# Main panel
if st.sidebar.button('Submit'):
	#@st.cache
	star_df,comp_set = star_data_input_zip(uploaded_file)
	st.header('**STR Compiled Data**')
	st.write(comp_set)
	st.write(star_df)
	st.markdown(filedownload(star_df), unsafe_allow_html=True)
	st.markdown(xldownload(star_df), unsafe_allow_html=True)
	st.line_chart(star_df[['OCC_my_prop','ADR_my_prop','RevPAR_my_prop']])
else:
	st.info('Awaiting for ZIP file to be uploaded.')
	
multiple_files = st.file_uploader(
    "Multiple File Uploader",
    accept_multiple_files=True
)

if st.button('Submit'):
	#@st.cache
	star_df,comp_set = star_data_input(multiple_files)
	st.header('**STR Compiled Data**')
	st.write(comp_set)
	st.write(star_df)
	st.markdown(filedownload(star_df), unsafe_allow_html=True)
	st.markdown(xldownload(star_df), unsafe_allow_html=True)
	st.line_chart(star_df[['OCC_my_prop','ADR_my_prop','RevPAR_my_prop']])
else:
	st.info('Awaiting for STR Reports to be uploaded.')
