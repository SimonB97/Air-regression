# Organizational Functions---------------------------------------------------------------

def path(path, smart = True):
    start = "../../data/"
    
    if smart == False:
        full_path = start + path
        return full_path
    
    else:
        split_extention = path.split(".")
        extra_path = ""
        
        #file is a CSV file
        if split_extention[1] == "csv":
            if "FeatureList" in split_extention[0]:
                extra_path = "csv/FeatureList/"
            elif "Air" in split_extention[0]:
                extra_path = "csv/AirQuality/"
            else:
                extra_path = "csv/"
        # file is not a CSV file
        elif split_extention[1] == "json":
            extra_path = "results/json/"
        else:    
            extra_path = "results/"
    
        full_path = start + extra_path + path
    
        return full_path


def data_path(path):
    start = "../../data/"
    full_path = start + path
    return full_path


