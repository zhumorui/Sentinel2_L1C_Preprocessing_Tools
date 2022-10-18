An auto tool for sentinel2-L1C images downloading and processing(Cutting and removing unuseless dataset)

Follow the jupyter notebook for more details!

Note: imgread nad imgwrite functions in dataset_preprocess.py are implemented by @[Neooolee](https://github.com/Neooolee)

### Preprocess training dataset 
python dataset_preprocess.py --source 'dataset' --output './prepared_dataset' --list 'imgs_list.txt'

### Preprocess labels
python dataset_preprocess.py --source 'Mask' --output './prepared_dataset'  --if_label True
