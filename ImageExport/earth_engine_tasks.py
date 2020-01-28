#%%
# Import libraries
import ee
import json
import numpy as np
import pandas as pd

#%%
ee.Initialize()

#%%
# Use these bands for prediction.
#bands = ['B1','B2','B3']
bands = ['avg_rad']
# Satellite data
#sat_dat = 'LANDSAT/LE07/C01/T1_SR' # Daytime images (From 1999 to Present)
#sat_dat = 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS' # Night images (From 1992 to 2014)
sat_dat = 'NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG' #Night images (2014 to present)

# Use Set Images
l8sr = ee.ImageCollection(sat_dat)

# Cloud masking function
def maskL8sr(image):
  cloudShadowBitMask = ee.Number(2).pow(3).int()
  cloudsBitMask = ee.Number(2).pow(5).int()
  qa = image.select('pixel_qa')
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
    qa.bitwiseAnd(cloudsBitMask).eq(0))
  return image.updateMask(mask).select(bands).divide(10000)


#%%
# Open the geojson of NUTS 2 regions to get the coordinates of the regions
with open("/Users/maxbehrens/Documents/Msc/Thesis/Data/geo_data_2016/NUTS_RG_01M_2016_4326_LEVL_2.geojson") as f:
    nuts2_poly_2016 = json.load(f)

with open("/Users/maxbehrens/Documents/Msc/Thesis/Data/geo_data_2013/NUTS_RG_01M_2013_4326_LEVL_2.geojson") as f:
    nuts2_poly_2013 = json.load(f)

with open("/Users/maxbehrens/Documents/Msc/Thesis/Data/geo_data_2010/NUTS_RG_01M_2010_4326_LEVL_2.geojson") as f:
    nuts2_poly_2010 = json.load(f)

with open("/Users/maxbehrens/Documents/Msc/Thesis/Data/geo_data_2006/NUTS_RG_01M_2006_4326_LEVL_2.geojson") as f:
    nuts2_poly_2006 = json.load(f)

#%%
# Identify number of multipolygons
tot = 0
multi = 0
single = 0
big_multi = 0
for i in range(len(nuts2_poly_2016['features'])):
    if nuts2_poly_2016['features'][i]['geometry']['type'] == 'MultiPolygon':
        multi += 1
        sum_poly = 0
        for k in range(1,len(nuts2_poly_2016['features'][i]['geometry']['coordinates'])):
            sum_poly += len(nuts2_poly_2016['features'][i]['geometry']['coordinates'][k][0])
        big_multi += int(len(nuts2_poly_2016['features'][i]['geometry']['coordinates'][0][0])<sum_poly)
    else:
        single += 1
    tot += 1

print('Total length:',tot)
print('No. multi: ',multi)
print('No. single: ',single)
print(big_multi)

#%%
# Get the cleaned GDP data to match with regions and download correct data
gdp_data = pd.read_csv('/Users/maxbehrens/Documents/Msc/Thesis/Data/gdp_data/nuts_gdp_cleaned.csv')
gdp_data.head()

#%%
# Specify patch and file dimensions. Only needed for TFrecords files - not used anymore
imageExportFormatOptions = {
  'patchDimensions': [256, 256],
  'maxFileSize': 917334556,
  'compressed': True
}

#%%
# Test logic
gdp_data[gdp_data['region']==nuts2_poly_2006['features'][42]['properties']['NUTS_ID']]

#%%
# Test the json structure
len(nuts2_poly_2016['features'])#[331]['properties']

#%%
# Download the data from Earth Engine and save into Google Drive
folder = 'nuts_viirs'
scale = 80

regions = []
years = []
gdp_values = []

for index, row in gdp_data.iloc[3745:].iterrows():
    
    if row['year'] >= 2014:
        for i in range(len(nuts2_poly_2016['features'])):
            if row['region'] == nuts2_poly_2016['features'][i]['properties']['NUTS_ID']:
                
                if nuts2_poly_2016['features'][i]['geometry']['type'] == 'MultiPolygon':
                    t = nuts2_poly_2016['features'][i]['geometry']['coordinates'][0]
                else:    
                    t = nuts2_poly_2016['features'][i]['geometry']['coordinates']

                region = nuts2_poly_2016['features'][i]['properties']['NUTS_ID']
                area_name = row['region']+'_'+str(row['year'])
                region = ee.Geometry.Polygon(t)
                
                dataset = ee.ImageCollection(sat_dat) \
                    .filterBounds(region) \
                    .filterDate((str(row['year'])+'-01-01'),(str(row['year'])+'-12-31')) \
                    .select(bands) 
                    #.map(maskL8sr) \ 
                dataset = dataset.reduce('mean')
                task = ee.batch.Export.image.toDrive(image=dataset.clip(region),
                                        description=area_name,
                                        folder=folder,
                                        region=region['coordinates'],
                                        scale=scale,
                                        fileFormat='GeoTIFF',
                                        maxPixels= 3784216672400,
                                        skipEmptyTiles=True)

                task.start()
                
                regions.append(region)
                years.append(row['year'])
                gdp_values.append(row['value'])
                print(str(row['region'])+': '+row['region']+str(row['year'])+' will be downloaded.')

    # Only for night
    else:
        pass


# %%
for i in range(len(nuts2_poly_2006['features'])):
    print(nuts2_poly_2006['features'][i]['properties']['NUTS_ID'])

# %%
i = 0
for index, row in gdp_data.iterrows():
    if row['year'] < 2015 and len(row['region']) > 2:
        i += 1
    else:
        pass

print(i)

# %%
