#%%
# Import libraries
import pandas as pd
import numpy as np
import re

#%%
# Import gdp data
gdp_data = pd.read_excel("Data/gdp_data/nuts2_gdp.xls",sheet_name='Data',skiprows=530,nrows=516)
gdp_data.head()

#%%
# Import NUTS 2 country metainfos
country_code = pd.read_csv("Data/gdp_data/country_codes.csv", delimiter=";")
country_code.head()

#%%
# Reshape to long format
gdp_long = pd.melt(gdp_data, id_vars=['GEO/TIME'],value_vars=['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017'])
gdp_long.head()

#%%
# Extract the country codes from column
gdp_long['countries'] = gdp_long['GEO/TIME'].str[:2]
gdp_long.head()

#%%
# Merge with country infos
gdp_nuts = gdp_long.merge(country_code,how = 'left' ,left_on = 'countries', right_on = 'Code')
gdp_nuts.head()

#%%
# Drop rows where country is not recorded
gdp_cleaned = gdp_nuts[(gdp_nuts['Country'].isnull() == False) & (gdp_nuts['value'].isnull() == False)].drop(columns = ['countries'])
gdp_cleaned.columns = ['region','year','value','code','country']

#%%
# Save the cleaned data frame
gdp_cleaned.to_csv("Data/gdp_data/nuts_gdp_cleaned.csv", index = False)

#%%
# Sanity check
# Number of missing values
gdp_cleaned.isna().sum()

#%%
# Test
gdp_cleaned.groupby(['country','year'])['value'].to_list()

#%%
