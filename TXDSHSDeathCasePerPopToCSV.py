import math
import os
import time
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


def per_pop(df):
    '''
    helper function that removes all rows that do not describe counties from death csv and that calculates death per population
    inputs: death by county excel sheet
    outputs: cumulative death by county and death per population csv

    notes:
    index in col 0 bc we converted the csv into a dataframe
    county name in col 1
    county population size in col 2
    daily new death count starting col 3               
    '''
    #preps to name output csv by extractsing date of latest update from the name of first column before we delete the column and deletes orig Excel files
    if run == "death_df": 
        name = "Deaths by Population_" + list(df.columns.values)[0] 
        os.remove('/Users/Dino-Sunlight/Downloads/Texas COVID-19 Fatality Count Data by County.xlsx')
    elif run == "case_df":
        name = "Cases by Population_" + list(df.columns.values)[0]
        os.remove('/Users/Dino-Sunlight/Downloads/Texas COVID-19 Case Count Data by County.xlsx')
    else:
        print("What the heck. Neither case or death dataframe.")
    name = name.replace("/","-")
    row_count = 0 #initializes row_count
     #drops titular rows, "Unknown" row, and anything after "Total" row. For some reason, row[0] gives the index, population is a string, but all cases/deaths are integers    
    for row in df.itertuples():
        if type(row[3]) != int or row_count == math.inf or row[1] == "Unknown":
            df.drop(index = row[0], axis = 0, inplace = True)
        elif row[1] == "Total": #lol this is finally working
            row_count = math.inf
        row_count += 1
        #test 
        #print(row_count, "", df.head(10))
    #remove all but 1st, 2nd, and last columnn
    df.drop(df.columns.to_series()[2:(len(df.columns) - 1)], axis = 1, inplace = True) #assume that the index column is not counted as a column       

    #translate population entry from string to float, then rename columns and create and populate 'per capita' column. Would be more efficient if I called on columns by their index instead of name
    if run == "death_df":
        df.columns = ['County','Total Population','Cumulative Deaths']
        df['Total Population'] = pd.to_numeric(df['Total Population'])
        df.loc[:,"Cumulative Deaths per 100,000 Population"] = (df.loc[:,'Cumulative Deaths']) / (df.loc[:,'Total Population']) * 10**5
    elif run == "case_df":
        df.columns = ['County','Total Population','Cumulative Cases']
        df['Total Population'] = pd.to_numeric(df['Total Population']) #running into issues because TXDSHS added new "unknown" county row on July 27, 2020
        df.loc[:,"Cumulative Cases per 100,000 Population"] = (df.loc[:,'Cumulative Cases']) / (df.loc[:,'Total Population']) * 10**5
    #sort dataframe by population of county
    total = df.tail(1) #stores the total row before deleting it
    df.drop(df.tail(1).index,inplace=True)
    df.sort_values(by = "Total Population", inplace = True, ascending = False) #sorts
    df.append(total, ignore_index = True) #adds total row back in
    #return this edited dataframe as a csv
    df.to_csv(name + '.csv', index = False) #change naming to the original name of the first column, first row
    print(".csv created.")


#automated download of Texas Fatality Data by County ((and hospitalizations at some point??)) and then plug it into helper function
CD_PATH = '/Users/Dino-Sunlight/Desktop/COVIDeeDesktop/chromedriver'

chromeOptions = webdriver.ChromeOptions()
#prefs = {"download.default_directory" : dl_directory}
#chromeOptions.add_experimental_option("prefs",prefs)

#downloads death data from TXDSHS website
driver = webdriver.Chrome(executable_path=CD_PATH)
website = 'https://dshs.texas.gov/coronavirus/AdditionalData.aspx'
driver.get(website)
driver.find_element_by_xpath("/html/body[@id='bodymain']/form[@id='aspnetForm']/div[@id='body']/div[@class='container']/div[@id='ctl00_ContentPlaceHolder1_ContentPageColumnCenter']/div[@id='ctl00_ContentPlaceHolder1_pnlContent']/div[@class='content editorStyles']/div[@id='ctl00_ContentPlaceHolder1_uxContent']/ul[1]/li[2]/a").click()

#pauses code 5 seconds to allow for last download to complete
time.sleep(5)

#run helper function for death by county Excel file from TXDSHS
death_df = pd.read_excel('/Users/Dino-Sunlight/Downloads/Texas COVID-19 Fatality Count Data by County.xlsx') #be aware -- this is a very specific call to load data. LOL ok it takes the first row as column titles....great...
run = "death_df"
per_pop(death_df) #does it not finish this before running the below?!

#downloads case data by county; it seems like I need to re-declare the driver for each download. 
#Note that case data columns are formatted with a few lines between the words, but ultimately converts fine from excel to df to csv, dimensions (276, 134) why 134 on July 16?
driver = webdriver.Chrome(executable_path=CD_PATH)
website = 'https://dshs.texas.gov/coronavirus/AdditionalData.aspx'
driver.get(website)
print(driver.title)
driver.find_element_by_xpath("/html/body[@id='bodymain']/form[@id='aspnetForm']/div[@id='body']/div[@class='container']/div[@id='ctl00_ContentPlaceHolder1_ContentPageColumnCenter']/div[@id='ctl00_ContentPlaceHolder1_pnlContent']/div[@class='content editorStyles']/div[@id='ctl00_ContentPlaceHolder1_uxContent']/ul[1]/li[1]/a").click()

#pauses code 5 seconds to allow for last download to complete
time.sleep(5)

#run helper function for case by county Excel file from TXDSHS
case_df = pd.read_excel('/Users/Dino-Sunlight/Downloads/Texas COVID-19 Case Count Data by County.xlsx') #be aware -- this is a very specific call to load data. LOL ok it takes the first row as column titles....great...
run = "case_df"
per_pop(case_df)