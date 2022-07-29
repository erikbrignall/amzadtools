# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:14:21 2022

@author: erikb
"""

import pandas as pd #load the pandas library with alias pd
import numpy as np # load numpy for NaN substition
import json
import streamlit as st

fields = ["Customer Search Term","Spend","14 Day Total Sales","Campaign Name"]

# function to find substrings for a given campaign name
def findsubstrings(c):
    dfc = df[df['Campaign Name'] == c]
    kwlist = dfc['Query'].tolist()

    substringlist = [] #loop to split word list into seperate words
    for x in kwlist:
        split_results = x.split(' ')
        z = 0
        for y in split_results:
            substringlist.append(split_results[z])
            z = z+1

    substringlist = [item.lower() for item in substringlist] #make sure all lower to remove duplicates caused by capitalisation
    substringlist = set(substringlist) # turn list into unique set of words
    return(substringlist)

# for a given ss and campaign return a list of ss, campaign, total rev, total cost, ROAS
def sscalc(ss,c):
    dfss = df.loc[(df['Query'].str.contains(ss,regex=False)) & (df['Campaign Name'] == c)]
    dfss['Cost'] = dfss['Cost'].astype('float')
    dfss['Revenue'] = dfss['Revenue'].astype('float')
    cost = dfss['Cost'].sum()
    if cost == 0:
        cost = 0.0001
    rev = dfss['Revenue'].sum()
    if rev == 0:
        rev = 0.0001
    roas = rev/cost
    ssrow = [ss,c,rev,cost]
    return(ssrow)

def clean_negatives(dfc):
    dfc = dfc[dfc['cost'] > 10]
    stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
    dfc = dfc[~dfc.ss.isin(stopwords)]
    return(dfc)

st.title('Negative Substring analysis')
st.write('Please upload the Search query report for analysis')
st.text('Note: this should include the fields: Customer Search Term, Spend, 14 Day Total Sales, Campaign Name')

# Upload data to analyse
uploaded_file = st.file_uploader("Upload Search Query File")

if uploaded_file is not None:
    #read csv
    df=pd.read_csv(uploaded_file)
    st.write("csv successfully uploaded")
    df = df[fields]
    #st.dataframe(df)

    #cols = ['Campaign Name','Query','Cost','Revenue']
    cols = ['Query','Cost','Revenue','Campaign Name']
    df.columns = cols
    #df.head()

    # analysis should be run at a campaign level
    # create a set of campaign names
    campaigns = set(df["Campaign Name"])

    # initialise list to hold all substring/ campaign combinations
    results_list = []

    # for each campaign find a list of substrings 
    with st.spinner("calculating..."):
        for c in campaigns:
            dfc = df[df['Campaign Name'] == c]
            kwlist = dfc['Query'].tolist()
    
            # find all substrings in specific campaign
            substrings = findsubstrings(c)
    
            for ss in substrings:
                x = sscalc(ss,c)
                results_list.append(x)
    
            dfresults = pd.DataFrame(results_list, columns = ['ss', 'c','rev','cost'])

    dfresults = clean_negatives(dfresults)

    dfresults['ROAS'] = dfresults['rev']/dfresults['cost']
    dfresults = dfresults[dfresults['ROAS'] < 0.3]
    dfresults = dfresults.sort_values(by=['cost'], ascending=False)
    dfresults.loc[dfresults['ROAS'] < 0.01, 'ROAS'] = 0
    dfresults.loc[dfresults['rev'] < 0.01, 'rev'] = 0
    dfresults = dfresults.reset_index(drop=True)
    dfresults = dfresults[['ss','c','cost','rev','ROAS']]

    # find approximate revenue lost through these substrings, de-duping where they are together
    ucosts = dfresults['cost'].unique()
    cost = ucosts.sum()
    #cost = dfresults['cost'].sum()
    cost = cost.round(2)
    st.write("Approx. spend on keywords with low performing substrings: ")
    st.write(cost)
    
    st.dataframe(dfresults)

    @st.cache
    def convert_df(df):
       return df.to_csv().encode('utf-8')


    csv = convert_df(dfresults)

    st.download_button(
          "Press to Download",
          csv,
          "file.csv",
          "text/csv",
          key='download-csv'
        )