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
bands = ['avg_vis']
# Satellite data
sat_dat = 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS'
# Use Landsat 8 surface reflectance data.
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
with open("Data/geo_data/NUTS_RG_01M_2016_4326_LEVL_2.geojson") as f:
    nuts2_poly = json.load(f)

#%%
gdp_data = pd.read_csv('Data/gdp_data/nuts_gdp_cleaned.csv')
gdp_data.head()

#%%
# Specify patch and file dimensions.
imageExportFormatOptions = {
  'patchDimensions': [256, 256],
  'maxFileSize': 917334556,
  'compressed': True
}

#%%
gdp_data[gdp_data['region']==nuts2_poly['features'][21]['properties']['NUTS_ID']]

#%%
nuts2_poly['features'][331]['properties']

#%%
regions = []
years = []
gdp_values = []
for i in range(332):
    if nuts2_poly['features'][i]['properties']['NUTS_ID'] not in gdp_data['region'].values:
        print(str(i)+': Not in regions.')
    elif nuts2_poly['features'][i]['geometry']['type'] == 'MultiPolygon':
        print(str(i)+': MultiPolygon.')
    else:
        t = nuts2_poly['features'][i]['geometry']['coordinates']
        region = nuts2_poly['features'][i]['properties']['NUTS_ID']
        for index, row in gdp_data[gdp_data['region']==nuts2_poly['features'][i]['properties']['NUTS_ID']].iterrows():
            if row['year'] >= 2014:
                print('After 2014')
            else:
                region = ee.Geometry.Polygon(t)
                dataset = ee.ImageCollection(sat_dat) \
                    .filterBounds(region) \
                    .filterDate((str(row['year'])+'-01-01'),(str(row['year'])+'-12-31')) \
                    .select(bands)
                    #.map(maskL8sr)
                dataset = dataset.reduce('median')
                task = ee.batch.Export.image.toDrive(image=dataset.clip(region),
                                        description=(row['region']+'_'+str(row['year'])),
                                        folder="nuts_night_all",
                                        region=region['coordinates'],
                                        scale=30,
                                        fileFormat='GeoTIFF',
                                        maxPixels= 3784216672400,
                                        skipEmptyTiles=True)

                task.start()
                
                regions.append(region)
                years.append(row['year'])
                gdp_values.append(row['value'])
                print(str(i)+': '+row['region']+str(row['year'])+' will be downloaded.')



#%%
# Print all tasks.
print(ee.batch.Task.list())

#%%
for i in range(332):
    print(nuts2_poly['features'][i]['properties']['NUTS_ID'])


#%%
