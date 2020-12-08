import json

class DataLoader():

    # Load existing data from json file, expects json to have either one object or an array of objects
    def load_data(self,data_path):
        with open(data_path) as json_file:
            data = json.load(json_file)
        return data

    # Convert json file containing N json objects not separated by a comma
    # to a valid json file readable by the json.load() function.
    # ONLY NEEDS TO BE RAN ONCE PER JSON FILE
    # The converted file is an array of json objects
    def convert_to_valid_json(self,data_path):
        data = []
        with open(data_path) as f:
            for line in f:
                data.append(json.loads(line))
        with open(data_path,'w') as f:
            f.write(json.dumps(data))
            f.close()
