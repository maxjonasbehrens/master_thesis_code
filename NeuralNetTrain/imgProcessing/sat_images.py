#%%
import numpy as np
import pyrsgis
from skimage.transform import resize
from matplotlib import pyplot as plt
import pandas as pd

#%%
# Function to create input data for CNN
def create_data(files,path,y_dat, prediction,replace_nan = "mean",resolution = 256,night=True):
    x = []
    y = []
    label = []
    i = 0
    for f in files:
        if i % 10 == 0:
            print("Image processed: ",str(i)," of ",str(len(files)))
        ds, temp = pyrsgis.raster.read(str(path+f))
        if night == False:
            temp = np.moveaxis(temp,0,-1)

        if replace_nan == "mean":
            temp[np.isnan(temp)] = round(np.nanmean(temp),3)
        elif replace_nan == "normal":
            mu, sigma = np.nanmean(temp), np.nanstd(temp)
            n_nan = len(temp[np.isnan(temp)])
            temp[np.isnan(temp)] = np.random.normal(mu,sigma,n_nan)
        else:
            temp[np.isnan(temp)] = 0.0
        
        temp_resized = resize(temp, (resolution, resolution))
        
        x.append(temp_resized)
        split1 = f.rsplit('_',1)[0]
        split2 = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
        y.append(y_dat.loc[(y_dat['nuts2']==split1) & (y_dat['year']==split2),prediction])
        label.append(f)
        i += 1
    return x, y, label

# Function to use if processed images are loaded and corresponding y and label have to be produced
def create_y_label(files,path,y_dat,prediction):
    y = []
    label = []
    for f in files:
        split1 = f.rsplit('_',1)[0]
        split2 = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
        y.append(y_dat.loc[(y_dat['nuts2']==split1) & (y_dat['year']==split2),prediction])
        label.append(f)
    return y, label

#%%
# Create sampled image data based on raw data
def create_sample_data(files,path,y_dat,prediction='nuts_value',resolution=256):
    x_ = []
    y_ = []
    label = []
    i = 0
    for f in files:
        if i % 10 == 0:
            print("Image processed: ",str(i)," of ",str(len(files)))
        ds, temp = pyrsgis.raster.read(str(path+f))
        temp = np.moveaxis(temp,0,-1)
        
        del ds

        for k in range(26):
            x = round(np.random.uniform(high = temp.shape[0]))
            y = round(np.random.uniform(high = temp.shape[1]))
            sample = temp[x:x+resolution,y:y+resolution,:]
            while np.isnan(sample).any():
                x = round(np.random.uniform(high = temp.shape[0]))
                y = round(np.random.uniform(high = temp.shape[1]))
                sample = temp[x:x+resolution,y:y+resolution,:]
                # Maybe replace already taken values with nan to prevent overlapping
            
            x_.append(sample)
            split1 = f.rsplit('_',1)[0]
            split2 = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
            y_.append(y_dat.loc[(y_dat['nuts2']==split1) & (y_dat['year']==split2),prediction])
            label.append(f)
        
        del temp
        i += 1
    return x_, y_, label