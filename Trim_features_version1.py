import pandas as pd
import numpy as np

# the features we would like to keep per structure
featureIds_to_be_kept = dict()
featureIds_to_be_kept['Mesa'] = [1, 2, 3, 11, 4]  # <-- manually assign some feature list
featureIds_to_be_kept['Mesa_Class'] = [1, 2, 3, 4, 7]
featureIds_to_be_kept['MxG'] = [9,11]

reduced_feature_filename = r'D:\YAS_Tasks\2017WW44.3_features\reduced_feature_DataFrame.csv'
reduced_unique_feature_by_structure_filename = r'D:\YAS_Tasks\2017WW44.3_features\reduced_feature_by_structure_DataFrame.csv'
reduced_metrics_filename = r'D:\YAS_Tasks\2017WW44.3_features\reduced_metrics_DataFrame.csv'
reduced_metrics_canonical_filename = r'D:\YAS_Tasks\2017WW44.3_features\reduced_metrics_canonical_DataFrame.csv'

total_number_of_features_to_keep = 0
for structure in featureIds_to_be_kept:  # for each structure, we will build our final table
    total_number_of_features_to_keep += len(featureIds_to_be_kept[structure])
print("total number of features we will keep at the end: {0}".format(total_number_of_features_to_keep))

# read the metric file; all information is here
feature_file = r'D:\YAS_Tasks\2017WW44.3_features\4VXRFC_feat_info.csv'
df = pd.read_csv(feature_file)
df["metrics used"] = df["metrics used"].fillna("none")  # <-- some features have no "metrics used" entry, e.g. FOV


# the feature class definition
class feature:
    def __init__(self, strctr, feat_id, met_req, imprf_curr, feat_name_curr):
        self.structure = strctr
        self.featureid = feat_id
        self.metrics_required = met_req
        self.imprfid_current = imprf_curr
        self.feature_name_current = feat_name_curr

def replace_underscore(input_word):
    str_index = input_word.find(")_")
    if str_index == -1:
        pass # print("found nothing")
    else:
        underscore_val = input_word[str_index+1:]
        # print(underscore_val, str_index)
        input_word = input_word.replace(")" + underscore_val, ")")
    return input_word


# let's get all the features information into a dictionary, features belong to feature class
features_metrics_map = dict()
for _j, (strctr, featid, description, full_description, metrics_used) in enumerate(zip(df["structure"], df["feat number"], df["description"], df["full description"], df["metrics used"])):

    # print(metrics_used, type(metrics_used))
    if metrics_used == 'none': # <-- it's nan
        imprf_list = ['IMPRF999999']
        imprf_name_list = ['Dummy']
    else: # some parsing for the metrics names
        metricid_w_name = metrics_used.split(";")
        imprf_list = list()
        imprf_name_list = list()
        for imprf in metricid_w_name:
            imprfid, imprf_name = imprf.split("=")
            imprf_list.append(imprfid)
            imprf_name_list.append(imprf_name)

    # populate the features_metrics_map dictionary
    obj_feature = feature(strctr=strctr, feat_id=featid, met_req=imprf_name_list, imprf_curr=imprf_list, feat_name_curr = description)
    if (strctr, featid) in features_metrics_map:
        pass
    else:
        features_metrics_map[(strctr, featid)] = obj_feature


# getting closer to the end: work on the "features to keep" data structure --> a DataFrame
df_features_to_keep = pd.DataFrame(index=range(total_number_of_features_to_keep), columns=['structure', 'featureID to keep', 'metrics needed', 'current IMPRF id', 'new IMPRF id', 'current feature name', 'new feature name'])
df_features_to_keep = df_features_to_keep.fillna("NONE")  # initialize the DataFrame

feature_structures_to_keep = featureIds_to_be_kept.keys()  # the different types of structures we have
row_index = 0  # set the counter
metric_counter = 0  # set the metric counter to 0
surviving_imprf_bag = dict()  # initialize the dictionary of remaining IMPRF
for structure in feature_structures_to_keep:  # for each structure, we will build our final table

    print(structure)
    feature_id_list = featureIds_to_be_kept[structure]  # <-- get the feature ids that we'd like to keep
    metrics_set = set()  # we will make a set of the metrics that we will need to keep for this structure

    for _i, feature in enumerate(feature_id_list):  # for each of the featureIDs, refer to the dictionary features_metrics_map

        obj_feature = features_metrics_map[(structure,feature)]  # <-- get the feature object back

        # read from the object
        featureid_to_keep = obj_feature.featureid
        metrics_needed = obj_feature.metrics_required
        current_IMPRFid = obj_feature.imprfid_current
        current_feature_name = obj_feature.feature_name_current

        # print(featureid_to_keep, metrics_needed, current_IMPRFid, current_feature_name)
        # insert into the DataFrame
        df_features_to_keep.iloc[row_index]["structure"] = structure
        df_features_to_keep.iloc[row_index]["featureID to keep"] = featureid_to_keep
        df_features_to_keep.iloc[row_index]["metrics needed"] = metrics_needed
        df_features_to_keep.iloc[row_index]["current IMPRF id"] = current_IMPRFid
        df_features_to_keep.iloc[row_index]["current feature name"] = current_feature_name

        modified_current_feature_name = current_feature_name.replace("IMPRF","@FRPMI@") # <-- to make it easy to replace later, down below
        df_features_to_keep.iloc[row_index]["new feature name"] = modified_current_feature_name

        row_index += 1  # increment the row index

        for metric_index, metric in enumerate(current_IMPRFid):
            # metrics_set.add(metric) <-- old way
            metrics_set.add(metric + "@@" + metrics_needed[metric_index])  # put the metricID and name (e.g. YSize, LayoutYSize, etc.) into the set data structure

    # now, the set of metrics go into the dictionary as another dictionary with new indices!
    surviving_imprf_bag[structure] = dict(zip(list(metrics_set), list(range(1,len(metrics_set) + 1))))
    metric_counter += len(metrics_set) # update the metric counter, which will be used for the last DataFrame

print(surviving_imprf_bag)

# now, ready to update the 2 columns of the DataFrame, they are currently missing
row_index = 0  # set the counter
for structure in feature_structures_to_keep:  # for each structure, we will build our final table

    feature_id_list = featureIds_to_be_kept[structure]  # <-- get the feature ids that we'd like to keep
    for _i, feature in enumerate(feature_id_list):  # for each of the featureIDs, refer to the dictionary features_metrics_map

        obj_feature = features_metrics_map[(structure,feature)]  # <-- get the feature object back

        current_feature_name = obj_feature.feature_name_current
        modified_current_feature_name = df_features_to_keep.iloc[row_index]["new feature name"] # <-- we will update it shortly
        current_IMPRFid = obj_feature.imprfid_current  # <-- this is a list, just loop through
        current_IMPRFnames = obj_feature.metrics_required  # <-- another list

        new_metric_name_list = list()
        for imprf_index, curr_metric in enumerate(current_IMPRFid):

            current_imprf_name = current_IMPRFnames[imprf_index] # <-- need this to construct the key for surviving_imprf_bag, as defined in line 108
            new_metric_name = "IMPRF" + str(surviving_imprf_bag[structure][curr_metric + "@@" + current_imprf_name])  # creating the new metric
            old_metric_name = "@FRPMI@" + curr_metric[5:]

            new_metric_name_list.append(new_metric_name)  # i will put this into the DataFrame shortly

            modified_current_feature_name = modified_current_feature_name.replace(old_metric_name, new_metric_name)  # replace IMPRFx with its new name
            # print(curr_metric, modified_current_feature_name)

        df_features_to_keep.iloc[row_index]["new IMPRF id"] = new_metric_name_list
        print(replace_underscore(modified_current_feature_name))
        df_features_to_keep.iloc[row_index]["new feature name"] = replace_underscore(modified_current_feature_name) # see if the feature name needs to be further updated for ")_m"

        row_index += 1  # increment the DataFrame row index


# at the end, write the df_features_to_keep dataframe
df_features_to_keep.to_csv(reduced_feature_filename)

# getting the unique features DataFrame by structure can be done on JMP, etc. hence skipping

# the metric names in order for each structure (another dataframe)
df_reduced_metrics = pd.DataFrame(index=range(metric_counter), columns=['structure', 'metric id', 'metric IMPRF', 'metric name'])
df_reduced_metrics = df_reduced_metrics.fillna("NONE")  # initialize the DataFrame

row_index = 0  # set the counter
for structure in feature_structures_to_keep:  # for each structure, we will build our final table
    structure_dict = surviving_imprf_bag[structure]
    for metric_name, metric_id in structure_dict.items():
        df_reduced_metrics.iloc[row_index]["structure"] = structure
        df_reduced_metrics.iloc[row_index]["metric id"] = metric_id

        metric_english_name = metric_name.split("@@")[1]
        df_reduced_metrics.iloc[row_index]["metric name"] = metric_english_name
        df_reduced_metrics.iloc[row_index]["metric IMPRF"] = "IMPRF" + str(metric_id)
        row_index += 1  # increment the DataFrame row index

df_reduced_metrics.to_csv(reduced_metrics_filename)

# the metric names in order for each structure, this time in the same cell (another dataframe)
df_reduced_canonical_metrics = pd.DataFrame(index=range(len(feature_structures_to_keep)), columns=['structure', 'metric list'])
df_reduced_canonical_metrics = df_reduced_canonical_metrics.fillna("NONE")  # initialize the DataFrame

row_index = 0  # set the counter
for structure in feature_structures_to_keep:  # for each structure, we will build our final table
    structure_dict = surviving_imprf_bag[structure]
    df_reduced_canonical_metrics.iloc[row_index]["structure"] = structure
    metric_list = ""
    for metric_name, metric_id in structure_dict.items():

        metric_english_name = metric_name.split("@@")[1]
        metric_list = metric_list + "," + metric_english_name
        df_reduced_canonical_metrics.iloc[row_index]["metric list"] = metric_list[1:]

    row_index+= 1

df_reduced_canonical_metrics.to_csv(reduced_metrics_canonical_filename)

# may need to do some exclusion for DUMMY metrics; e.g. feature = FOV and my script assigns a metric for it; not a big deal though