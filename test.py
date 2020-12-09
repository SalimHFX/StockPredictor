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



        # V0 : FAIRE TOUT POUR UNE SEULE ENTREPRISE
        stock_movement_dates = {}
        # verify cause_timeframe validity (yet to be done)
        # get the cursor index
        timeframe_index = int(re.search(r'\d+', cause_timeframe).group())
        # place the cursor on the timeframe index
        current_company_name = stock_prices[0]['event']['symbol']
        stock_prices_cursor = 0
        for stock_price in stock_prices:
            company_name = stock_price['event']['symbol']
            if (company_name == current_company_name and stock_prices_cursor < timeframe_index):
                stock_prices_cursor += 1
                current_company_name = company_name
            else:

            #close_price = float(stock_price['event']['close'])
