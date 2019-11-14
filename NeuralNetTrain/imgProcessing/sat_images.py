import numpy as np
import pyrsgis
from skimage.transform import resize

# Function to transform a weirdly formed region into a rectangle shaped image
def prepocess_image(image):
  len_list = []
  for i in range(image.shape[0]):
    len_list.append(len(image[i][~np.isnan(image[i])]))

  for i in range(1,101):
    if image.shape[0] % i == 0:
      x_step = i
    if image.shape[1] % i == 0:
      y_step = i

  len_mean = np.mean(len_list)
  processed_image = []
  h_temp = None

  for x in range(0,image.shape[0],x_step):
    for y in range(0,image.shape[1],y_step):
      if np.any(np.isnan(image[x:x+x_step,y:y+y_step])) == False:
        if h_temp is None:
          h_temp = image[x:x+x_step,y:y+y_step]
        elif h_temp.shape[1] >= len_mean:
          processed_image.append(h_temp)
          h_temp = None
        else:
          h_temp = np.hstack((h_temp,image[x:x+x_step,y:y+y_step]))
  
  final_features = np.array(processed_image,dtype=np.uint8)
  new_shape = final_features.shape[0]*final_features.shape[1]
  final_features = final_features.reshape((new_shape,final_features.shape[2]))
  
  return final_features

  # Function to create input data for CNN
def create_data(files,path,y_dat,resolution = 256):
  x = []
  y = []
  label = []
  i = 0
  for f in files:
    if i % 10 == 0:
      print("Image processed: ",str(i)," of ",str(len(files)))
    ds, temp = pyrsgis.raster.read(str(path+f))
    temp = prepocess_image(temp)
    temp_resized = resize(temp, (resolution, resolution))
    x.append(temp_resized)
    split1 = f.rsplit('_',1)[0]
    split2 = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
    y.append(y_dat.loc[(y_dat['region']==split1) & (y_dat['year']==split2),'value'])
    label.append(f)
    i += 1
  return x, y, label

# Function to use if processed images are loaded and corresponding y and label have to be produced
def create_y_label(files,path,y_dat):
  y = []
  label = []
  for f in files:
    split1 = f.rsplit('_',1)[0]
    split2 = int(f.rsplit('_',1)[1].rsplit('.',1)[0])
    y.append(y_dat.loc[(y_dat['region']==split1) & (y_dat['year']==split2),'value'])
    label.append(f)
  return y, label