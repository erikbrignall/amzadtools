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

st.title('Search Query Report Analyser')
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
    total_roas = total_rev/total_cost
    total_roas = total_roas.round(2)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Total Revenue", value=total_rev)
    col2.metric(label="Total Spend", value=total_cost)
    col3.metric(label="Total Queries", value=total_queries)
    col4.metric(label="Total ROAS", value=total_roas)
    col5.metric(label="Total Campaigns", value=total_campaigns)
    #st.write(total_queries)
    #st.write(total_campaigns)

    desc = {"Veet": "Veet","Vanish":"Vanish","Finish": "Finish", "Calgon": "Calgon","Harpic": "Harpic", "Air Wick": "Air Wick", "Botanica": "Botanica", "Cillit" : "Cillit Bang", "Mr Sheen": "Mr Sheen", "Durex": "Durex", "Scholl": "Scholl"}

    # add brand column
    def check_kw(x):
        for key in desc:
            if key.lower() in x.lower():
                return desc[key]
        return ''
    
    df["Brand"] = df["campaign"].map(lambda x: check_kw(x))
    df['Brand'].replace("","Other", inplace=True)

    brands = 'finish|vanish|air wick|calgon|airwick|cillit|durex|sagrotan|botanica|scholl|sheen|veet|harpic'
    df.loc[df['query'].str.contains(brands),'brandkw'] = "Branded"
    df['brandkw'].fillna("Non Branded", inplace=True)

    #get brand level summary table
    st.subheader("Brand performance summary table")
    dfBrand = pd.pivot_table(df,index=['Brand'],values=['cost','revenue','conversions','clicks'], aggfunc=np.sum)
    dfBrand.reset_index(inplace=True)
    dfBrand['ROAS'] = dfBrand['revenue']/dfBrand['cost']
    dfBrand['AOV'] = dfBrand['revenue']/dfBrand['conversions']
    dfBrand['CVR'] = dfBrand['conversions']/dfBrand['clicks']
    dfBrand = dfBrand.sort_values(by='cost', ascending=False)
    st.dataframe(dfBrand)
    
    st.subheader("Brand/ Non Brand performance summary table")
    # Brand non brand summary
    dfBNonB = pd.pivot_table(df,index=['brandkw'],values=['cost','revenue','conversions','clicks'], aggfunc=np.sum)
    dfBNonB.reset_index(inplace=True)
    dfBNonB['ROAS'] = dfBNonB['revenue']/dfBNonB['cost']
    dfBNonB['AOV'] = dfBNonB['revenue']/dfBNonB['conversions']
    dfBNonB['CVR'] = dfBNonB['conversions']/dfBNonB['clicks']
    st.dataframe(dfBNonB)
    
    # Match type level performance
    st.subheader("Match Type performance summary table")
    dfMT = pd.pivot_table(df,index=['match_type'],values=['cost','revenue','conversions','clicks'], aggfunc=np.sum)
    dfMT.reset_index(inplace=True)
    dfMT['ROAS'] = dfMT['revenue']/dfMT['cost']
    dfMT['AOV'] = dfMT['revenue']/dfMT['conversions']
    dfMT['CVR'] = dfMT['conversions']/dfMT['clicks']
    st.bar_chart(dfMT, x="match_type", y=["cost","revenue"])
    st.dataframe(dfMT)
    


    #st.header('Negative Substring analysis')
    #st.write('Please upload the Search query report for analysis')
    #st.text('Note: this should include the fields: Customer Search Term, Spend, 14 Day Total Sales, Campaign Name')

