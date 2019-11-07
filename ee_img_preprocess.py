# -*- coding: utf-8 -*-
#%%
# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import pyrsgis
from skimage.transform import resize
from PIL import Image
from matplotlib import pyplot as plt
from os import listdir
from os.path import isfile, join

#%%
al01_2016_path = "/gdrive/My Drive/nuts_night/DE22_2012.tif"

ds1, featuresAL01 = pyrsgis.raster.read(al01_2016_path)

print("AL01 shape: ",featuresAL01.shape)
print(featuresAL01[:10,:10])

featuresAL01.shape[0]

# Reshape image to be a rectangle
raw_list = []
i_prev = 0

for i in range(0,featuresAL01.shape[0],2):
  if i != 0:
    raw_list.append(h_temp) 
  h_temp = None
  for k in range(0,featuresAL01.shape[1],5):
    if np.any(np.isnan(featuresAL01[i:i+2,k:k+5])) == False:
      if h_temp is None:
        h_temp = featuresAL01[i:i+2,k:k+5]
      else:
        h_temp = np.hstack((h_temp,featuresAL01[i:i+2,k:k+5]))
    else:
      pass

print(len(raw_list))

featuresAL01[1:1+2,1:1+5]

al01_resized = resize(test, (2000,2000))

plt.imshow(al01_resized, interpolation='nearest')
plt.show()

al01_resized.shape

mypath = "/gdrive/My Drive/nuts_night/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# Reshape the image to have a rectangle shape

y_dat = pd.read_csv("/gdrive/My Drive/ThesisData/Data/nuts_gdp_cleaned.csv")
y_dat.head()

split1 = onlyfiles[0].rsplit('_',1)[0]
print(split1)
split2 = int(onlyfiles[0].rsplit('_',1)[1].rsplit('.',1)[0])
print(split2)

y_dat.loc[(y_dat['region']==split1) & (y_dat['year']==split2),'value']

def create_data(files,path, resolution = 256):
  x = []
  y = []
  label = []
  for f in files:
    ds, temp = pyrsgis.raster.read(str(path+f))
    #temp = temp.swapaxes(0,2)
    temp_resized = resize(temp, (resolution, resolution))
    x.append(temp_resized)
    split1 = f.rsplit('_',1)[0]
    split2 = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
    y.append(y_dat.loc[(y_dat['region']==split1) & (y_dat['year']==split2),'value'])
    label.append(f)
  return x, y, label

res = 32
x,y,label = create_data(onlyfiles,mypath, resolution=res)

print('Shape of x: ',len(x))
print('Shape of y: ',len(y))
print('Shape of labels: ', len(label))

"""## TO DO:



1.   Maybe adjust sampling method: First create rectangle shaped picture and the rescale
2.   Review literature, how they handled high res images
3.   Write function for correct train, validation and test split -> not the same locations in train and test
"""

regions = []
for i in range(len(label)):
  regions.append(label[i].rsplit('_',1)[0])

regions = np.unique(regions)
print(len(regions))

msk = np.random.rand(len(regions)) < 0.7
train_split = regions[msk]
test_split = regions[~msk]
print(len(train_split))
print(len(test_split))

import math
label_train = []
label_test = []
x_train = []
y_train = []
x_test = []
y_test = []
for i in range(len(label)):
  if label[i].rsplit('_',1)[0] in train_split:
    if math.isnan(y[i]):
      pass
    else:
      label_train.append(label[i])
      x_train.append(x[i])
      y_train.append(int(y[i]))
  else:
    if math.isnan(y[i]):
      pass
    else:
      label_test.append(label[i])
      x_test.append(x[i])
      y_test.append(int(y[i]))
  
label_train = np.array(label_train)
label_test = np.array(label_test)
x_train = np.array(x_train)
x_test = np.array(x_test)
y_train = np.array(y_train)
y_test = np.array(y_test)  
print(x_train.shape)
print(x_test.shape)
print(y_test.shape)

x_train = np.array([x_train])
x_train = np.moveaxis(x_train,0,-1)
print(x_train.shape)
x_test = np.array([x_test])
x_test = np.moveaxis(x_test,0,-1)
print(x_test.shape)

x_train = np.nan_to_num(x_train)
x_test = np.nan_to_num(x_test)

# Standard Model
model = tf.keras.Sequential()

model.add(tf.keras.layers.Conv2D(filters=64,kernel_size=3, kernel_initializer='normal', input_shape=(64,64,1), activation='relu'))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(units=128, activation='relu'))
model.add(tf.keras.layers.Dense(units=1, activation = 'linear'))

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mse','mae'])

# Data Augmentation
training_data_generator = tf.keras.preprocessing.image.ImageDataGenerator(shear_range=0.2,
                                                                         zoom_range=0.2,
                                                                         horizontal_flip=True)
test_data_generator = tf.keras.preprocessing.image.ImageDataGenerator()

# Data Preparation
batch_size = 10

# Define the data flow
training_generator = training_data_generator.flow(x_train,y_train,batch_size=batch_size)
test_generator = test_data_generator.flow(x_test,y_test,batch_size=1,shuffle=False)

# Calculate the number of steps
training_steps = training_generator.n/batch_size

# Run the model
model.fit_generator(training_generator,
                    steps_per_epoch=training_steps,
                    epochs = 30,
                    verbose = 1
                   )

