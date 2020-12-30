from Streaming.Preprocessing.stock_prices_preprocessor import  StockPricesPreprocessor

class PreprocessingManager():
    @staticmethod
    def preprocess_stock_prices(stock_prices, time_interval):
        # Launch Preprocessor
        stock_prices_preprocessor = StockPricesPreprocessor()

        # Clean stock prices
        stock_prices = stock_prices_preprocessor.clean_stock_prices(stock_prices)

        # Sort stock prices : by company and by date
        stock_prices = stock_prices_preprocessor.sort_stock_prices_by_date(stock_prices)
        stock_prices = stock_prices_preprocessor.sort_stock_prices_by_company(stock_prices)

        # Filter stock prices : restrict stocks to a given time interval
        stock_prices = stock_prices_preprocessor.filter_stock_prices_by_date(stock_prices,time_interval)

        print("PreprocessingManager.preprocess_stock_prices : PREPROCESSING DONE")

        return stock_prices
