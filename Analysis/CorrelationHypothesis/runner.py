from Streaming.Loading import DataLoadingManager
from Streaming.Preprocessing import PreprocessingManager
from Streaming.Extraction import DataExtractionManager
from Analysis.CorrelationHypothesis import DayByDayModelCreationManager
from Analysis.TestSetCreation import TestSetManager
from Evaluation import ModelEvaluationManager
from Cleaning.cleaner import SignificantTextsCleaner
from utils.utils import DateUtils
import json
import argparse



# Load the configuration used for the pipeline
config_file = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/StockPredictor/config.json")

# Config constants : Articles dataset related
CORPUS_PER_COMPANY_FILTERING = config_file['baseline']['articles_dataset']['corpus_per_company_filtering']
SOURCE = config_file['baseline']['articles_dataset']['source'] #YET TO BE USED
FEED_FILTERING = config_file['baseline']['articles_dataset']['feed_filtering'] #YET TO BE USED
TRAIN_TIMEFRAME_WINDOW = config_file['baseline']['articles_dataset']['train_timeframe_window']
EFFECT_TIMEFRAME = config_file['baseline']['articles_dataset']['effect_timeframe'] #YET TO BE USED
DATE_FORMAT = config_file['baseline']['articles_dataset']['date_format']
ELASTIC_TRAIN_INDEX = config_file['baseline']['articles_dataset']['elastic_train_index']
ELASTIC_TEST_INDEX = config_file['baseline']['articles_dataset']['elastic_test_index']
TRAIN_BOUNDARIES = config_file['baseline']['articles_dataset']['train_boundaries']
TEST_BOUNDARIES = config_file['baseline']['articles_dataset']['test_boundaries']
ELASTIC_TRAIN_INDEX_SIZE = config_file['baseline']['articles_dataset']['elastic_train_index_size']
ELASTIC_TRAIN_INDEX_FOREGROUND_TO_BACKGROUND_THRESHOLD = config_file['baseline']['articles_dataset']['elastic_train_index_foreground_to_background_threshold']

# Config constants : Stock prices dataset related
CLOSE_PRICE_MOVEMENT_THRESHOLD = config_file['baseline']['stock_prices_dataset']['close_price_movement_threshold']
CLOSE_PRICE_MOVEMENT_DIRECTION = config_file['baseline']['stock_prices_dataset']['close_price_movement_direction']

# Config constants : Analysis related
ANALYSIS_TYPE = config_file['baseline']['analysis']['type']
ANALYSIS_FIELDS = config_file['baseline']['analysis']['type']['fields']
MAX_WORDS_PER_COMPANY = config_file['baseline']['analysis']['type']['max_words_per_company']
MAX_WORDS_PER_DAY = config_file['baseline']['analysis']['type']['max_words_per_day']
CONNEXION_PORT = config_file['baseline']['analysis']['type']['connexion_port']
CONNEXION_TIMEOUT = config_file['baseline']['analysis']['type']['connexion_timeout']
#COMPARISON_METRIC = config_file['baseline']['analysis']['type']['comparison_metric']
COMPARISON_METRIC_THRESHOLD = config_file['baseline']['analysis']['type']['comparison_metric_threshold']

# Config constants : Evaluation related
EVALUATION_METRICS = config_file['baseline']['evaluation']['metrics']

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--stock-prices-path',type=str,default="/home/salim/Coding/Masters Project/Dataset/stock_prices/stock_prices_20201023.json")
parser.add_argument('--preprocessed-stock-prices',type=bool,default=False)
parser.add_argument('--load-model-from-json',type=bool,default=False)
# TODO : WARNING - not the same model path as the one in the main runner
parser.add_argument('--model-path',type=str,default="/home/salim/Coding/Masters Project/StockPredictor/Saved Models/day_by_day_model_v1_20200501_20200930.json")
parser.add_argument('--save-model',type=bool,default=False)
parser.add_argument('--saved-model-path',type=str,default='/home/salim/Coding/Masters Project/StockPredictor/Saved Models/')
parser.add_argument('--load-testset-from-json',type=bool,default=False)
parser.add_argument('--testset-path',type=str,default="/home/salim/Coding/Masters Project/StockPredictor/Analysis/TestSetCreation/testset_significant_texts_per_day_v2_20201001_20201025.json")
parser.add_argument('--save-testset', type=bool, default=False)
parser.add_argument('--saved-testset-path', type=str, default='/home/salim/Coding/Masters Project/StockPredictor/Analysis/TestSetCreation/')
args = parser.parse_args()
print(args)

# Load the data files (news headlines and stock price information)
#stock_prices = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/Dataset/stock_prices/stock_prices_20200501_20200930.json")
#articles = DataLoadingManager.load_data("~/Coding/Masters Project/Dataset/articles_20201015_20201026.json")
stock_prices = DataLoadingManager.load_data(args.stock_prices_path)


# Preprocess the loaded data
if(args.preprocessed_stock_prices):
    train_stock_prices = stock_prices
else:
    train_stock_prices = PreprocessingManager.preprocess_stock_prices(stock_prices, TRAIN_BOUNDARIES)


# Extract the data from the data files (relevant days from stock prices, and titles from news headlines corresponding to those relevant days)
train_stock_movement_dates = DataExtractionManager.extract_relevant_days_by_company(train_stock_prices,TRAIN_TIMEFRAME_WINDOW, CLOSE_PRICE_MOVEMENT_DIRECTION, CLOSE_PRICE_MOVEMENT_THRESHOLD, date_format=DATE_FORMAT)
print(train_stock_movement_dates)

# Create & Train the model (launch ES request, store the significant-text per company results in a data structure inside the model)
if(args.load_model_from_json):
    # Load model
    json_model = DataLoadingManager.load_data(args.model_path)
    # Clean model
    cleaned_model = SignificantTextsCleaner.clean_day_by_day_model_from_json(json_model)
    stock_prediction_model = DayByDayModelCreationManager.from_json(cleaned_model)
    print("runner.py : Model Loading DONE")
else:
    # Create a new model
    stock_prediction_model = DayByDayModelCreationManager.train_day_by_day_model(es_port=CONNEXION_PORT, timeout=CONNEXION_TIMEOUT,
                                                              es_index=ELASTIC_TRAIN_INDEX,es_index_size = ELASTIC_TRAIN_INDEX_SIZE,
                                                              foreground_to_background_index_threshold = ELASTIC_TRAIN_INDEX_FOREGROUND_TO_BACKGROUND_THRESHOLD,
                                                              company_relevant_days=train_stock_movement_dates,
                                                              significant_text_field=ANALYSIS_FIELDS,
                                                              max_words_per_company=MAX_WORDS_PER_COMPANY)
    # Clean the model
    stock_prediction_model = SignificantTextsCleaner.clean_day_by_day_model(stock_prediction_model)
    print("ModelCreationManager.create_model : MODEL CREATION AND TRAINING DONE")
    #print(stock_prediction_model.companySignificantTexts)


# Save the model in a json file (the significant-texts per company dictionary)
if(args.save_model):
    with open(args.saved_model_path + 'day_by_day_model_v1_20200501_20200930.json', 'w') as f:
        json.dump(stock_prediction_model.companySignificantTexts, f)
    print("runner.py : MODEL SAVING DONE")

# Create the test set
if(args.load_testset_from_json):
    testset = DataLoadingManager.load_data(args.testset_path)
    # Clean testset
    cleaned_testset = SignificantTextsCleaner.clean_model_from_json(testset)
    print("runner.py : Testset Loading DONE")
else:
    print("nichts")



testset_dates = DateUtils.get_days_list_from_date_interval(["2020-10-01","2020-10-25"],"%Y-%m-%d")
for date in testset_dates:
    unhyphened_date = date.replace("-","")
    similarity_score_file_name = 'day_by_day_similarity_scores_train_20200501_20200930_test_'+unhyphened_date+'.json'
    with open('SimilarityScoreFiles/'+similarity_score_file_name, 'w') as f:
        json.dump(stock_prediction_model.similarity_score(date,cleaned_testset[date]), f)

