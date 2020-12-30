from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import re

class StockPredictionModel():

    def __init__(self, companyRelevantDays):
        # Dictionary containing for each company its relevant days
        # (a relevant day is a day in which a stock movement has occured)
        # todo : maybe create a class for the CompanyRelevantDay data structure
        self.companyRelevantDays = self.convert_company_dates(companyRelevantDays,'D-1','%Y-%m-%d')

        # Dictionary containing for each company a list of relevant words
        # no scores are attached to the words for the baseline version
        self.companySignificantTexts = {}


    #get_significant_texts(self,es_port,timeout,field,max_nb_words_per_company) : (9200,

    # Launch the ES significant-text request and get the response
    def get_es_significant_texts(self,es_port,timeout,articles_dates,field,max_nb_words):
        # Connect to the elastic cluster
        es = Elasticsearch([{'host':'localhost','port':es_port}],timeout=timeout)

        # Query the index
        res = es.search(index='articles_20200501_20200930_no_duplicate_title',body={
        "size":0,
        "query": {
            "bool": {
              "must": [{
                "terms": {
                  "published":articles_dates
                }
              }]
            }
        },
        "aggs": {
            "Significant texts": {
              "significant_text": {
                  "field": field,
                  "filter_duplicate_text": True,
                  "size": max_nb_words
              }
            }

        }

        })
        return res

    def format_es_response(self,es_response):
        formatted_response = []
        for item in es_response['aggregations']['Significant texts']['buckets']:
            formatted_response.append({'significant_text':item['key'], 'score':item['score']})
        return formatted_response

    def set_companySignificantTexts(self, es_port, timeout, significant_text_field, max_words_per_company):
        input_dates_for_significant_text = {}
        for company in self.companyRelevantDays:
            # Get the elastic search significant text for the relevant days of one company
            es_response = self.get_es_significant_texts(
                es_port,timeout,self.companyRelevantDays[company],significant_text_field, max_words_per_company)
            #print("Elastic search response : ",es_response)

            # Format the elasticsearch response and store it into the companySignificantTexts class attribute
            self.companySignificantTexts[company] = self.format_es_response(es_response)


    # Convert the company_relevant_days dictionary
    # { "company_i_name": [ {"price_loss_date":'XXXX-XX-XX',"initial_date":'XXXX-XX-XX'},
    #                       {"price_loss_date":'XXXX-XX-XX',"initial_date":'XXXX-XX-XX'}
    #                     ],
    #   ....
    #  "company_n_name": [ ... ]
    # }
    # to a dictionary with only the company names and the (price_loss_date - train_timeframe_window) :
    # { "company_i_name": [ 'YYYY-YY-YY','YYYY-YY-YY',....],
    #   "company_n_name: [..]
    # }
    def convert_company_dates(self, company_relevant_days, train_timeframe_window, date_format):
        input_dates_for_significant_text = {}
        train_timeframe_window = int(re.search(r'\d+', train_timeframe_window).group())
        for company,dates in company_relevant_days.items():
            input_dates_for_significant_text[company] = []
            for date in dates:
                # We append to the company dates the (price_loss_date - train_timeframe_window)
                # (for example that would be the day before the price_loss_date if train_timeframe_window = D-1)
                significant_text_date = str((datetime.strptime(date['price_loss_date'],date_format) - timedelta(days=train_timeframe_window)).strftime(date_format))
                input_dates_for_significant_text[company].append(significant_text_date)
        return input_dates_for_significant_text


if __name__ == '__main__':
    articles_dates = {
        "FOXA": [
            {'price_loss_date':'2020-05-03','initial_date':'2020-05-04'},
            {'price_loss_date':'2020-06-18','initial_date':'2020-06-19'}
        ],
        "GOOG": [
            {'price_loss_date':'2020-09-03','initial_date':'2020-09-04'}
        ]
    }

    stockPredictor = StockPredictionModel(articles_dates)
    print(stockPredictor.companyRelevantDays)
    stockPredictor.set_companySignificantTexts(es_port=9200,timeout=30,significant_text_field="title",max_words_per_company=10)
    print(stockPredictor.companySignificantTexts)
