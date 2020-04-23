# First Test to download data from Earth Engine

### JUST TESTING ###

#%%
import ee

#%%
ee.Initialize()

#%%
img = ee.Image('LANDSAT/LT05/C01/T1_SR/LT05_034033_20000913')
print(img)
print(img.getInfo())

#%%
import tensorflow as tf
tf.enable_eager_execution()
import folium
EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token=4/pAH330U5u5VXTbzGotUM5VIn-mnI1RRR7WLlDjOpYw2luqJtZ14ultM'

#%%
# Use these bands for prediction.
bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']
# Use Landsat 8 surface reflectance data.
l8sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')

#%%
# Cloud masking function.
def maskL8sr(image):
  cloudShadowBitMask = ee.Number(2).pow(3).int()
  cloudsBitMask = ee.Number(2).pow(5).int()
  qa = image.select('pixel_qa')
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
    qa.bitwiseAnd(cloudsBitMask).eq(0))
  return image.updateMask(mask).select(bands).divide(10000)

#%%
# The image input data is a 2018 cloud-masked median composite.
image = l8sr.filterDate('2018-01-01', '2018-12-31').map(maskL8sr).median()

#%%
# Use folium to visualize the imagery.
mapid = image.getMapId({'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3})
map = folium.Map(location=[38., -122.5])
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='median composite',
  ).add_to(map)
map.add_child(folium.LayerControl())
map

#%%
# Change the following two lines to use your own training data.
labels = ee.FeatureCollection('projects/google/demo_landcover_labels')
label = 'landcover'

#%%
# Sample the image at the points and add a random column.
sample = image.sampleRegions(
  collection=labels, properties=[label], scale=30).randomColumn()

#%%
# Partition the sample approximately 70-30.
training = sample.filter(ee.Filter.lt('random', 0.7))
testing = sample.filter(ee.Filter.gte('random', 0.7))

#%%
from pprint import pprint

# Print the first couple points to verify.
pprint({'training': training.first().getInfo()})
pprint({'testing': testing.first().getInfo()})

