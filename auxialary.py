import json

def get_json_data(file_path, debug = True):
    if debug:
        print("get_json_data")
    with open(file_path, encoding="utf-8") as file:
            json_data = json.load(file)
            if debug:
                print(to_json(json_data))
            return json_data
    if debug:    
        print("JSON data from " + file_path + " could not be loaded!")
    return None

def to_json(data):
    return json.dumps(data, indent = 4, sort_keys=True)