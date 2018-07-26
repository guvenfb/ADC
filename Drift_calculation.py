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

