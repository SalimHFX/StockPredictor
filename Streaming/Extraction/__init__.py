from Streaming.Extraction.data_extractor import DataExtractor


class DataExtractionManager():
    @staticmethod
    def extract_relevant_days_by_company(stock_prices, train_timeframe_window, stock_movement, close_price_movement_threshold, date_format):
        data_extractor = DataExtractor()

        relevant_days_by_company = data_extractor.identify_relevant_days(stock_prices, train_timeframe_window, stock_movement, close_price_movement_threshold, date_format)

        formatted_relevant_days_by_company = data_extractor.convert_company_dates(relevant_days_by_company,train_timeframe_window,date_format)

        print("DataExtractionManager.extract_data : EXTRACTION DONE")

        return formatted_relevant_days_by_company



