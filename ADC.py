import pandas as pd
from os import listdir

# folder paths and filenames
data_train_test_path = r'D:\YAS_Tasks\2017WW43.2_ADC'
csv2_files_path = r'D:\YAS_Tasks\2017WW43.2_ADC\csv2'

training_data_filename = '4M0MOP-train-features.csv'
test_data_filename = '4M0MOP-test-features.csv'

# read the csv2 filenames into a list
csv2_files_list = listdir(csv2_files_path)

# keep the following columns in the training and test data sets
keep_these_columns = ["LotId", "LayerId", "WaferId", "InspectionTime", "DeviceId", "DefectId", "Class", "FeatureRowNo"]

# append the csv2 files
appended_csv2 = []
for csv2_file in csv2_files_list:  # read each one and concat them
    df = pd.read_csv(csv2_files_path + '\\' + csv2_file)
    appended_csv2.append(df)
appended_csv2 = pd.concat(appended_csv2, axis=0)

# set index for easy merge
appended_csv2.set_index(['LotId','WaferId','InspectionTime','DefectId'], drop=True, inplace=True)
appended_csv2.drop(axis=1, labels=["LayerId", "DeviceId", "Class"], inplace=True)
appended_csv2["check_flag"] = 1  # add this column to get rid of NaN later

# read the test data set
df = pd.read_csv(data_train_test_path + '\\' + test_data_filename)
df = df[keep_these_columns]
df.set_index(['LotId','WaferId','InspectionTime','DefectId'], drop=True, inplace=True)  # set the exact index

# join by index by default, should be fast
dd = df.join(appended_csv2, how='inner')
dd.dropna(subset=['check_flag'], inplace=True) #  <-- get rid of all rows that are missing check_flag, which means csv2 did not have data for that row

# remove check_flag column
dd.drop(axis=1, labels="check_flag", inplace=True)

# write the files out
appended_csv2.to_csv(data_train_test_path + "\\concat_csv2.csv")
dd.to_csv(data_train_test_path + "\\updated_set.csv")


# add timestamp to the defects to see "drift" by reviewtime
import pandas as pd
from os import listdir
import glob
import os

shift_file_1 = r'F:\SRCData\raw_images\4M2FC_M1_P3T_BPQ_SOS_MR\D7477LLA\w617\D7477LLA_4M2FC_M1_P3T_BPQ_SOS_MR_617_20171220T100346_shifts_20171221T082528.csv'
df = pd.read_csv(shift_file_1)

image_file_folder = r'F:\SRCData\raw_images\4M2FC_M1_P3T_BPQ_SOS_MR\D7477LLA\w617\20171220T100346'
image_file_list = listdir(image_file_folder)

listing = glob.glob(image_file_folder + "\*Internal.tiff")
timestamp_dict = dict()
dict_len = len(listing)
for imfile in listing:
    defectID_start = imfile.find("\\d")
    defectID_end = imfile.find("r4_Class_Internal")
    defectID = imfile[defectID_start + 2:defectID_end]

    timestamp_dict[int(defectID)] = os.path.getmtime(imfile)

df_ts = pd.DataFrame(index=range(dict_len), columns=['defectID', 'mod_timestamp'])
df_ts = df_ts.fillna(-1)  # initialize the DataFrame
row_index = 0  # set the counter
for dID, stamp in timestamp_dict.items():
    df_ts.iloc[row_index]["defectID"] = dID
    df_ts.iloc[row_index]["mod_timestamp"] = stamp
    row_index += 1

df.set_index(['DefectId'], drop=True, inplace=True)
df_ts.set_index(['defectID'], drop=True, inplace=True)
df_w_timestamp = df.join(df_ts, how='inner')

output_file = r'F:\SRCData\raw_images\4M2FC_M1_P3T_BPQ_SOS_MR\D7477LLA\w617\D7477LLA_4M2FC_M1_P3T_BPQ_SOS_MR_617_20171220T100346_shifts_20171221T082528_w_timestamp.csv'
df_w_timestamp.to_csv(output_file)

