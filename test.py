from Streaming.Extraction.data_extractor import DataExtractor
from datetime import datetime
import json

# Load the configuration used for the pipeline
data_extractor = DataExtractor()
config_file = data_extractor.load_data("config.json")
TRAIN_BOUNDARIES = config_file['baseline']['dataset']['train_boundaries']




with open('/home/salim/Coding/Masters Project/Dataset/stock_prices_20200501_20200930.json','w') as f:
    f.write(json.dumps(stocks))
    f.close()



