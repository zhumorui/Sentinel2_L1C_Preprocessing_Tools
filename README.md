An auto tool for sentinel2-L1C images downloading and processing(Cutting and removing unuseless dataset)

Follow the jupyter notebook for more details!

Note: imgread nad imgwrite functions in dataset_preprocess.py are implemented by @[Neooolee](https://github.com/Neooolee)


## Step

### Prepare your dataset dictionary like the following structure:  
    -- dataset
        -- S2A_MSIL1C_20190714T043711_N0208_R033_T46TFN_20190714T073938.SAFE   
        -- S2A_MSIL1C_20180930T030541_N0206_R075_T49QDD_20180930T060706.SAFE  

### Create the imgs_list.txt to split the train and test likt the following structure:  
"""  
train  
S2A_MSIL1C_20190714T043711_N0208_R033_T46TFN_20190714T073938  

test  
S2A_MSIL1C_20180930T030541_N0206_R075_T49QDD_20180930T060706  
  
"""

### Preprocess training dataset 
python dataset_preprocess.py --source 'dataset' --output './prepared_dataset' --list 'imgs_list.txt'

### Preprocess labels 
python dataset_preprocess.py --source 'Mask' --output './prepared_dataset'  --if_label True
