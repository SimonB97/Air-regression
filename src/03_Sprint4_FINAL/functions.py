import pandas as pd
import json
import orga_functions as org

#functions-------------------------------------------------------------------------------------------------------------------------------

#data preparation-----------------------------------------------------------------------------
def data_preparation_df(dframe, feature_df_path = "02_PlausFeatureList.csv"):
    dframe = df_drop_unknown_columns(dframe)
    dframe = df_correct_datetime(dframe)
    dframe = df_change_columns(dframe)
    dframe = filter_plausible_feature(dframe, feature_df_path)
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
    return dframe
                     

#missing value treatment------------------------------------------------------------------
def df_replace_missing(dframe,feature_df_path = "02_PlausFeatureList.csv"):
    
    path = org.path(feature_df_path)
    feature_df = pd.read_csv(path, sep =";", index_col='names')
    
    list_col_mean = ["co_gt","pt08_s1_co", "c6h6_gt", "pt08_s2_nmhc", "pt08_s3_nox", "no2_gt"]
    list_col_hist = ["nox_gt","pt08_s4_no2", "pt08_s5_o3", "t", "rh", "ah"]
    
    dframe.drop(columns =["nmhc_gt"], inplace =True)
    
    dframe = filter_plausible(dframe, feature_df)
    for m in list_col_mean:
        dframe[m] = column_replace_na_by_mean(dframe, feature_df, m)
    for h in list_col_hist:
        dframe[h] = column_replace_na_by_hist(dframe,feature_df, h)
        dframe[h] = column_replace_na_by_mean(dframe,feature_df, h) # if hist values are NaN
    
    return dframe
        

# methode - replacement of NaN values by mean
def column_replace_na_by_mean(dframe,feature_df, column):
    dframe[column] = dframe[column].fillna(feature_df.loc[column]["mean"])
    return dframe[column]

# methode - replacement of NaN values by historical data
def column_replace_na_by_hist(dframe,feature_df, column):
    dframe[column] = dframe[column].fillna(method= 'ffill')
    return dframe[column]



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

# Removing values from 'df_in' that do not meet min/max-definition in Featurelist from 'feature_df_path'
def filter_plausible_feature(df_in, feature_df_path = "02_PlausFeatureList.csv"):
    dframe = df_in
    df_fl = pd.read_csv(org.path(feature_df_path), sep= ';', index_col= 'names', decimal= '.')
    for ind in df_fl.index:
        if ind != 'month' and ind != 'hour':        
            min = df_fl.loc[ind].at['min']
            max = df_fl.loc[ind].at['max']
            dframe[ind] = dframe[ind][(dframe[ind] >= min) & (dframe[ind] <= max)]
    return dframe


# sklearn--------------------------------------------------------------------------------------------

# DataFrame that displays the actual future ah_values in comparison with the prediction
def check_df(x_test_in,y_test_in, clf_model_in):
    
    #transforms series into DataFrame (avoid errors)
    if isinstance(y_test_in, pd.Series):
        y_test_in = y_test_in.to_frame()
    
    set_date_index(y_test_in)
    
    #array of predicted values
    pred_y = pred_array(x_test_in, clf_model_in)
    
    #series of predicted values
    series_pred = pd.Series(pred_y)
    
    #series of actual future values
    series_future = pd.Series(y_test_in["ah_target"].values)
    
    #dataframe with datetime of the prediction
    date = pd.DataFrame(x_test_in.index.values)
    date[0] = pd.to_datetime(date[0], format = "%Y-%m-%d %H:%M:%S")
    date["future_datetime"] = date[0] + pd.DateOffset(hours=6, minutes=0)
    date.drop(columns=[0], inplace = True)
    
    #new dataframe for checking the prediction
    check_df = pd.concat([date["future_datetime"], series_future, series_pred], axis=1)
    check_df.rename(columns= {0: "future_ah", 1:"predicted_ah"}, inplace = True)
    check_df.set_index("future_datetime", inplace = True)
    return check_df


# DataFrame that displays the prediction
def prediction_df(x_test_in, clf_model_in):
    
    #array of predicted values
    pred_y = pred_array(x_test_in, clf_model_in)
    
    #series of predicted values
    series_pred = pd.Series(pred_y)
    
    #dataframe with datetime of the prediction
    date = pd.DataFrame(x_test_in.index.values)
    date[0] = pd.to_datetime(date[0], format = "%Y-%m-%d %H:%M:%S")
    date["future_datetime"] = date[0] + pd.DateOffset(hours=6, minutes=0)
    date.drop(columns=[0], inplace = True)
    
    #new dataframe
    pred_df = pd.concat([date["future_datetime"], series_pred], axis=1)
    pred_df.rename(columns= {0:"predicted_ah"}, inplace = True)
    pred_df.set_index("future_datetime", inplace = True)
    return pred_df



# array of predicted values
def pred_array(x_dframe, model_clf):
    
    set_date_index(x_dframe)
    x_data = df_to_feature_columns(model_clf, x_dframe)
    return model_clf.predict(x_data)



#only columns needed by the model, other columns dropped 
def df_to_feature_columns(model_clf, dframe):
    clf_feature_list = model_clf.feature_names_in_
    
    for x in dframe.columns:
        if not x in clf_feature_list:
            dframe.drop(columns= [x], inplace = True)
    return dframe



# set date as index (if it has not already happened)
def set_date_index(dframe):
    if set(dframe).issuperset(["date"]):
        if dframe.index.name == None:
            dframe.set_index("date", inplace = True)
    return dframe


# JSON to df------------------------------------------------------------------------------------------------

# df with results of the prediction
def pred_json_df(json_path, model_clf):
    x_dframe = json_to_ml_features_df(json_path, model_clf)
    return prediction_df(x_dframe, model_clf)


# df ready for the ML-model----------------------------------------------
def json_to_ml_features_df(json_path, model_clf,feature_df_path = "02_PlausFeatureList.csv", smart = True):
    df = json_to_correct_missing_df(json_path, feature_df_path)
    df.set_index("date", inplace = True)
    df = df_to_feature_columns(model_clf, df)
    return df


# prepared_df with replaced missing values
def json_to_correct_missing_df(json_path,feature_df_path = "02_PlausFeatureList.csv" , smart = True):
    df = json_to_prepared_df(json_path, smart)
    df = df_replace_missing(df, feature_df_path)
    return df

# df with correct datetime and other datapes; column name with small letters and droped unknown columns
def json_to_prepared_df(json_path, smart = True):
    df = json_to_df(json_path, smart)
    df = df_correct_datetime(df)
    df = df_correct_dtypes(df)
    df = df_change_columns(df)
    df = df_drop_unknown_columns(df)
    return df

#json is save like the original dateset (capital letters etc.)
def json_to_df(json_path, smart = True):
    df = pd.DataFrame (columns = og_column_list())
    f = open(org.path(json_path, smart))
    data = json.load(f)
    f.close()
    df = df.append(data)
      
    return df


#functions & static_values/lists for creating JSON Files.------------------------------------------------------------------------------------

# correct datatypes
def df_correct_dtypes(dframe):
    for c in dframe.columns: 
        if c in og_int_column_list(): 
            dframe[c] = dframe[c].fillna(na_value()).astype('int32')
        elif c in og_float_column_list():
            dframe[c] = dframe[c].fillna(na_value()).astype('float64')
    return dframe


#placeholder for na_values
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



