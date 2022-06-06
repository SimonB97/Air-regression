import pandas as pd
import json
import X1_DataPreparation as data_prep
import X2_MissingValueTreatment as mvtreatment
import X3_Forecasting as forecast
import orga_functions as org

#functions-------------------------------------------------------------------------------------------------------------------------------


#concat multiple dataframes
def dfs_concat(*dfs):
    df = pd.concat(dfs)
    df.reset_index(drop = True, inplace = True)
    return df


# JSON to df for Forecasting ------------------------------------------------------------------------------------------

# df with results of the prediction
def pred_json_df(json_path, model_clf):
    x_dframe = json_to_ml_features_df(json_path, model_clf)
    return forecast.prediction_df(x_dframe, model_clf)


# df ready for the ML-model----------------------------------------------
def json_to_ml_features_df(json_path, model_clf,feature_df_path = "02_AlleFeatureList.csv", smart = True):
    df = json_to_correct_missing_df(json_path, feature_df_path)
    df.set_index("date", inplace = True)
    df = forecast.df_to_feature_columns(model_clf, df)
    return df


# JSON to clean DataFrame ---------------------------------------------------------------------------------------------

# prepared_df with replaced missing values
def json_to_correct_missing_df(json_path,feature_df_path = "02_AlleFeatureList.csv" , smart = True):
    df = json_to_prepared_df(json_path, smart)
    df = mvtreatment.df_replace_missing(df, feature_df_path)
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


#static values/lists -----------------------------------------------------------------------------------------------------------------


def og_column_list():
    og_list = ['Date', 'Time', 'CO(GT)', 'PT08.S1(CO)', 'NMHC(GT)', 'C6H6(GT)',
       'PT08.S2(NMHC)', 'NOx(GT)', 'PT08.S3(NOx)', 'NO2(GT)',
       'PT08.S4(NO2)', 'PT08.S5(O3)', 'T', 'RH', 'AH']
    return og_list

