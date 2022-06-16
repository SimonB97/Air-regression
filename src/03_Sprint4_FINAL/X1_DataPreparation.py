import pandas as pd
import orga_functions as org

#functions-------------------------------------------------------------------------------------------------------------------------------

#data preparation - ALL IN ONE
def data_preparation_df(dframe):
    dframe = df_drop_unknown_columns(dframe)
    dframe = df_correct_datetime(dframe)
    dframe = df_change_columns(dframe)
    return dframe


#drop unknown columns (original and prepared)
def df_drop_unknown_columns(dframe):
    for x in dframe.columns:
        if not change_column(x) in new_column_list():
            dframe.drop(columns= [x], inplace = True)
    return dframe


# correct datetime
def df_correct_datetime(dframe_in):
    dframe = dframe_in
    dframe["Date"] = dframe["Date"] + " "+ dframe["Time"]
    dframe.drop(columns= ["Time"], inplace = True)
    dframe["Date"] = pd.to_datetime(dframe["Date"], format = "%d/%m/%Y %H.%M.%S")
    return dframe


# change column names
def df_change_columns(dframe):
    if isinstance(dframe, pd.DataFrame):
        dframe.columns = [change_column(x) for x in dframe.columns]
    return dframe


# change a single column name
def change_column(name):
    name = name.replace("(", "_")
    name = name.replace(".", "_")
    name = name.replace(")", "")
    name = name.lower()
    return name




# Removing values from 'dframe' that do not meet min/max-definition in Featurelist from 'feature_df_path'
def df_filter_plausible(dframe, feature_df_path = "02_PlausFeatureList.csv", smart = True):
    df_fl = pd.read_csv(org.path(feature_df_path, smart), sep= ';', index_col= 'names', decimal= '.')
    for ind in df_fl.index:
        if ind != 'month' and ind != 'hour':        
            min = df_fl.loc[ind].at['min']
            max = df_fl.loc[ind].at['max']
            dframe[ind] = dframe[ind][(dframe[ind] >= min) & (dframe[ind] <= max)]
    return dframe





#static values/lists -----------------------------------------------------------------------------------------------------------------


def og_column_list():
    og_list = ['Date', 'Time', 'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 'C6H6(GT)',
       'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)',
       'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
    return og_list



def new_column_list():
    new_list = ['date', 'time', 'co_gt', 'pt08_s1_co', 'nmhc_gt', 'c6h6_gt',
                'pt08_s2_nmhc', 'nox_gt', 'pt08_s3_nox', 'no2_gt', 'pt08_s4_no2',
                'pt08_s5_o3', 't', 'rh', 'ah']
    return new_list

def og_int_column_list():
    int_list = ['PT08.S1(CO)', 'NMHC(GT)',
       'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)',
       'PT08.S4(NO2)', 'PT08.S5(O3)']
    return int_list


