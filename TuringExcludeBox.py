import pandas as pd
import numpy as np
from os import listdir

class Exclude:

    def __init__(self, path_to_DICER, resolution_in_nm):

        self.dicer_filespath = path_to_DICER
        self.resolution_in_nm = resolution_in_nm
        self.exclude_table = self.read_exclude_box_file_list(self.dicer_filespath)
        self.care_area_dictionary = self.get_care_area_dictionary()

    def read_exclude_box_file_list(self, csv2_files_path=None):

        # read the csv2 filenames into a list
        csv2_files_list = listdir(csv2_files_path)
        exclude_file_list = list()
        for file in csv2_files_list: # copy the filenames of interest
            if ("ARRAY" in file.upper() and "WINDOW" in file.upper()) or "METROCELLS" in file.upper() or "DIEHBORDER" in file.upper() or "DIEVBORDER" in file.upper():
                if ("ARRAY" in file.upper() and "WINDOW" in file.upper()):
                    # make sure ARRAY comes before WINDOW (per Sung's spec)
                    if file.upper().find("ARRAY") < file.upper().find("WINDOW"):
                        exclude_file_list.append(file)
                else:
                    exclude_file_list.append(file)

        # now append the csv files
        all_exclude_box_tables = []
        for exclude_box_file in exclude_file_list:  # read each one and concat them
            df = pd.read_csv(csv2_files_path + '\\' + exclude_box_file)
            all_exclude_box_tables.append(df)
        single_exclude_table_appended = pd.concat(all_exclude_box_tables, axis=0)

        # get rid of the row with NaN values (there is 1 such row for every csv file)
        single_exclude_table = single_exclude_table_appended.loc[~single_exclude_table_appended["xmin"].isnull()].copy()
        single_exclude_table.reset_index(inplace=True)  # create the index from the row index
        # assign a bounding boxID (BBID) for each row
        single_exclude_table["BBID"] = single_exclude_table.index
        # print(single_exclude_table.head(5))
        return single_exclude_table

    def write_exclude_box_file_list(self, csv_file_path=None, filename=None):
        self.exclude_table.to_csv(csv_file_path + filename)

    def get_rectangular_area_from_bounding_boxes(self, x_start=0, y_start=0, x_end=0, y_end=0):
        x_pixels = list()
        y_pixels = list()

        for x_pixel in range(int(np.floor(x_start)), int(np.ceil(x_end)) + self.resolution_in_nm, self.resolution_in_nm):
            x_pixels.append(np.floor(x_pixel / self.resolution_in_nm) + 1)

        for y_pixel in range(int(np.floor(y_start)), int(np.ceil(y_end)) + self.resolution_in_nm, self.resolution_in_nm):
            y_pixels.append(np.floor(y_pixel / self.resolution_in_nm) + 1)

        return x_pixels, y_pixels

    # finds the bounding box of a coordinate
    def find_pixelID(self, x_coord=-1, y_coord=-1):
        x_pixel = (np.floor(x_coord / self.resolution_in_nm) + 1)
        y_pixel = (np.floor(y_coord / self.resolution_in_nm) + 1)
        return (x_pixel, y_pixel)

    def get_care_area_dictionary(self):

        care_area_dict = dict()  #initialize the look-up table for TURING to use
        for _j, (xmin, ymin, xmax, ymax, BBID) in enumerate(
                zip(self.exclude_table["xmin"], self.exclude_table["ymin"], self.exclude_table["xmax"], self.exclude_table["ymax"], self.exclude_table["BBID"])):

            # first, find all the pixels in this bounding box
            [x_pixels, y_pixels] = self.get_rectangular_area_from_bounding_boxes(x_start=xmin, x_end=xmax, y_start=ymin, y_end=ymax)

            # next, assign the BBID
            for x_pixel in x_pixels:
                for y_pixel in y_pixels:

                    if (x_pixel, y_pixel) in care_area_dict:
                        care_area_dict[(x_pixel, y_pixel)].append(BBID)  # append the BBID
                    else:
                        care_area_dict[(x_pixel, y_pixel)] = [BBID]  # append the BBID
        return care_area_dict

    def search_within_bounding_box(self, x=0, y=0):
        # find the bounding boxes for this pixelID
        pixelID = self.find_pixelID(x_coord=x,y_coord=y)  # first find the pixels of the coordinates
        print("printing pixelIDs", pixelID)
        if pixelID in self.care_area_dictionary:  # the pixel pair may not be in our dictionary; that depends on what area the exclude boxes cover
            bounding_boxes = self.care_area_dictionary[pixelID]  # gets a list of BBIDs, which are the indexes of the bounding box df
            print("printing bounding boxes", bounding_boxes)
            for BBID in bounding_boxes:
                if x >= self.exclude_table.loc[BBID]["xmin"] and x <= self.exclude_table.loc[BBID]["xmax"] and y >= self.exclude_table.loc[BBID]["ymin"] and y <= self.exclude_table.loc[BBID]["ymax"]:
                    return True

        return False
