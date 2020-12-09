from Streaming.Loading.data_loader import DataLoader

class DataLoadingManager():
    # Load json file
    # Expects either an array of json objects or a stack of json objects
    @staticmethod
    def load_data(data_path):
        data_loader = DataLoader()
        try:
            return data_loader.load_data(data_path)
        except ValueError:
            print("DataExtractor.convert_to_valid_json : JSON file contained in {} wasn't initially valid valid and had to be converted"
                  "before being loaded".format(data_path))
            # Convert to valid JSON
            data_loader.convert_to_valid_json(data_path)
            # Load back the json
            return data_loader.load_data(data_path)
