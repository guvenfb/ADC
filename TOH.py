import pandas as pd
import numpy as np
import time


# df_reduced_canonical_metrics = pd.DataFrame(index=range(len(feature_structures_to_keep)*2), columns=['structure', 'metric list'])

df_TOH = pd.DataFrame(index=range(1*1000*1000), columns=["val","ru"])
df_TOH["pixel_no"] = df_TOH.index + 1

# fill with values
val_col = pd.Series(np.random.randn(df_TOH.shape[0]))
df_TOH["ru"] = np.random.randint(1, 11, df_TOH.shape[0])
df_TOH["val"] = val_col

print(df_TOH.head(5))
test_runs = 25

# try summing up using dictionaries
start = time.time()
sum_dict = dict()
for epoch in range(1):
    for _j, (ru, val) in enumerate(zip(df_TOH["ru"], df_TOH["val"])):
        if ru in sum_dict:
            sum_dict[ru] = sum_dict[ru] + val
        else:
            sum_dict[ru] = val
end = time.time()
print("dictionary time: ", end - start)

# now try summarizing using pandas
# df_TOH_summary_by_ru = df_TOH.groupby(['ru'])
start = time.time()
for epoch in range(test_runs):
    df_TOH.groupby(['ru'])['val'].sum()
end = time.time()
print("DataFrame time: ", end - start)