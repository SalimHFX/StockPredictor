from Streaming.Loading import DataLoadingManager
from Streaming.Preprocessing import PreprocessingManager
from Streaming.Extraction import DataExtractionManager

# Load the configuration used for the pipeline
config_file = DataLoadingManager.load_data("config.json")

# Config constants : Dataset related
CORPUS_PER_COMPANY_FILTERING = config_file['baseline']['dataset']['corpus_per_company_filtering']
SOURCE = config_file['baseline']['dataset']['source']
FEED_FILTERING = config_file['baseline']['dataset']['feed_filtering']
TRAIN_TIMEFRAME_WINDOW = config_file['baseline']['dataset']['train_timeframe_window']
EFFECT_TIMEFRAME = config_file['baseline']['dataset']['effect_timeframe']
TRAIN_BOUNDARIES = config_file['baseline']['dataset']['train_boundaries']
TEST_BOUNDARIES = config_file['baseline']['dataset']['test_boundaries']
# Config constants : Analysis related
ANALYSIS_TYPE = config_file['baseline']['analysis']['type']
#ANALYSIS_FIELDS = config_file['baseline']['analysis']['fields']
#NB_WORDS_PER_DAY = config_file['baseline']['analysis']['nb_words_per_day']
#AGGREGATION_METRIC = config_file['baseline']['analysis']['aggregation_metric']
#COMPARISON_METRIC = config_file['baseline']['analysis']['comparison_metric']
# Config constants : Evaluation related
EVALUATION_METRICS = config_file['baseline']['evaluation']['metrics']

# Load the data files (news headlines and stock price information)
#stock_prices = DataLoadingManager.load_data("~/Coding/Masters Project/Dataset/
stock_prices = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/Dataset/multiple_companies_stock_prices_sample.json")
#articles = DataLoadingManager.load_data("~/Coding/Masters Project/Dataset/articles_20201015_20201026.json")

# Preprocess the loaded data
stock_prices = PreprocessingManager.preprocess_stock_prices(stock_prices, TRAIN_BOUNDARIES)
print(stock_prices)
# TODO : think of a way to use a different workflow if the stock_prices/articles have already been preprocessed
# TODO : articles preprocessing

# Extract the data from the data files (relevant days from stock prices, and titles from news headlines corresponding to those relevant days)
stock_movement_dates = DataExtractionManager.extract_data(stock_prices,'J-30', 'DOWNWARD', 0.01)
print(stock_movement_dates)

# Create the model

# Train the model (launch ES request, store the significant-text per company results in a data structure inside the model)

# Predict

# Evaluate the model

# Fine-tune the model
