import pandas as pd
import orga_functions as org

#functions-------------------------------------------------------------------------------------------------------------------------------


#missing value treatment
def df_replace_missing(dframe,feature_df_path = "02_AlleFeatureList.csv"):
    
    feature_df = pd.read_csv(org.path(feature_df_path), sep =";", index_col='names')
    
    list_col_mean = ["co_gt","pt08_s1_co", "c6h6_gt", "pt08_s2_nmhc", "pt08_s3_nox", "no2_gt", "nmhc_gt"]
    list_col_hist = ["nox_gt","pt08_s4_no2", "pt08_s5_o3", "t", "rh", "ah"]
    
    #dframe.drop(columns =["nmhc_gt"], inplace =True)
    
    dframe = filter_plausible(dframe, feature_df)
    
    for m in list_col_mean:
        dframe[m] = column_replace_na_by_mean(dframe, feature_df, m)
    for h in list_col_hist:
        dframe[h] = column_replace_na_by_hist(dframe, h)
        dframe[h] = column_replace_na_by_mean(dframe,feature_df, h) # if hist values are NaN
    
    return dframe
        

# methode - replacement of NaN values by mean
def column_replace_na_by_mean(dframe, feature_df, column):
    dframe[column] = dframe[column].fillna(feature_df.loc[column]["mean"])
    return dframe[column]

# methode - replacement of NaN values by historical data
def column_replace_na_by_hist(dframe, column):
    dframe[column] = dframe[column].fillna(method= 'ffill')
    return dframe[column]



# Removing values from 'df_in' that do not meet min/max-definition in Featurelist from 'feature_df_path'
def df_filter_plausible(dframe, feature_df_path = "02_AlleFeatureList.csv"):
    print(feature_df_path)
    df_fl = pd.read_csv(org.path(feature_df_path), sep= ';', index_col= 'names', decimal= '.')
    for ind in df_fl.index:
        if ind != 'month' and ind != 'hour':        
            min = df_fl.loc[ind].at['min']
            max = df_fl.loc[ind].at['max']
            dframe[ind] = dframe[ind][(dframe[ind] >= min) & (dframe[ind] <= max)]
    return dframe


# Removing values from 'df_in' that do not meet min/max-definition in Featurelist 'df_fl_in'
def filter_plausible(dframe, feature_df):
    for ind in feature_df.index:
        if ind != 'month' and ind != 'hour':        
            min = feature_df.loc[ind].at['min']
            max = feature_df.loc[ind].at['max']
            dframe[ind] = dframe[ind][(dframe[ind] >= min) & (dframe[ind] <= max)]
    return dframe




