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
bands = ['B1','B2','B3']
bands = ['avg_vis']
# Satellite data
#sat_dat = 'LANDSAT/LE07/C01/T1_SR' # Daytime images (From 1999 to Present)
sat_dat = 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS' # Night images (From 1992 to 2014)

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
with open("Data/geo_data/NUTS_RG_01M_2016_4326_LEVL_2.geojson") as f:
    nuts2_poly = json.load(f)

#%%
# Get the cleaned GDP data to match with regions and download correct data
gdp_data = pd.read_csv('Data/gdp_data/nuts_gdp_cleaned.csv')
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
gdp_data[gdp_data['region']==nuts2_poly['features'][21]['properties']['NUTS_ID']]

#%%
# Test the json structure
nuts2_poly['features'][331]['properties']

#%%
# Download the data from Earth Engine and save into Google Drive
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
            area_name = row['region']+'_'+str(row['year'])
            if row['year'] >= 2014:
                print('After 2014')
            # Used if data was not fully downloaded
            #if area_name in files:
            #    print('Already Downloaded.')
            else:
                region = ee.Geometry.Polygon(t)
                dataset = ee.ImageCollection(sat_dat) \
                    .filterBounds(region) \
                    .filterDate((str(row['year'])+'-01-01'),(str(row['year'])+'-12-31')) \
                    .select(bands)
                    #.map(maskL8sr) \    
                dataset = dataset.reduce('mean')
                task = ee.batch.Export.image.toDrive(image=dataset.clip(region),
                                        description=area_name,
                                        folder="nuts_night",
                                        region=region['coordinates'],
                                        scale=80,
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
