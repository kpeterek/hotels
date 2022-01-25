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
import pickle5 as pickle
import datetime as dt
from bs4 import BeautifulSoup
import requests
import plotly.graph_objects as go
import fin_plan as fp


pd.options.display.float_format = "{:,.2f}".format
cols_needed = ['Title','Address','City','State','PostalCode','Units','Open Date','Phase','Latitude','Longitude','distance','sort']
cols_exist = ['StarID','Property','Address','City','State','postalcode','Rooms','OpenDate','Latitude','Longitude','distance']
dodge_pipeline = pd.read_csv('pipeline.csv')
dodge_census = pd.read_csv('census.csv')
str_census = pd.read_csv('str_census_small.csv')
with open('Closings_pickle.pkl', 'rb') as f: 
	closings = pickle.load(f)
with open('Kalibri_zip_code_markets.pkl', 'rb') as f: 
	kalibri_zip = pickle.load(f)
with open('AllSubmarketData.pkl', 'rb') as f: 
	kalibri_data = pickle.load(f)
plot_cols = ['OCC_my_prop','ADR_my_prop','RevPAR_my_prop']
name_str = pd.DataFrame(dodge_census[['Property','StarID']])



def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

local_css("style.css")
remote_css('https://fonts.googleapis.com/css2')

def search(regex: str, df, case=False):
    """Search all the text columns of `df`, return rows with any matches."""
    textlikes = df.applymap(str)
    return df[
        textlikes.apply(
            lambda column: column.str.contains(regex, regex=True, case=case, na=False)
        ).any(axis=1)
    ]


def tsa_info(moving_avg = 7):
    url = 'https://www.tsa.gov/coronavirus/passenger-throughput'
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html')
    table = soup.find('table')
    table_body = table.find('tbody')
    rows = table_body.findAll('tr')
    data = []
    for row in rows:
        cols = row.findAll('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele if ele else 0 for ele in cols])
        
    tsa_data = pd.DataFrame(data,columns=['Date','2022','2021','2020','2019'])
    tsa_data.Date = pd.to_datetime(tsa_data.Date)
    tsa_data.index = tsa_data.Date
    tsa_data.drop(columns='Date',inplace=True)
    tsa_data = tsa_data.sort_index(ascending=True)
    tsa_data = tsa_data.apply(lambda x:x.str.replace(',','').astype('float'))
    tsa_sma = tsa_data[tsa_data.index.year == 2022].rolling(7).mean().fillna(0)
    tsa_sma['2020_indexed_2019'] = tsa_sma['2020']/tsa_sma['2019']
    tsa_sma['2021_indexed_2019'] = tsa_sma['2021']/tsa_sma['2019']
    tsa_sma['2022_indexed_2019'] = tsa_sma['2022']/tsa_sma['2019']
    tsa_sma['2019_index_line'] = 1.0
    tsa_sma.iloc[:,-4:].loc['2022'].plot(title = 'TSA Travelers, 7-day Moving Average')
    return tsa_sma.sort_values(by='Date',ascending = False),tsa_data
    

@st.cache(allow_output_mutation=True)
def star_data_input(files):
	cols = [0,1,2,3,5,6,7,8,12,13,14,15,17,18,19,20,24,25,26,27,29,30,31,32,34]
	star_df = pd.DataFrame()
	comp_set = pd.DataFrame()
	for path in files:
		try:
			if 'Monthly STAR Report' in pd.read_excel(path,sheet_name='Table of Contents',skiprows=2,usecols='B',header=0,nrows=0).columns[0]:
				date = pd.to_datetime(pd.read_excel(path,sheet_name='Glance',skiprows=4).iloc[0,1],infer_datetime_format=True)+MonthEnd(1)
				comps = pd.read_excel(path,sheet_name='Response',skiprows=21,usecols='C:L',header=0).dropna(axis=0,how = 'all').dropna(axis=1,how='all').dropna(subset=['Name'])
				star = pd.read_excel(path,sheet_name='Comp',skiprows=18,usecols='B:T',nrows=34,header=1,index_col=0,parse_dates=True).T
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
	#star_df=star_df.reset_index().drop_duplicates(subset=['index', 'STARID'], keep='last')
	comp_set = comp_set[~comp_set['STR#'].duplicated(keep='last')]
	#star_df.to_clipboard(header=False)
	star_df.columns = ['OCC_my_prop','OCC_comp','OCC_Index','OCC_Rank', 'OCC_per_chg_my_prop','OCC_per_chg_comp','OCC_per_chg_index','OCC_per_chg_rank','ADR_my_prop','ADR_comp','ADR_Index','ADR_Rank','ADR_per_chg_my_prop','ADR_per_chg_comp','ADR_per_chg_index','ADR_per_chg_rank','RevPAR_my_prop','RevPAR_comp','RevPAR_Index','RevPAR_Rank','RevPAR_per_chg_my_prop','RevPAR_per_chg_comp','RevPAR_per_chg_index','RevPAR_per_chg_rank','STARID']
	star_df=star_df.reset_index().drop_duplicates(subset=['index','STARID'],keep='last').set_index('index')
	print(comp_set)
	return star_df,comp_set

@st.cache(allow_output_mutation=True)             
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
	return star_df,comp_set


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
#with st.sidebar.header('1. Upload your ZIP file'):
 #   uploaded_file = st.sidebar.file_uploader("Excel-containing ZIP file", type=["zip"])
  #  st.sidebar.markdown("""
#[Example ZIP input file](https://github.com/dataprofessor/excel-file-merge-app/raw/main/nba_data.zip)
#""")

# File download
def filedownload(df):
    csv = df.to_csv()
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="merged_file.csv">Download Merged File as CSV</a>'
    return href

def xldownload(df):
    df.to_excel('data.xlsx')
    data = open('data.xlsx', 'rb').read()
    b64 = base64.b64encode(data).decode('UTF-8')
    #b64 = base64.b64encode(xl.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/xls;base64,{b64}" download="merged_file.xlsx">Download Merged File as XLSX</a>'
    return href

def main():
	menu = ['BOV','TSA Info','NewSupply','Comp Search']
	choice = st.sidebar.selectbox('Menu',menu)
	st.title('Explore Your Hotels!!!')
	if choice == 'BOV':
		st.write('''All the hotel data you can handle bro!''')
		st.subheader('BOV Analysis')
		multiple_files = st.file_uploader("STR Report File Dump - drop all the STR reports for your property here",accept_multiple_files=True)
		if st.button('Run STR Data from Multi-File Tool'):
			#@st.cache
			star_df,comp_set = star_data_input(multiple_files)
			st.header('**STR Compiled Data**')
			for star_id in star_df['STARID'].unique():
				st.write(comp_set[comp_set['Subj_prop'] == star_id].iloc[0,0],comp_set[comp_set['Subj_prop'] == star_id].iloc[0,1])
				st.line_chart(star_df[star_df.STARID == star_id][plot_cols])
				st.header('**STR Competitive Set**')
				st.write(comp_set[comp_set['Subj_prop'] == star_id])
				st.header('**STR Statistics**')
				st.write(star_df.reset_index())
				st.header('**Incoming Supply**')
				data  = dd.newsupply(float(comp_set.iloc[0,0]),7.0,'radius')
				st.write(data.dropna())
				data.rename(columns = {'Latitude':'lat','Longitude':'lon'},inplace=True)
				data.dropna(inplace=True)
				st.map(data)
			st.markdown(filedownload(star_df.reset_index()), unsafe_allow_html=True)
			st.markdown(xldownload(star_df.reset_index()), unsafe_allow_html=True)
		else:
			st.info('Awaiting for STR Reports to be uploaded.')
	elif choice == 'TSA Info':
		if st.button('Run TSA Latest Data'):
			#@st.cache
			tsa_sma, tsa_data = tsa_info()
			st.line_chart(tsa_sma.iloc[:,-3:].loc['2021'])
	elif choice == 'NewSupply':
		hotel = st.sidebar.selectbox('Select Hotel',name_str['Property'])
		st.sidebar.write(hotel, ' has the StarID of ',name_str[name_str.Property == hotel]['StarID'].item())
		data = dodge_pipeline[['Title','Address','City','State','PostalCode','Units','Open Date','Phase','Latitude','Longitude']]
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
			st.write(data.dropna())
			data.rename(columns = {'Latitude':'lat','Longitude':'lon'},inplace=True)
			data.dropna(inplace=True)
			st.map(data)
			st.header("File Download")
			csv = data.to_csv(index=False)
			b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
			href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
			st.markdown(href, unsafe_allow_html=True)
	elif choice == 'Comp Search':
		keys = st.sidebar.text_input("search hotel keywords")
		submit = st.sidebar.button('Search Hotel')
		chain_scale = st.sidebar.selectbox('Filter Comps by Chain Scale',str_census['Chain Scale'].unique())
		submit5 = st.sidebar.button('Filter Comp by Chain Scale')
		data = pd.DataFrame()
		hotel = pd.DataFrame()
		comps = pd.DataFrame()
		if submit:
			data = dd.str_lookup(keys)
		st.write(data)
		star = st.text_input('Enter Hotel Star')	
		submit2 = st.button('Retrieve Hotel')
		if submit2:
			hotel = dd.str_find(int(star))
		st.write(hotel)
		radius = st.text_input('Radius?')
		submit3 = st.button('Get Compset')
		if submit3:
			comps = dd.nearby_comps_str(int(star),radius=float(radius))
		st.write('### Full Dataset', comps)
		if submit5:
			st.write('Results:', comps.loc[(comps['Chain Scale']==chain_scale)])
		#selected_indices = st.multiselect('Select rows:', comps.index)
		#submit4 = st.button('Pull final compset')
		#if submit4:
		#	selected_rows = comps[comps['Hotel Name'].isin(list(selected_indices))]
		#st.write(comps)


#years = df["year"].loc[df["make"] = make_choice]
#year_choice = st.sidebar.selectbox('', years) 




if __name__ == '__main__':
	main()
			
	
# markets = 1
# brands= dodge_pipeline.Chain.dropna().unique()

# stars = dodge_census.StarID.dropna().unique()

# market = st.sidebar.selectbox('Select Market',dodge_pipeline[dodge_pipeline.State == state]['Submarket'].dropna().unique())

# brand = st.sidebar.selectbox('Select brand',brands)


# st.write(state)
# st.write(brand)



#broker = closings.groupby('Agent')
#sorted_region_unique = sorted(closings['Region name'].astype(str).unique())
#selected_region = st.sidebar.multiselect('Region name',sorted_region_unique, sorted_region_unique)
#sorted_city_unique = sorted(closings['City, ST'].astype(str).unique())
#selected_city = st.sidebar.multiselect('City, ST',sorted_city_unique, sorted_city_unique)
#date = st.sidebar.date_input('start date', dt.date(2000,1,1))
#st.write(date)

#sorted_city_unique = sorted(closings['City, ST'].astype(str).unique())
#selected_city = st.sidebar.multiselect('City, ST',sorted_city_unique, sorted_city_unique)
#st.write(closings[(closings['Sale Date'].dt.date >= date)&(closings['Region name'].isin(selected_region))])
#st.write(closings[(closings['Sale Date'].dt.date >= date)&(closings['Region name'].isin(selected_region))].describe())
#(closings['City, ST'].isin('selected_city'))&

# Main panel
#if st.sidebar.button('Submit'):
#	#@st.cache
#	star_df,comp_set = star_data_input_zip(uploaded_file)
#	st.header('**STR Compiled Data**')
#	st.write(comp_set)
#	st.write(star_df)
#	st.markdown(filedownload(star_df), unsafe_allow_html=True)
#	st.markdown(xldownload(star_df), unsafe_allow_html=True)
#	st.line_chart(star_df[['OCC_my_prop','ADR_my_prop','RevPAR_my_prop']])
#else:
#	st.info('Awaiting for ZIP file to be uploaded.')
	
