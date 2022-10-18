from cgi import test
import os
import numpy as np
from glob import glob
from gdaldiy import imgread, imgwrite
import argparse


parser = argparse.ArgumentParser(description='sentinel2 L1C dataset preprocess')
parser.add_argument('--source', type=str, required=True, help='original sentinel2 L1C dataset or labels path')
parser.add_argument('--output', type=str, required=True, help='image clips output path')
parser.add_argument('--list', type=str, required=False, help='images list for deviding training and test' )
parser.add_argument('--if_label', type=bool, required=False, default=False, help='if cutting labels')
parser.add_argument('--organise_labels', type=bool, required=False, default=False, help='if you want to filter and organise the labels to only keep those with corresponding patches')
args = parser.parse_args()


def get_list(img_list):
    # Get train and test dataset list
    with open(img_list,'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip('\n') == "train":
                train_list = []
                train_read_mode = True
            elif line.strip('\n') == "test":
                test_list = []
                train_read_mode = False

            elif len(line.strip('\n')) > 0 :
                if train_read_mode == True:
                    train_list.append(line.strip('\n'))
                elif train_read_mode == False:
                    test_list.append(line.strip('\n'))
                else:
                    print("Error, Check dataset list\n")
    return train_list, test_list

def cut_image(all_bands_path,save_clips_path,train_list,test_list):

    print("Start Cutting images\n")

    for i in range(len(all_bands_path)//13):
        img_name = all_bands_path[i*13].split('.SAFE')[0].split('/')[-1]
        print("Processing {}/{} image: {}".format(i+1,len(all_bands_path) // 13,str(img_name),))

        # Prepare image dictionary for cutting
        band_name_10m = ['B02', 'B03', 'B04', 'B08']
        band_name_20m = ['B05', 'B06', 'B07', 'B8A', 'B11', 'B12']
        band_name_60m = ['B01', 'B09', 'B10']

        # Create an empty dict to storage different bands in an image
        bands_dict={}
        band_10m = []
        band_20m = []
        band_60m = []

        for band_path in all_bands_path[i*13 : 13*(i+1)]:
            band = imgread(band_path)
            band_name = band_path.split('/')[-1].split('.jp2')[0][-3:]

            if band_name in band_name_10m:
                band_10m.append(band)
            elif band_name in band_name_20m:
                band_20m.append(band)
            elif band_name in band_name_60m:
                band_60m.append(band)
            else:
                print("Unkown band!! Band:{} is invalid!\n".format(str(band_name)))
        
        bands_dict['band_10m'] = band_10m
        bands_dict['band_20m'] = band_20m
        bands_dict['band_60m'] = band_60m
    # -------------------------------------- #

        key = img_name

        """
        window_size=384 #384 for 10 m bands, 192 for 20 m bands, 64 for 60 m bands.
        stride=384 #384 for 10 m bands, 192 for 20 m bands, 64 for 60 m bands.
        """

        for i in bands_dict.keys():
            if i == 'band_10m':
                window_size = 384 # for 10 m bands
                stride = 384 # for 10 m bands
                img = np.stack(bands_dict['band_10m'],axis=2) 
                band_dir_name = '10m'

            elif i == 'band_20m':
                window_size = 192 # for 20 m bands
                stride = 192 # for 20 m bands
                img = np.stack(bands_dict['band_20m'],axis=2) 
                band_dir_name = '20m'

            elif i == 'band_60m':
                window_size = 64 # for 60 m bands
                stride = 64 # for 60 m bands
                img = np.stack(bands_dict['band_60m'],axis=2) 
                band_dir_name = '60m'
            else:
                print("unknow bands! Please check dataset!\n")
                break

            h,w=img.shape[0],img.shape[1]
            assert (h in [10980,5490,1830]) and (w in [10980,5490,1830])\
            , "invalid image size detect! height:{},width:{}".format(h,w)

            h_steps=(w-window_size)//stride+1
            w_steps=(h-window_size)//stride+1
            n=0
            for i in range(h_steps):
                high=i*stride
                for j in range(w_steps):
                    width=j*stride
                    n=n+1
                    if np.all(img[high:high+window_size,width:width+window_size]>0):
                        if key in train_list:
                            imgwrite(os.path.join(save_clips_path,'train',band_dir_name)+"/"+key+'_'+str(n)+'.tif',img[high:high+window_size,width:width+window_size])
                        elif key in test_list:
                            imgwrite(os.path.join(save_clips_path,'test',band_dir_name)+"/"+key+'_'+str(n)+'.tif',img[high:high+window_size,width:width+window_size])
                        else:
                            print("Unknown dataset, Please check imgs_list.txt!\n")
                            break
    print("Cutting images process finished!\n")


# Remove incompleted bands
def remove_incompleted_bands_files(path):

    print("removce incompleted bands files in path: {}".format(path))
    for _, dirs, _ in os.walk(os.path.join(path)):
        for dir in dirs:
            for _, _, band_files in os.walk(os.path.join(path,dir)):
                if dir == "10m":
                    list_10m = band_files
                elif dir == "20m":
                    list_20m = band_files
                elif dir == "60m":
                    list_60m = band_files
                else:
                    print("invalid dir!\n")
                    break
                break
        intersection_list = list(set(list_10m).intersection(list_20m, list_60m))

        for i in list_10m:
            if not i in intersection_list:
                os.remove(os.path.join(path, '10m', i))
        for i in list_20m:
            if not i in intersection_list:
                os.remove(os.path.join(path, '20m', i))
        for i in list_60m:
            if not i in intersection_list:
                os.remove(os.path.join(path, '60m', i))           
        break

    return intersection_list

def try_make_directory(base_dir, new_dir):
    dir_path = os.path.join(base_dir, new_dir)
    if os.path.exists(dir_path):
        print("Exist output path: {}".format(dir_path))
        i = 1
        while True:
            dir_path = os.path.join(base_dir, '{}_{}'.format(new_dir, str(i)))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print("Create a new output dir: {}\n".format(dir_path))
                break
            else:
                i += 1
    else:
        os.makedirs(dir_path)

    return dir_path

def process_labels():
    input_path = args.source
    save_clips_path = os.path.join(args.output,'output')

    if args.organise_labels:       
        if not os.path.exists(os.path.join(save_clips_path, 'train', '10m')) or not os.path.exists(os.path.join(save_clips_path, 'test', '10m')):
            raise Exception(f"Missing train/test directory, make sure you have cut the image patches first, or don't specify `organise_labels`")

        train_lbls_path = try_make_directory(os.path.join(save_clips_path, 'train'), 'labels')
        test_lbls_path = try_make_directory(os.path.join(save_clips_path, 'test'), 'labels')
        train_img_names = [os.path.basename(f) for f in glob(os.path.join(save_clips_path, 'train', '10m', '*.tif'))]
        test_img_names = [os.path.basename(f) for f in glob(os.path.join(save_clips_path, 'test', '10m', '*.tif'))]
    else:
        save_clips_path = try_make_directory(args.output, 'output') 
    
    # Load labels
    labels_path = glob(os.path.join(args.source, "*.tif"))
    labels_path.sort()
    print("The number of labels is: {}\n".format(len(labels_path)))

    # Start cutting labels
    print("Start cutting labels")
    for label_path in labels_path:
        label = imgread(label_path)
        label_name = label_path.split('.tif')[0].split('/')[-1]
        h,w=label.shape[0],label.shape[1]
        assert (h in [10980]) and (w in [10980])\
        , "invalid label size detect! height:{},width:{}".format(h,w)

        window_size = 384 # for 10m resolution label image
        stride = 384 # for 10 m resolution label image 
        h_steps=(w-window_size)//stride+1
        w_steps=(h-window_size)//stride+1
        n=0
        for i in range(h_steps):
            high=i*stride
            for j in range(w_steps):
                width=j*stride
                n=n+1
                if label_name[-5:] == '_Mask':
                    label_name = label_name[:-5]

                label_name_ext = label_name+'_'+str(n)+'.tif'

                if args.organise_labels:
                    if label_name_ext in train_img_names:
                        save_clips_path = train_lbls_path
                    elif label_name_ext in test_img_names:
                        save_clips_path = test_lbls_path
                    else:
                        continue

                # TEST HERE
                imgwrite(os.path.join(save_clips_path, label_name_ext), label[high:high+window_size,width:width+window_size])
        print("Generate {} clips for labels: {}".format(n, label_name))

    if args.organise_labels:
        print("\nCutting labels finished!\nTrain output path: '{}'".format(train_lbls_path))
        print("Test output path: '{}'".format(test_lbls_path))
    else:
        print("\nCutting labels finished!\nOutput path: '{}'".format(save_clips_path))


def process_dataset():
    
    print("Loading sentinel dataset...\n")

    # Load Sentinel Data
    all_bands_path = glob(os.path.join(args.source, "S2A_MSIL1C*.SAFE/GRANULE/*/IMG_DATA/*_B?*.jp2"))
    all_bands_path.sort()
    assert (len(all_bands_path) % 13) == 0 , "every image should own 13 bands!"
    print("The number of images with 13 bands is: {}\n".format(len(all_bands_path)//13))

    # Get train and test list
    train_list, test_list = get_list(args.list)
    # print("Get train_list:\n{}\n".format(train_list))
    # print("Get test_list:\n{}\n".format(test_list))

    # Create training and test dirs
    save_clips_path = try_make_directory(args.output,'output')
    

    if not os.path.exists(os.path.join(save_clips_path,'train')):
        os.makedirs(os.path.join(save_clips_path,'train','10m'))
        os.makedirs(os.path.join(save_clips_path,'train','20m'))
        os.makedirs(os.path.join(save_clips_path,'train','60m'))

    if not os.path.exists(os.path.join(save_clips_path,'test')):
        os.makedirs(os.path.join(save_clips_path,'test','10m'))
        os.makedirs(os.path.join(save_clips_path,'test','20m'))
        os.makedirs(os.path.join(save_clips_path,'test','60m'))

    # Start cutting images
    cut_image(all_bands_path,save_clips_path,train_list, test_list)

    # Start removing non completed bands files

    train_path = os.path.join(save_clips_path, 'train')
    test_path = os.path.join(save_clips_path,'test')
    
    output_train_list = remove_incompleted_bands_files(train_path)
    output_test_list = remove_incompleted_bands_files(test_path)

    print("Generate {} image_clips for training".format(len(output_train_list)))
    print("Generate {} image_clips for testing\n".format(len(output_test_list)))
    print("Cutting images finished!\nOutput path: '{}'".format(save_clips_path))

def main(args):
    if args.if_label == True:
        print("Start Cutting labels process")
        process_labels()
    else:
        assert args.list != None, "img list is required for cutting dataset"
        print("Start Cutting datasets process")
        process_dataset()


if __name__ == '__main__':
    main(args)





    