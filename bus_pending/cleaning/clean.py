import pandas as pd
import sqlite3
import pyarrow
import numpy as np
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)



conn = sqlite3.connect('/Users/kelingsdatabase/Documents/CS122 Project/buses_static_2024-02-29.db')
query = "SELECT * FROM buses WHERE tmstmp > '20240220 23:59'"
df = pd.read_sql_query(query, conn)

conn.close()

## intitial filterings

def ghostbuses(df):
    """
    count the # of observations for each bus
    if # =1 defined as ghost bus
    and set the pdist to 0
    this is an in-place modification
    """
    df = df.copy()
    df['GroupSize'] = df.groupby('vid')['vid'].transform('count')
    df['status'] = np.where(df['GroupSize'] == 1, 'Ghost', pd.NA)
    df.loc[df['status'] == 'Ghost', 'pdist'] = 0

    return df

df = ghostbuses(df)


def determine_occurrence(subset):

    """
    count how many minutes this bus has run in this trip
    this function is designed to modify df in place!!
    """
    subset = subset.copy()
    subset['change'] = subset['des'] != subset['des'].shift()
    subset['group'] = subset['change'].cumsum()
    consecutive_counts = subset.groupby('group').size()
    counts_df = consecutive_counts.reset_index(name='consecutive_counts').set_index('group')
    final_df = pd.merge(subset, counts_df, left_on='group', right_index=True, how='left')

    return final_df


def error_dealing(subset):

    """
    1.if it's the first few minutes or last few minutes of this bus, lable as middle_cut
    else: 2.if appeared less than 10 minutes in df, lable as error
    """
    trip_sequence = list(set(subset['group'].values.tolist()))

    #then we filter out top and bottom rows
    subset['error']=np.where(subset['group'].isin(trip_sequence[1:-1:1]),'complete', 
                             'middle_cut')
    condition = subset['error'] == 'complete'
    subset.loc[condition, 'error'] = np.where(subset.loc[condition, 'consecutive_counts'] <= 10, 'error', 'complete')
    return subset


concat_subsets = []  # List to store each processed subset


def final_observation(df):
    grouped_sum = df.groupby('group_x')['pdist_x'].transform('max')
    df['total_dist'] = grouped_sum 
    last_values = df.groupby('group_x')['hdg_x'].transform('last')
    df['last_value'] = last_values

    return df


for name, subset in df.groupby(by = 'vid'):

    subset_2 = determine_occurrence(subset)
    error_dealing(subset_2)
    #subset.drop('change','group','consective_counts')
    complete_df = determine_occurrence(subset_2[subset_2['error'] == 'complete'])
    #determine_occurrence(subset)
    merged_df = pd.merge(subset_2, complete_df, on='tmstmp', how='left')
    pdist_accu = merged_df
    final_df = final_observation(merged_df)
    concat_subsets.append(final_df)
    
final_dfs = pd.concat(concat_subsets)
final_dfs.drop('vid_y,	lat_y,	lon_y,	hdg_y,	pid_y,	pdist_y,	rt_y,	des_y,	dly_y,	tatripid_y,	tablockid_y,	zone_y,	origtatripno_y,	GroupSize_y,	status_y')

final_dfs.to_csv('CONCAT_VERSION.csv')








# def update_des_recursive(df):
#     # Calculate 'change', 'group', and 'consecutive_counts'
#     subset = determine_occurrence(df)

    
#     # Update 'des' where 'consecutive_counts' is less than 15
#     mask = subset['consecutive_counts'] <= 10
#     for i in df[mask].index:
#         # Find the next different 'des' value from the row above
#         next_diff_des = df.loc[i+1:, 'des'].loc[lambda x: x != df.loc[i, 'des']].head(1).values
#         if len(next_diff_des) > 0:
#             df.at[i, 'des'] = next_diff_des[0]
    
#     # Recalculate 'change', 'group', and 'consecutive_counts' after the update
#     subset = determine_occurrence(subset)
    
#     # Check if there's any 'consecutive_counts' less than or equal to 15
#     if df['consecutive_counts'].le(15).any():
#         # Recursion if there's any count less than or equal to 15
#         return update_des_recursive(df)
#     else:
#         # Drop temporary columns if needed
#         df.drop(['change', 'group'], axis=1, inplace=True)
#         return determine_occurrence(df)





    
    



    
















# print(sorted_df.head(100))
# subset_vid = sorted_df.groupby(by = 'vid')
# for bus,subset in subset_vid:
#     print(f"Group name: {bus}")
#     print(subset)
#     break


"""
count report time of each vehicle
"""
# df['GroupSize'] = df.groupby('vid')['vid'].transform('count')
# print(df.head())
# Q1 = df['GroupSize'].quantile(0.1)
# #Q3 = df['GroupSize'].quantile(0.75)
# print(Q1)
#df['pdist'] = pd.to_numeric(df['pdist'], errors='coerce')

# lst = []
# pattern_counts = df.groupby('vid')['pid'].nunique().reset_index(name='num_patterns')
# for _,row in pattern_counts.iterrows():
#      if row['num_patterns'] != 2:
#           lst.append(row['vid'])
# #print(df[df['vid'].isin(lst)])
# print(df[df['vid'] == 8290])
#lst = []
#vehicles_2_routes = []


# rt_counts = df.groupby('vid')['rt'].nunique().reset_index(name='num_routes')
# ct = 0 
# for _,row in rt_counts.iterrows():
#      if row['num_routes'] != 1:
#           print(row)
#           ct +=1
#           lst.append(row['vid'])
#           vehicles_2_routes.append(row['vid'])
# print(df[df['vid'] == 8328])
# print(ct)
# print(df[df['vid'].isin(lst)].shape)
# df_droute = df[df['vid'] == 8328]
# sorted_df = df_droute.sort_values(by=['vid', 'tmstmp'])
# print(sorted_df.head(100))






# Display the result
#print(pattern_counts)




# aggregated = df.groupby('rt').agg(
#     smallest_pdist=('pdist', 'min'),
#     largest_pdist=('pdist', 'max')
# ).reset_index()

# # Step 2: Merge back with the original df to flag the smallest and largest pdist occurrences
# merged_df = df.merge(aggregated, on='rt')

# # Flag rows with smallest and largest pdist for each rt
# merged_df['is_smallest_pdist'] = merged_df['pdist'] == merged_df['smallest_pdist']
# merged_df['is_largest_pdist'] = merged_df['pdist'] == merged_df['largest_pdist']

# # Step 3: Count occurrences
# # Count how many times the smallest and largest pdist have shown up for each route
# count_smallest = merged_df.groupby('rt')['is_smallest_pdist'].sum().reset_index(name='count_smallest_pdist')
# count_largest = merged_df.groupby('rt')['is_largest_pdist'].sum().reset_index(name='count_largest_pdist')

# # Merge the counts back with the aggregated DataFrame
# final_result = aggregated.merge(count_smallest, on='rt').merge(count_largest, on='rt')

# # Display the final DataFrame
# pd.set_option('display.max_rows', None)  # Optional: to display all rows
# print(final_result)

# print(df['rt'].unique())
# print(df[df['rt'] == '3']['pdist'])


# result = df.groupby('rt').agg(
#     smallest_pdist=('pdist', 'min'),
#     largest_pdist=('pdist', 'max'),
    
# ).reset_index()
# pd.set_option('display.max_rows', None)
# print(result)

# for _,row in df.iterrows():
#     if row['pdist'] == 1:
#         print(row)

#print(df.shape)
#for index, row in df.iterrows():
    # Access column values using row['ColumnName']
    #if type(row['pdist']) != int:
        #print(row['pdist'])

# df_103 = df[df['rt'] == '103']
# sorted_df = df_103.sort_values(by=['vid', 'tmstmp'])
# print(sorted_df)