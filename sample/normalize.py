import numpy as np
import os
import png
import sys

from skimage import data, img_as_float
from skimage import exposure
from skimage import io

#from sklearn.preprocessing import StandardScaler
import scipy.misc
import imageio
import re

    #32767.5 # target_mean
    #65535 max_num

# This function is huge but it gets the job done
def identify_files(path, channel = "BRIGHTFIELD", input_extension = 'tif'):
    #legacy renaming
    dir = path
    #dir = "/Users/nrindtor/bucket_tmp/flatfield/703__2018-11-07T20_55_16-Measurement_1/703__2018-11-07T20_55_16-Measurement_1-sk2-A01-f07-ch2/"
    #dir = sys.argv[1]
    #for local:
    #dir = '/Users/nrindtor/rapid_dev/insilico-labeling/703_cd45/cd45_projection/'
    #channel = "CD45"
    #path = 'local_data/703_cd45/named' #/Users/nrindtor/bucket/flatfield/703__2018-11-07T20_55_16-Measurement_1-sk2-A01-f07-ch2
    #dir = os.path.join(os.getcwd(), path)
    file_list = os.listdir(dir)     # I only keep .tiff images in my list
    file_list = [i for i in file_list if input_extension in i]
    file = np.array(file_list)
    # I select the image_channel images that show my pattern
    # I nest list comprehension, np arrays to create my final list
    image_channel_path = np.sort(file[np.array([channel in i for i in file])])
    return(image_channel_path)


def create_output_filename(path, image_channel_path, file_extension = 'png', crop_num=-4):
    #legacy renaming
    dir = path
    # I create a list of output filenames
    scale_path = []
    for i in range(len(image_channel_path)):
        #TODO in case of a projection this step should be skipped
        #num = re.search(r'(z_depth-)(\d*)', image_channel_path[i]).group(2)
        #num = int(num)-1
        #new_name = re.sub(r'depth-\d*', "depth-"+ str(num), image_channel_path[i])
        #new_name = new_name[:-4] + file_extension #trimming the file ending
        new_name = image_channel_path[i][:crop_num] + file_extension #trimming the file ending
        joined_new_name = os.path.join(dir, new_name)
        scale_path.append(joined_new_name)

    return(scale_path)


def normalize_convert(path, image_channel_path, scale_path, target_std, target_mean, max_num, min_num):
    #legacy renaming
    dir = path
    # joining
    joined_list = []
    for i in np.ndarray.tolist(image_channel_path):
        joined = os.path.join(dir, i)
        joined_list.append(joined)
    #I collapse the list into the standard input format for image collections
    collapsed_list = ':'.join(joined_list)
    #I load data
    image_coll = io.imread_collection(collapsed_list)

    #I scale and save data
    image_scaled = []
    for i in range(len(image_coll)):
        #image_scaled.append(StandardScaler().fit_transform(image_coll[i]))
        tmp = image_coll[i]
        #tmp = tmp.astype(np.uint16)
        #I rescale
        mat_ms = target_mean + (tmp - tmp.mean()) * (target_std/tmp.std())
        #I trim
        mat_ms[mat_ms > max_num] = max_num
        mat_ms[mat_ms < min_num] = min_num
        #mat_ms = mat_ms.astype(np.int16)
        mat_ms = mat_ms*65535
        mat_ms = mat_ms.astype(np.uint16)
        #I store
        imageio.imwrite(uri = scale_path[i], im = mat_ms)
        #imageio.imwrite(uri = collapsed_list, im = mat_ms)

        print("normalized files in: {0}" .format(scale_path[i]))

def normalize_convert_brightfield(path,image_channel_path, scale_path, target_std = 0.125, target_mean = 0.5 , max_num = 1 , min_num = 0):
    normalize_convert(path,image_channel_path, scale_path, target_std, target_mean, max_num, min_num)

def normalize_convert_flourescent(path,image_channel_path, scale_path, target_std = 0.125, target_mean = 0.25 , max_num = 1 , min_num = 0):
    normalize_convert(path,image_channel_path, scale_path, target_std, target_mean, max_num, min_num)

# buggy TODO nrindtor
def __clean(path, pattern = '.tiff'):
    """
    erase files that have been renamed but not normalized
    """
    for f in os.listdir(path):
        if re.search(pattern, f):
            os.remove(os.path.join(path, f))

    print("directory cleaned")
