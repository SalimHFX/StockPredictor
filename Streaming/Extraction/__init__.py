from Streaming.Extraction.data_extractor import DataExtractor


class DataExtractionManager():
    @staticmethod
    def extract_data(stock_prices, cause_timeframe, stock_movement, close_price_movement_threshold):
        data_extractor = DataExtractor()
        return data_extractor.identify_relevant_days(stock_prices, cause_timeframe, stock_movement, close_price_movement_threshold)



