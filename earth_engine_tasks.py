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
def maskL8sr(image, bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']):
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
print(nuts2_poly['features'][2]['properties']['NUTS_ID'])

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
# Print all tasks.
print(ee.batch.Task.list())

#%%
