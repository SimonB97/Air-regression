import pandas as pd
import json
import X1_DataPreparation as data_prep
import X2_MissingValueTreatment as mvtreatment
import X3_Forecasting as forecast
import X4_ReadJSON as readj
import orga_functions as org

#functions-------------------------------------------------------------------------------------------------------------------------------


#add new DataFrame to the main data set
def add_new_df(new_dframe, df_continuous, df_continous_path):
    whole_df = readj.dfs_concat(df_continuous, new_dframe)
    
    # save 
    path = org.path(df_continous_path)
    whole_df.to_csv(path, sep=';', index = False)
    return whole_df


# JSON to df for Forecasting -------------------------------------------------------------------------------------

# df with results of the prediction
def pred_json_df(json_path, model_clf):
    x_dframe = json_to_ml_features_df(json_path, model_clf)
    return forecast.prediction_df(x_dframe, model_clf)


# df ready for the ML-model----------------------------------------------
def json_to_ml_features_df(json_path, model_clf, df_continous_path = "03_AirQuality_continuous.csv", feature_df_path = "02_AlleFeatureList.csv", smart = True):
    df = json_to_correct_df(json_path, df_continous_path, feature_df_path)
    df.set_index("date", inplace = True)
    df = forecast.df_to_feature_columns(model_clf, df)
    return df


# JSON to clean DataFrame -----------------------------------------------------------------------------------------

# prepared_df with replaced missing values
def json_to_correct_df(json_path, df_continous_path = "03_AirQuality_continuous.csv", feature_df_path = "02_AlleFeatureList.csv" , smart = True):
    #data preparation
    df = json_to_prepared_df(json_path, smart)
    
    #DataFrame with the whole data set
    df_continuous = pd.read_csv(org.path("03_AirQuality_continuous.csv"), sep=';')
    
    #missing value treatment
    df = df_replace_missing_continuous(df,df_continuous, feature_df_path)
    
    #add to main data set
    add_new_df(df, df_continuous, df_continous_path)
    
    return df



# df with correct datetime and other datapes; column name with small letters and droped unknown columns
def json_to_prepared_df(json_path, smart = True):
    df = json_to_df(json_path, smart)
    df = data_prep.data_preparation_df(df)
    return df



#json is save like the original dateset (capital letters)
def json_to_df(json_path, smart = True):
    df = pd.DataFrame (columns = og_column_list())
    f = open(org.path(json_path, smart))
    data = json.load(f)
    f.close()
    df = df.append(data)  
    return df


#missing value treatment------------------------------

def df_replace_missing_continuous(new_df, dframe_continuous, feature_df_path = "02_AlleFeatureList.csv"):
    
    feature_df = pd.read_csv(org.path(feature_df_path), sep =";", index_col='names')
    
    list_col_mean = ["co_gt","pt08_s1_co", "c6h6_gt", "pt08_s2_nmhc", "pt08_s3_nox", "no2_gt", "nmhc_gt"]
    list_col_hist = ["nox_gt","pt08_s4_no2", "pt08_s5_o3", "t", "rh", "ah"]
        
    new_df = mvtreatment.filter_plausible(new_df, feature_df)
    
    
    for m in list_col_mean:
        new_df[m] = mvtreatment.column_replace_na_by_mean(new_df, feature_df, m)
    
    for h in list_col_hist:
        new_df[h] = column_replace_na_by_hist(new_df,dframe_continuous, h)

    
    return new_df


# methode - replacement of NaN values by historical data
def column_replace_na_by_hist(new_dframe,dframe_continuous, column):
    
    #last entries
    df_hist = dframe_continuous.tail()
    
    #concat
    concat_df = readj.dfs_concat(df_hist, new_dframe)
    
    #get number of rows of new_df
    numb_new_rows = new_dframe.shape[0]

    concat_df[column] = concat_df[column].fillna(method= 'ffill')
    
    return concat_df.tail(1)[column].values




#static values/lists -----------------------------------------------------------------------------------------------------------------


def og_column_list():
    og_list = ['Date', 'Time', 'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 'C6H6(GT)',
       'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)',
       'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
    return og_list

