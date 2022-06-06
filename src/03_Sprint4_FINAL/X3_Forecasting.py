import pandas as pd
import json
import orga_functions as org

#functions-------------------------------------------------------------------------------------------------------------------------------


# DataFrame that displays the actual future ah_values in comparison with the prediction
def check_df(x_dframe, y_values, reg_model):
    
    #transforms series into DataFrame (avoid errors)
    if isinstance(y_values, pd.Series):
        y_values = y_values.to_frame()
    
    set_date_index(y_values)
    
    #array of predicted values
    pred_y = pred_array(x_dframe, reg_model)
    
    #series of predicted values
    series_pred = pd.Series(pred_y)
    
    #series of actual future values
    series_future = pd.Series(y_values["ah_target"].values)
    
    #dataframe with datetime of the prediction
    date = pd.DataFrame(x_dframe.index.values)
    date[0] = pd.to_datetime(date[0], format = "%Y-%m-%d %H:%M:%S")
    date["future_datetime"] = date[0] + pd.DateOffset(hours=6, minutes=0)
    date.drop(columns=[0], inplace = True)
    
    #new dataframe for checking the prediction
    check_df = pd.concat([date["future_datetime"], series_future, series_pred], axis=1)
    check_df.rename(columns= {0: "future_ah", 1:"predicted_ah"}, inplace = True)
    check_df.set_index("future_datetime", inplace = True)
    return check_df


# DataFrame that displays the prediction
def prediction_df(x_dframe, reg_model):
    
    #array of predicted values
    pred_y = pred_array(x_dframe, reg_model)
    
    #series of predicted values
    series_pred = pd.Series(pred_y)
    
    #dataframe with datetime of the prediction
    date = pd.DataFrame(x_dframe.index.values)
    date[0] = pd.to_datetime(date[0], format = "%Y-%m-%d %H:%M:%S")
    date["future_datetime"] = date[0] + pd.DateOffset(hours=6, minutes=0)
    date.drop(columns=[0], inplace = True)
    
    #new dataframe
    pred_df = pd.concat([date["future_datetime"], series_pred], axis=1)
    pred_df.rename(columns= {0:"predicted_ah"}, inplace = True)
    pred_df.set_index("future_datetime", inplace = True)
    return pred_df


# array of predicted values
def pred_array(x_dframe, reg_model):
    
    set_date_index(x_dframe)
    data = df_to_feature_columns(reg_model, x_dframe)
    return reg_model.predict(data)


#only columns needed by the model, other columns dropped 
def df_to_feature_columns(reg_model, dframe):
    reg_feature_list = reg_model.feature_names_in_
    
    for x in dframe.columns:
        if not x in reg_feature_list:
            dframe.drop(columns= [x], inplace = True)
    return dframe



# set date as index (if it has not already happened)
def set_date_index(dframe):
    if set(dframe).issuperset(["date"]):
        if dframe.index.name == None:
            dframe.set_index("date", inplace = True)
    return dframe
