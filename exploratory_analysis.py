#%%
# Import libraries
import pandas as pd
import numpy as np
import re

#%%
# Import gdp data
gdp_data = pd.read_excel("Data/nuts2_gdp.xls",sheet_name='Data',skiprows=530,nrows=516)
gdp_data.head()

#%%
country_code = pd.read_csv("Data/country_codes.csv", delimiter=";")
country_code.head()

#%%
gdp_long = pd.melt(gdp_data, id_vars=['GEO/TIME'],value_vars=['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017'])
gdp_long.head()

#%%
gdp_long['countries'] = gdp_long['GEO/TIME'].str.extract('([^0-9]+)', expand=False).str.strip()
gdp_long.head()

#%%
gdp_nuts = gdp_long.merge(country_code,how = 'left' ,left_on = 'countries', right_on = 'Code')
gdp_nuts.head()

#%%
gdp_cleaned = gdp_nuts[gdp_nuts['Country'].isnull() == False].drop(columns = ['countries'])
gdp_cleaned.columns = ['region','year','value','code','country']

#%%
#gdp_cleaned.to_csv("data/nuts_gdp_cleaned.csv", index = False)

#%%
# Number of missing values
gdp_cleaned.isna().sum()

#%%
gdp_cleaned.groupby(['country','year'])['value'].to_list()

#%%
