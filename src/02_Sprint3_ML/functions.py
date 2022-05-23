import pandas as pd
import json
import orga_functions as org

#static_values/lists etc. --------------------------------------------------------------------------------------------------------

#replacement for na_values
def na_value():
    return -1024000


def og_column_list():
    og_list = ['Date', 'Time', 'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 'C6H6(GT)',
       'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)',
       'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
    return og_list

def og_int_column_list():
    int_list = ['PT08.S1(CO)', 'NMHC(GT)',
       'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)',
       'PT08.S4(NO2)', 'PT08.S5(O3)']
    return int_list

def og_float_column_list():
    float_list = ['CO(GT)', 'C6H6(GT)',
             'T', 'RH', 'AH']
    return float_list


def new_column_list():
    new_list = ['date', 'time', 'co_gt', 'pt08_s1_co', 'nmhc_gt', 'c6h6_gt',
                'pt08_s2_nmhc', 'nox_gt', 'pt08_s3_nox', 'no2_gt', 'pt08_s4_no2',
                'pt08_s5_o3', 't', 'rh', 'ah']
    return new_list

#functions----------------------------------------------------------------------------------------------------------------------

# correct datetime
def df_correct_datetime(dframe_in):
    dframe = dframe_in
    dframe["Date"] = dframe["Date"] + " "+ dframe["Time"]
    dframe.drop(columns= ["Time"], inplace = True)
    dframe["Date"] = pd.to_datetime(dframe["Date"], format = "%d/%m/%Y %H.%M.%S")
    return dframe


# correct datatypes
def df_correct_dtypes(dframe):
    for c in dframe.columns: 
        if c in og_int_column_list(): 
            dframe[c] = dframe[c].fillna(na_value()).astype('int32')
        elif c in og_float_column_list():
            dframe[c] = dframe[c].fillna(na_value()).astype('float64')
    return dframe


# change column names
def df_change_columns(dframe):
    if isinstance(dframe, pd.DataFrame):
        dframe.columns = [change_column(x) for x in dframe.columns]
    return dframe

def change_column(name):
    name = name.replace("(", "_")
    name = name.replace(".", "_")
    name = name.replace(")", "")
    name = name.lower()
    return name

#concat multiple dataframes
def dfs_concat(*dfs):
    df = pd.concat(dfs)
    df.reset_index(drop = True, inplace = True)
    return df

#drop unknown columns (original and prepared)
def df_drop_unknown_columns(dframe):
    for x in dframe.columns:
        if not change_column(x) in new_column_list():
            dframe.drop(columns= [x], inplace = True)
            
# Removing values from 'df_in' that do not meet min/max-definition in Featurelist 'df_fl_in'
def filter_plausible(df_in, df_fl_in):
    dframe = df_in
    df_fl = df_fl_in
    for ind in df_fl.index:
        if ind != 'month' and ind != 'hour':        
            min = df_fl.loc[ind].at['min']
            max = df_fl.loc[ind].at['max']
            dframe[ind] = dframe[ind][(dframe[ind] >= min) & (dframe[ind] <= max)]
    return dframe

# JSON to df-------------------------------------------
def json_to_prepared_df(json_path, smart = True):
    df = json_to_df(json_path, smart)
    df = df_correct_datetime(df)
    df = df_correct_dtypes(df)
    df = df_change_columns(df)
    return df

def json_to_df(json_path, smart = True):
    df = pd.DataFrame (columns = og_column_list())
    f = open(org.path(json_path, smart))
    data = json.load(f)
    f.close()
    df = df.append(data)
      
    return df


