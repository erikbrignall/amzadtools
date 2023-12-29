# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 18:29:51 2022

@author: erikb
"""

import pandas as pd #load the pandas library with alias pd
import numpy as np # load numpy for NaN substition
#import json
import streamlit as st

fields = ["Match Type","Customer Search Term","Clicks","Spend","14 Day Total Sales","Campaign Name","14 Day Total Orders (#)"]

st.title('Search Query Report Recommendations')
st.header('KW Data Summary:')
st.sidebar.title('Upload file for analysis:')
st.sidebar.write('Please upload the Search query report (xlsx) for analysis')
st.sidebar.write('Note: this should include the fields: Customer Search Term, Spend, 14 Day Total Sales, Campaign Name, 14 Day Total Orders (\#)')

pw = "pass123"

# Upload data to analyse
uploaded_file = st.sidebar.file_uploader("Upload Search Query File")

if uploaded_file is not None and pw == "pass123":
    #read csv
    df=pd.read_excel(uploaded_file)
    st.sidebar.write("csv successfully uploaded")
    # PRE-PROCESSING DATA
    df = df[['Portfolio name','Campaign Name','Ad Group Name','Targeting','Match Type','Customer Search Term','Impressions'\
    ,'Clicks','Spend','14 Day Total Sales ','14 Day Total Orders (#)','14 Day Advertised ASIN Units (#)','14 Day Brand Halo ASIN Sales ']]

    cols = ['portfolio','campaign','adgroup','keyword','match_type','query','impressions','clicks','cost','revenue','conversions','units_same','revenue_halo']
    df.columns = cols
    df = df.sort_values(by=['cost'], ascending=False)

    # OVERALL SUMMARY STATS
    total_rev = df['revenue'].sum().astype(int)
    total_cost = df['cost'].sum().astype(int)
    total_queries = len(df)
    total_campaigns = df['campaign'].nunique()

    st.write(total_rev)
    st.write(total_cost)
    st.write(total_queries)
    st.write(total_campaigns)
     
    #get brand level summary table
    st.subheader("Brand performance summary table")
    dfBrand = pd.pivot_table(df,index=['Brand'],values=['cost','revenue','conversions','clicks'], aggfunc=np.sum)
    dfBrand.reset_index(inplace=True)
    dfBrand['ROAS'] = dfBrand['revenue']/dfBrand['cost']
    dfBrand['AOV'] = dfBrand['revenue']/dfBrand['conversions']
    dfBrand['CVR'] = dfBrand['conversions']/dfBrand['clicks']
    st.dataframe(dfBrand)
    
    st.subheader("Brand/ Non Brand performance summary table")
    # Brand non brand summary
    
    #st.dataframe(dfBNonB)
    
    # Match type level performance
    #st.subheader("Match Type performance summary table")
    
    #st.dataframe(dfBNonB)
    


    #st.header('Negative Substring analysis')
    #st.write('Please upload the Search query report for analysis')
    #st.text('Note: this should include the fields: Customer Search Term, Spend, 14 Day Total Sales, Campaign Name')

