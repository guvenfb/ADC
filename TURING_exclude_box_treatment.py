import pandas as pd
import numpy as np
from os import listdir
import TuringExcludeBox as TEB

# folder paths and filenames
file_path = r'D:\YAS_Tasks\2018WW06.5 TURING_exclude'
obj_exclude = TEB.Exclude(path_to_DICER=file_path, resolution_in_nm=5000)
obj_exclude.write_exclude_box_file_list(r'D:\YAS_Tasks\2018WW06.5 TURING_exclude\\', "exclude_boxes_mg.csv")

# We can also add the ambit size into the search; slight change to the class instantiation is required
print(obj_exclude.search_within_bounding_box(1116600, 1))

'''
# for each coordinate we have in our DataFrame (of TURING defects), we need to do a search using the function below. It returns a Boolean variable
belongs_to_exclude_area = list()
for _j, (x_in_nm, y_in_nm) in enumerate(zip(MY_DataFrame["x"], MY_DataFrame["y"])):
    
    if obj_exclude.search_within_bounding_box(x_in_nm, y_in_nm):  # if it's true
        belongs_to_exclude_area.append(1)
    else:
        belongs_to_exclude_area.append(0)

MY_DataFrame["in_exclude_area"] = belongs_to_exclude_area
'''

