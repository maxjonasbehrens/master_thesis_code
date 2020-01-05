#%%
import numpy as np
import pyrsgis
from skimage.transform import resize
from matplotlib import pyplot as plt
import pandas as pd
import math
import imageio
from os import listdir
from os.path import isfile, join

#%%
def create_save_data(path,y_dat,prediction,kind = 'normal',alt_path = None,replace_nan = 'mean', resolution = 256, night = True, test_size = 0.2):
    
    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    np.random.seed(42)

    # Create list of unique regions
    regions = []
    for i in range(len(files)):
        regions.append(files[i].rsplit('_',1)[0])

    regions = np.unique(regions)

    # Split regions into train and test set
    msk_test = np.random.rand(len(regions)) < test_size

    train_split = regions[~msk_test]
    test_split = regions[msk_test]

    msk_val = np.random.rand(len(train_split)) < (test_size+0.05)

    val_split = train_split[msk_val]
    train_split = train_split[~msk_val]

    print('Random data splitting finished.')

    i = 0
    
    for f in files:

        if i % 10 == 0:
            print("Image processed: ",str(i)," of ",str(len(files)))
        
        i += 1

        region = f.rsplit('_',1)[0]
        year = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
        y = y_dat.loc[(y_dat['nuts2']==region) & (y_dat['year']==year),prediction].values[0]

        ds, img = pyrsgis.raster.read(str(path)+str(f))
        img = np.swapaxes(img,0,-1)
        img = np.swapaxes(img,0,-2)

        if kind != 'merge' and night:
            img = np.stack((img,)*3, axis = -1)

        if region in train_split:
            if math.isnan(y):
                pass
            else:
                if kind == 'subsample':
                    process_subsample_image(img,'training',region,year,y,resolution=resolution)
                elif kind == 'merge':
                    ds, img_day = pyrsgis.raster.read(str(alt_path)+str(f))
                    img_day = np.swapaxes(img,0,-1)
                    img_day = np.swapaxes(img,0,-2)

                    img = np.array([img])
                    img = np.swapaxes(img,0,-1)

                    img = resize(img, (resolution, resolution))
                    img_day = resize(img_day, (resolution, resolution))

                    process_merged_image(img_day,img,'training',region,year,y)
                else:
                    if night:
                        process_normal_image(img,'training',region,year,y,'mean','night')    
                    else:
                        process_normal_image(img,'training',region,year,y,'mean','day')

        elif region in val_split:
            if math.isnan(y):
                pass
            else:
                if kind == 'subsample':
                    process_subsample_image(img,'validation',region,year,y,resolution=resolution)
                elif kind == 'merge':
                    ds, img_day = pyrsgis.raster.read(str(alt_path)+str(f))
                    img_day = np.swapaxes(img,0,-1)
                    img_day = np.swapaxes(img,0,-2)

                    img = resize(img, (resolution, resolution))
                    img_day = resize(img_day, (resolution, resolution))

                    process_merged_image(img_day,img,'validation',region,year,y)
                else:
                    if night:
                        process_normal_image(img,'validation',region,year,y,'mean','night')    
                    else:
                        process_normal_image(img,'validation',region,year,y,'mean','day')

        else:
            if math.isnan(y):
                pass
            else:
                if kind == 'subsample':
                    process_subsample_image(img,'test',region,year,y,resolution=resolution)
                elif kind == 'merge':
                    try:
                        ds, img_day = pyrsgis.raster.read(str(alt_path)+str(f))
                        
                        img_day = np.swapaxes(img,0,-1)
                        img_day = np.swapaxes(img,0,-2)

                        img = resize(img, (resolution, resolution))
                        img_day = resize(img_day, (resolution, resolution))

                        process_merged_image(img_day,img,'test',region,year,y)
                    except:
                        print('Cannot find file.')
                else:
                    if night:
                        process_normal_image(img,'test',region,year,y,'mean','night')    
                    else:
                        process_normal_image(img,'test',region,year,y,'mean','day')
                
# Process raw image to normal day/night image
def process_normal_image(img_array, region_type, region, year, y, replace_nan = 'mean', time = 'day'):
    
    if replace_nan == "mean":
            img_array[np.isnan(img_array)] = round(np.nanmean(img_array),3)
    elif replace_nan == "normal":
        mu, sigma = np.nanmean(img_array), np.nanstd(img_array)
        n_nan = len(img_array[np.isnan(img_array)])
        img_array[np.isnan(img_array)] = np.random.normal(mu,sigma,n_nan)
    else:
        img_array[np.isnan(img_array)] = 0.0

    filepath = str(region_type)+'/'+str(time)+'/'+str(region)+'_'+str(y)+'_'+str(year)+'.png'
    imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img_array)


# Process merged image to combine day and night
def process_merged_image(img_day,img_night, region_type, region, year, y):

    img = np.append(img_day,img_night,axis = 2)

    filepath = str(region_type)+'/merge/'+str(region)+'_'+str(y)+'_'+str(year)+'.png'
    imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img)


# Process subsample from raw image
def process_subsample_image(img_array, region_type, region, year, y_value, resolution = 256, sample_size = 50):
    
    try:
        for k in range((sample_size+1)):
            x = round(np.random.uniform(high = img_array.shape[0]))
            y = round(np.random.uniform(high = img_array.shape[1]))
            sample = img_array[x:x+resolution,y:y+resolution,:]
            
            while np.isnan(sample).any():
                x = round(np.random.uniform(high = img_array.shape[0]))
                y = round(np.random.uniform(high = img_array.shape[1]))
                sample = img_array[x:x+resolution,y:y+resolution,:]

            filepath = str(region_type)+'/subsample/'+str(region)+'_'+str(y_value)+'_'+str(year)+'_'+str(k)+'.png'
            
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, sample)
    except:
        print('File not exists')


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
