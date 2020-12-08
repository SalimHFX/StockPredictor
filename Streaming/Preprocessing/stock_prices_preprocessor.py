from datetime import datetime

class StockPricesPreprocessor():

    # It turns out the stock_prices json file contains some unwanted lines, e.g : {'@version': '1', 'tags': ['_http_request_failure', '_rubyexception', '_split_type_failure'], 'http_request_failure': {'backtrace': None, 'runtime_seconds': 10.346, 'request': {'url': 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TTWO&apikey=2AHY12KMSKYRG1IN&outputsize=full', 'method': 'get'}, 'error': 'Read timed out', 'name': 'TTWO'}, '@timestamp': '2020-07-13T20:54:24.051Z'}
    # This function deletes those lines and only keeps in the json file objects that have correct time, symbol and close price attributes.
    def clean_stock_prices(self, stock_prices):
        # Filter out objects that either do not have the time attribute or have a time attribute with a wrong format (time is the date)
        format = '%Y-%m-%d'
        correct_date = lambda x: ('event' in x) and ('time' in x['event']) and self.validate_date(x['event']['time'],format)
        stock_prices = list(filter(correct_date,stock_prices))
        # Filter out objects that either do not have a symbol/close attribute or have an empty symbol/close attribute (symbol is the company name, close is the stock's close price)
        non_null_attributes = lambda x: ('event' in x) and ('symbol' in x['event']) and ('close' in x['event']) and (x['event']['symbol'] != "") and (x['event']['close'] != "")
        stock_prices = list(filter(non_null_attributes,stock_prices))

        return stock_prices


    # Sort the stock_prices json file by date
    def sort_stock_prices_by_date(self,stock_prices):
        # stock_prices.sort() is more efficient than stock_prices = stock_prices.sorted()
        try:
            stock_prices.sort(key=lambda x: datetime.strptime(x['event']['time'], '%Y-%m-%d'))
            return stock_prices
        except AttributeError:
            print(AttributeError) #if access to a specific attribute is needed, dir(AttributeError) lists the class's attributes


    # Sort the stock_prices json file by company
    def sort_stock_prices_by_company(self,stock_prices):
        # stock_prices.sort() is more efficient than stock_prices = stock_prices.sorted()
        try:
            stock_prices.sort(key=lambda x: x['event']['symbol'])
            return stock_prices
        except AttributeError:
            print(AttributeError)

    # Filter out the stock prices whose date is outside of the time_interval parameter
    # time_interval = [start_date, end_date] with the dates having the format 'YYYY-MM-DD'
    def filter_stock_prices_by_date(self,stock_prices, time_interval):
        start_date = datetime.strptime(time_interval[0], '%Y-%m-%d')
        end_date = datetime.strptime(time_interval[1], '%Y-%m-%d')

        within_time_interval = lambda x: (datetime.strptime(x['event']['time'], '%Y-%m-%d') >= start_date) and (datetime.strptime(x['event']['time'], '%Y-%m-%d') <= end_date)
        stock_prices = list(filter(within_time_interval, stock_prices))

        return stock_prices

    #Validate a date format
    def validate_date(self,date_text,format):
        try:
            datetime.strptime(date_text, format)
            return True
        except ValueError:
            return False
            #raise ValueError("Incorrect data format, should be YYYY-MM-DD")
