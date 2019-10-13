#%%
# Import libraries
import ee
import json
import numpy as np
import pandas as pd

#%%
ee.Initialize()

#%%
# Cloud masking function
def maskL8sr(image, bands = ['B1','B2', 'B3']):
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
len(nuts2_poly['features'])

#%%
t = nuts2_poly['features'][2]['geometry']['coordinates']
area = nuts2_poly['features'][2]['properties']['NUTS_NAME']

#%%
# Specify patch and file dimensions.
imageExportFormatOptions = {
  'patchDimensions': [256, 256],
  'maxFileSize': 104857600,
  'compressed': True,
  'collapseBands':True
}

#%%
# Load satellite imagery to gdrive
region = ee.Geometry.Polygon(t)
dataset = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
    .filterBounds(region) \
    .filterDate('2016-01-01', '2016-12-31') \
    .map(maskL8sr)
dataset = dataset.reduce('median')
task = ee.batch.Export.image.toDrive(image=dataset.clip(region),
                                      description=area,
                                      folder="testing",
                                      region=region['coordinates'],
                                      scale=30,
                                      fileFormat='TFRecord',
                                      formatOptions=imageExportFormatOptions,
                                      skipEmptyTiles=True)
task.start()

#%%
gdp_data[gdp_data['region']==nuts2_poly['features'][21]['properties']['NUTS_ID']]

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
            region = ee.Geometry.Polygon(t)
            dataset = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA') \
                .filterBounds(region) \
                .filterDate((str(row['year'])+'-01-01'),(str(row['year'])+'-12-31')) \
                .map(maskL8sr)
            dataset = dataset.reduce('median')
            task = ee.batch.Export.image.toDrive(image=dataset.clip(region),
                                      description=(row['region']+'_'+str(row['year'])),
                                      folder="nuts_tfrecords",
                                      region=region['coordinates'],
                                      scale=30,
                                      fileFormat='TFRecord',
                                      formatOptions=imageExportFormatOptions,
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
