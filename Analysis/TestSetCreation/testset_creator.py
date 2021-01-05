from utils.elastic_search_methods import ElasticSearchUtils
from utils.utils import DateUtils
from datetime import datetime, timedelta
import json

class TestSetCreator():

    # Create a separate ES index for the test set by reindexing the full articles index
    # into a smaller date range [gte_date,lt_date]
    def create_testset_index(self, es_port, es_timeout, reindex_timeout,source_index,dest_index,gte_date,lt_date):
        ElasticSearchUtils.reindex(es_port, es_timeout, reindex_timeout,source_index,dest_index,gte_date,lt_date)


    # Returns : (if test_boundaries = ['2020-10-01','2020-10-25']
    #   {
    #       "2020-10-01" : [ { 'significant_text': ... , "score": ...}, .... ,{ 'significant_text': ... , "score": ...} ],
    #       ...
    #       "2020-10-25" : [ { 'significant_text': ... , "score": ...}, .... ,{ 'significant_text': ... , "score": ...} ],
    #   }

    def get_testset_daily_significant_texts(self,es_port, es_index, timeout, field, max_nb_words, test_boundaries,date_format):
        testset_start = datetime.strptime(test_boundaries[0],date_format)
        testset_end = datetime.strptime(test_boundaries[1],date_format)
        # List containing all the days of the test_boundaries interval in the date_format
        testset_days = [datetime.strftime(testset_start + timedelta(days=x), date_format) for x in range((testset_end-testset_start).days + 1)]

        significant_texts_per_day = {}
        # For each day in the test_boundaries date range, we query the significant-texts
        for day in testset_days:
            single_day_significant_texts = ElasticSearchUtils.get_es_significant_texts_by_dates(es_port, es_index, timeout, [day], field, max_nb_words) #the array wrapping of the day variable is just an elastic search constraint
            significant_texts_per_day[day] = single_day_significant_texts

        return significant_texts_per_day

    @staticmethod
    def create_y_true(test_boundaries, date_format, testset_company_relevant_dates):
        # CREATE y_true json
        y_true = []
        testset_days_list = DateUtils.get_days_list_from_date_interval(test_boundaries,date_format)

        # Test timeframe companies
        TEST_COMPANIES = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMD', 'AMGN', 'AMZN', 'ASML', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CDNS', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DLTR', 'EA', 'EBAY', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'HAS', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'LULU', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL', 'NFLX', 'NTAP', 'NTES', 'NVDA', 'NXPI', 'ORLY', 'PAYX', 'PCAR', 'PEP', 'PYPL', 'QCOM', 'REGN', 'ROST', 'SBUX', 'SIRI', 'SNPS', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'UAL', 'ULTA', 'VRSK', 'VRSN', 'VRTX', 'WBA', 'WDAY', 'WDC', 'WLTW', 'WYNN', 'XEL', 'XLNX']
        #TODO : generate the companies' list in a dynamic way through a separate function

        # Generate the json with all test_boundaries dates and all companies with the value 0
        for idx,day in enumerate(testset_days_list):
            # Store the day in the prediction array
            y_true.append({})
            y_true[idx]['date'] = day
            y_true[idx]['companies'] = {}
            for company in TEST_COMPANIES:
                # Store the company with its class prediction
                y_true[idx]['companies'][company] = 0
        print("y_true blank = ",y_true)
        # Replace the 0 values with 1 values for the companies that have experienced a loss > CLOSE_PRICE_MOVEMENT_THRESHOLD within the test_boundaries
        for company in testset_company_relevant_dates:
            for loss_date in testset_company_relevant_dates[company]:
                for i in range(len(y_true)):
                    if y_true[i]['date'] == loss_date and company in y_true[i]['companies']:
                        y_true[i]['companies'][company] = 1
        print("y_true filled = ",y_true)
        '''
        with open('y_true.json', 'w') as f:
            json.dump(y_true, f)   
        '''
        return y_true

if __name__ == '__main__':
    testset_creator = TestSetCreator()
    testset_significant_texts_per_day = testset_creator.get_testset_daily_significant_texts(es_port=9200, es_index="articles_20201001_20201025_no_duplicate_title",
                                                        timeout=30, field="title", max_nb_words=30,test_boundaries=["2020-10-01","2020-10-25"],
                                                        date_format="%Y-%m-%d")
    # Save the model in a json file (the significant-texts per company dictionary)
    with open('testset_significant_texts_per_day_v1_20201001_20201025.json', 'w') as f:
        json.dump(testset_significant_texts_per_day, f)
