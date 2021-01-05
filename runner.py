from Streaming.Loading import DataLoadingManager
from Streaming.Preprocessing import PreprocessingManager
from Streaming.Extraction import DataExtractionManager
from Analysis.ModelCreation import ModelCreationManager
from Analysis.TestSetCreation import TestSetManager
from Evaluation import ModelEvaluationManager
from Cleaning.cleaner import SignificantTextsCleaner
import json
import argparse

# Load the configuration used for the pipeline
config_file = DataLoadingManager.load_data("config.json")

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
parser.add_argument('--model-path',type=str,default="/home/salim/Coding/Masters Project/StockPredictor/Saved Models/model_v1_20200501_20200930.json")
parser.add_argument('--save-model',type=bool,default=False)
parser.add_argument('--saved-model-path',type=str,default='/home/salim/Coding/Masters Project/StockPredictor/Saved Models/')
parser.add_argument('--load-testset-from-json',type=bool,default=False)
parser.add_argument('--testset-path',type=str,default="/home/salim/Coding/Masters Project/StockPredictor/Analysis/TestSetCreation/testset_significant_texts_per_day_v1_20201001_20201025.json")
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

# Create & Train the model (launch ES request, store the significant-text per company results in a data structure inside the model)
if(args.load_model_from_json):
    # Load model
    json_model = DataLoadingManager.load_data(args.model_path)
    # Clean model
    cleaned_model = SignificantTextsCleaner.clean_model(json_model)
    stock_prediction_model = ModelCreationManager.from_json(cleaned_model)
    print("Model Loading DONE")
else:
    stock_prediction_model = ModelCreationManager.train_model(es_port=CONNEXION_PORT,es_index=ELASTIC_TRAIN_INDEX,
                                                              timeout=CONNEXION_TIMEOUT,company_relevant_days=train_stock_movement_dates,
                                                              date_format=DATE_FORMAT, significant_text_field=ANALYSIS_FIELDS,
                                                              max_words_per_company=MAX_WORDS_PER_COMPANY)
    print("ModelCreationManager.create_model : MODEL CREATION AND TRAINING DONE")

# Save the model in a json file (the significant-texts per company dictionary)
if(args.save_model):
    with open(args.saved_model_path + 'model_v2_relevant_days_20200501_20200930.json', 'w') as f:
        json.dump(stock_prediction_model.companyRelevantDays, f)

    with open(args.saved_model_path + 'model_v2_20200501_20200930.json', 'w') as f:
        json.dump(stock_prediction_model.companySignificantTexts, f)
    print("runner : MODEL SAVING DONE")


# Create the test set
if(args.load_testset_from_json):
    testset = DataLoadingManager.load_data(args.testset_path)
    # Clean testset
    cleaned_testset = SignificantTextsCleaner.clean_model(testset)
    print("Testset Loading DONE")
else:
    testset = TestSetManager.create_testset_significant_texts(es_port=CONNEXION_PORT,es_index=ELASTIC_TEST_INDEX,timeout=CONNEXION_TIMEOUT,
                                                                                    field=ANALYSIS_FIELDS,max_nb_words=MAX_WORDS_PER_DAY,test_boundaries=TEST_BOUNDARIES,
                                                                                    date_format=DATE_FORMAT)
    # Clean testset
    cleaned_testset = SignificantTextsCleaner.clean_model(testset)

# Save the testset in a json file (the significant-texts per date dictionary)
if(args.save_testset):
    with open(args.saved_testset_path + 'testset_significant_texts_per_day_v2_20201001_20201025.json', 'w') as f:
        json.dump(cleaned_testset, f)
    print("runner : TESTSET SAVING DONE")

# Generate y_true for the test set
stock_prices = DataLoadingManager.load_data(args.stock_prices_path)
test_stock_prices = PreprocessingManager.preprocess_stock_prices(stock_prices, TEST_BOUNDARIES)
testset_company_relevant_dates = DataExtractionManager.extract_relevant_days_by_company(test_stock_prices,
                                                                                        TRAIN_TIMEFRAME_WINDOW,
                                                                                        CLOSE_PRICE_MOVEMENT_DIRECTION,
                                                                                        CLOSE_PRICE_MOVEMENT_THRESHOLD,DATE_FORMAT)
y_true = TestSetManager.create_y_true(TEST_BOUNDARIES, DATE_FORMAT, testset_company_relevant_dates)
# TODO : think of a way to use a different workflow if y_true has already been created (i.e you can just load it)

# Generate y_pred for the test set
y_pred = stock_prediction_model.predict_stock_movement(cleaned_testset,COMPARISON_METRIC_THRESHOLD)
# TODO : think of a way to use a different workflow if y_pred has already been created (i.e you can just load it)

# Evaluate the model
mean_accuracy, mean_precision, mean_recall = ModelEvaluationManager.evaluate_model(y_true, y_pred)
#print('mean_accuracy : ',mean_accuracy)
#print('mean_precision : ',mean_precision)
#print('mean_recall : ',mean_recall)
print('accuracies : ',mean_accuracy)
print('precisions : ',mean_precision)
print('recalls : ',mean_recall)

# Fine-tune the model

