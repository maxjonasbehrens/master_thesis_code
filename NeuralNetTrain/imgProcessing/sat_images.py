# Script to automatically process the data and do the data splitting

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
### NOT USED IN THESIS ###
# Test Time Series Prediction
def create_time_data(path, y_dat,replace_nan,test_size = 0.2):

    general_ban = ["SE","FI","NO","BE"]
    files = [f for f in listdir(path) if isfile(join(path, f)) and f[:2] not in general_ban]

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

    msk_val = np.random.rand(len(train_split)) < 0.25

    val_split = train_split[msk_val]
    train_split = train_split[~msk_val]

    i = 0

    for region in regions:

        if i % 10 == 0:
            print("Region processed: ",str(i)," of ",str(len(regions)))

        try:
            ds, img14 = pyrsgis.raster.read(str(path)+str(region+'_2014.tif'))
            img14 = np.swapaxes(img14,0,-1)
            img14 = np.swapaxes(img14,0,-2)
            img14[np.isnan(img14)] = round(np.nanmean(img14),3)

            ds, img15 = pyrsgis.raster.read(str(path)+str(region+'_2015.tif'))
            img15 = np.swapaxes(img15,0,-1)
            img15 = np.swapaxes(img15,0,-2)
            img15[np.isnan(img15)] = round(np.nanmean(img15),3)

            ds, img16 = pyrsgis.raster.read(str(path)+str(region+'_2016.tif'))
            img16 = np.swapaxes(img16,0,-1)
            img16 = np.swapaxes(img16,0,-2)
            img16[np.isnan(img16)] = round(np.nanmean(img16),3)

            ds, img17 = pyrsgis.raster.read(str(path)+str(region+'_2017.tif'))
            img17 = np.swapaxes(img17,0,-1)
            img17 = np.swapaxes(img17,0,-2)
            img17[np.isnan(img17)] = round(np.nanmean(img17),3)

            img1415 = img15-img14
            img1516 = img16-img15
            img1617 = img17-img16

            if region in train_split:
                filepath = 'training/viirs_time/'+str(region)+'_1415.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1415)

                filepath = 'training/viirs_time/'+str(region)+'_1516.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1516)

                filepath = 'training/viirs_time/'+str(region)+'_1617.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1617)
            
            if region in val_split:
                filepath = 'validation/viirs_time/'+str(region)+'_1415.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1415)

                filepath = 'validation/viirs_time/'+str(region)+'_1516.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1516)

                filepath = 'validation/viirs_time/'+str(region)+'_1617.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1617)
            
            if region in test_split:
                filepath = 'test/viirs_time/'+str(region)+'_1415.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1415)

                filepath = 'test/viirs_time/'+str(region)+'_1516.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1516)

                filepath = 'test/viirs_time/'+str(region)+'_1617.png'
                imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img1617)
        except:
            pass

        i += 1


#%%
# Function to automatically get the image data, preprocess it, split it and save it to the right folder in google drive
def create_save_data(path,y_dat,prediction,kind = 'normal',alt_path = None,replace_nan = 'mean', resolution = 256, night = True, test_size = 0.2):
    ''' Function to do image processing, splitting and saving
        - path: path where to find the image data
        - y_dat: DF with GDP values, region labels and countries
        - prediction: which GDP metric to predict
        - kind: which kind of image (experimented with different image types)
        - alt_path: used for experimenting with mergind day and night images
        - replace_nan: how to replace the remaining space of image
        - resolution: image resolution in which the image will be saved
        - night: Night images?
        - test_size: relative size of test data share
    '''

    # Banned countries
    general_ban = ["SE","FI","NO","BE"]
    country_ban = ["CY","EE","LU","LV","ME","MK","MT","HR","LT","SI"]

    # Get image files
    if "country" in replace_nan:
        files = [f for f in listdir(path) if isfile(join(path, f)) and f[:2] not in general_ban and f[:2] not in country_ban]
    else:
        files = [f for f in listdir(path) if isfile(join(path, f)) and f[:2] not in general_ban]

    np.random.seed(42)

    # Create list of unique regions
    regions = []
    for i in range(len(files)):
        regions.append(files[i].rsplit('_',1)[0])

    regions = np.unique(regions)

    # Split regions into train, validation and test data
    msk_test = np.random.rand(len(regions)) < test_size

    train_split = regions[~msk_test]
    test_split = regions[msk_test]

    msk_val = np.random.rand(len(train_split)) < 0.25 # Account for previous split which decreased the remaining count

    val_split = train_split[msk_val]
    train_split = train_split[~msk_val]

    print('Random data splitting finished.')

    i = 0
    
    # Iterate through all images
    for f in files:

        # Print progress
        if i % 10 == 0:
            print("Image processed: ",str(i)," of ",str(len(files)))
        
        i += 1

        # Get region, year and GDP value
        region = f.rsplit('_',1)[0]
        year = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
        y = y_dat.loc[(y_dat['nuts2']==region) & (y_dat['year']==year),prediction].values[0]

        # Convert image file to numpy array
        ds, img = pyrsgis.raster.read(str(path)+str(f))
        
        # Swap axes to get right format
        img = np.swapaxes(img,0,-1)
        img = np.swapaxes(img,0,-2)

        # Get light average from array
        mean = np.nanmean(img)

        # Resize the image
        img = resize(img, (resolution, resolution))

        # NOT USED - encode country GDP into image
        country = y_dat.loc[(y_dat['nuts2']==region) & (y_dat['year']==year),'country_value'].values[0] / y_dat['country_value'].max() * np.nanmax(img)

        # Other experimenting (merge day and night images)
        if kind != 'merge' and night:
            img = np.stack((img,)*3, axis = -1)

        # Do further processing and saving for training data
        if region in train_split:
            if math.isnan(y):
                pass
            else:
                # NOT USED - take only subsample of original image
                if kind == 'subsample':
                    process_subsample_image(img,'training',region,year,y,resolution=resolution)
                # NOT USED - merge day and night image
                elif kind == 'merge':
                    try:
                        ds, img_day = pyrsgis.raster.read(str(alt_path)+str(f))
                        
                        img_day = np.swapaxes(img_day,0,-1)
                        img_day = np.swapaxes(img_day,0,-2)

                        img = np.array([img])
                        img = np.swapaxes(img,0,-1)
                        img = np.swapaxes(img,0,-2)

                        img = resize(img, (resolution, resolution))
                        img_day = resize(img_day, (resolution, resolution))

                        process_merged_image(img_day,img,'training',region,year,y,country,replace_nan=replace_nan)
                    except:
                        print('Cannot find file.')
                # Process and save images
                else:
                    if night:
                        process_normal_image(img,'training',region,year,y,country,mean,replace_nan,'night')    
                    else:
                        process_normal_image(img,'training',region,year,y,country,mean,replace_nan,'day')

        # Do further processing and saving for validation data
        elif region in val_split:
            if math.isnan(y):
                pass
            else:
                # NOT USED - take only subsample of original image
                if kind == 'subsample':
                    process_subsample_image(img,'validation',region,year,y,resolution=resolution)
                # NOT USED - merge day and night image
                elif kind == 'merge':
                    try:
                        ds, img_day = pyrsgis.raster.read(str(alt_path)+str(f))
                        
                        img_day = np.swapaxes(img_day,0,-1)
                        img_day = np.swapaxes(img_day,0,-2)

                        img = np.array([img])
                        img = np.swapaxes(img,0,-1)
                        img = np.swapaxes(img,0,-2)

                        img = resize(img, (resolution, resolution))
                        img_day = resize(img_day, (resolution, resolution))

                        process_merged_image(img_day,img,'validation',region,year,y,country,replace_nan=replace_nan)
                    except:
                        print('Cannot find file.')
                # Process and save images
                else:
                    if night:
                        process_normal_image(img,'validation',region,year,y,country,mean,replace_nan,'night')    
                    else:
                        process_normal_image(img,'validation',region,year,y,country,mean,replace_nan,'day')

        # Do further processing and saving for test data
        else:
            if math.isnan(y):
                pass
            else:
                # NOT USED - take only subsample of original image
                if kind == 'subsample':
                    process_subsample_image(img,'test',region,year,y,resolution=resolution)
                # NOT USED - merge day and night image
                elif kind == 'merge':
                    try:
                        ds, img_day = pyrsgis.raster.read(str(alt_path)+str(f))
                        
                        img_day = np.swapaxes(img_day,0,-1)
                        img_day = np.swapaxes(img_day,0,-2)

                        img = np.array([img])
                        img = np.swapaxes(img,0,-1)
                        img = np.swapaxes(img,0,-2)

                        img = resize(img, (resolution, resolution))
                        img_day = resize(img_day, (resolution, resolution))

                        process_merged_image(img_day,img,'test',region,year,y,country,replace_nan=replace_nan)
                    except:
                        print('Cannot find file.')
                # Process and save images
                else:
                    if night:
                        process_normal_image(img,'test',region,year,y,country,mean,replace_nan,'night')    
                    else:
                        process_normal_image(img,'test',region,year,y,country,mean,replace_nan,'day')

#%%                
# Process raw image to normal day/night image
def process_normal_image(img_array, region_type, region, year, y, country, mean, replace_nan = 'mean', time = 'day'):

    # Replace remaining space depending on the parameter - thesis only uses mean
    if replace_nan == "mean":
        img_array[np.isnan(img_array)] = mean
    elif replace_nan == "normal":
        mu, sigma = np.nanmean(img_array), np.nanstd(img_array)
        n_nan = len(img_array[np.isnan(img_array)])
        img_array[np.isnan(img_array)] = np.random.normal(mu,sigma,n_nan)
    elif replace_nan == 'country':
        img_array[np.isnan(img_array)] = country
    elif replace_nan == 'country_tot':
        img_array[np.isnan(img_array)] = 0.0
        img_array = img_array / country
    else:
        img_array[np.isnan(img_array)] = 0.0

    # For regions after 2013 the processed image will be saved to the correct google drive folder
    if year > 2013:
        if replace_nan == 'country' or replace_nan == 'country_tot':
            filepath = str(region_type)+'/viirs_'+str(time)+'_'+replace_nan+'/'+str(region)+'_'+str(mean)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img_array)
        else:
            filepath = str(region_type)+'/viirs_'+str(time)+'/'+str(region)+'_'+str(mean)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img_array)
    else:
        if replace_nan == 'country' or replace_nan == 'country_tot':
            filepath = str(region_type)+'/'+str(time)+'_'+replace_nan+'/'+str(region)+'_'+str(mean)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img_array)
        else:
            filepath = str(region_type)+'/'+str(time)+'/'+str(region)+'_'+str(mean)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img_array)


# Process merged image to combine day and night - NOT USED IN THESIS
def process_merged_image(img_day,img_night, region_type, region, year, y, country, replace_nan = "mean"):

    img_night[np.isnan(img_night)] = 0.0

    if replace_nan == "mean":
        img_day[np.isnan(img_day)] = round(np.nanmean(img_day),3)
    elif replace_nan == "normal":
        mu, sigma = np.nanmean(img_day), np.nanstd(img_day)
        n_nan = len(img_day[np.isnan(img_day)])
        img_day[np.isnan(img_day)] = np.random.normal(mu,sigma,n_nan)
    elif replace_nan == 'country':
        img_day[np.isnan(img_day)] = country
    elif replace_nan == 'country_tot':
        img_day[np.isnan(img_day)] = 0.0
        img_day = img_day / country
    else:
        img_day[np.isnan(img_day)] = 0.0

    img = np.append(img_day,img_night,axis = 2)

    img[:,:,:2] = img[:,:,:2]/np.max(img[:,:,:2])
    img[:,:,3] = img[:,:,3]/np.max(img[:,:,3])

    if year > 2013:
        if replace_nan == 'country' or replace_nan == 'country_tot':
            filepath = str(region_type)+'/viirs_merge_'+replace_nan+'/'+str(region)+'_'+str(y)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img)
        else:    
            filepath = str(region_type)+'/merge/'+str(region)+'_'+str(y)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img)
    else:
        if replace_nan == 'country' or replace_nan == 'country_tot':
            filepath = str(region_type)+'/viirs_merge_'+replace_nan+'/'+str(region)+'_'+str(y)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img)
        else:    
            filepath = str(region_type)+'/merge/'+str(region)+'_'+str(y)+'_'+str(year)+'.png'
            imageio.imwrite('/gdrive/My Drive/ThesisData/'+filepath, img)


# Process subsample from raw image - NOT USED IN THESIS
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


### THE OTHER THREE REMAINING FUNCTIONS ARE FOR MANUALLY PROCESSING ONLY

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