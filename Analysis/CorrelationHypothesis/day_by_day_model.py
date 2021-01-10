from utils.elastic_search_methods import ElasticSearchUtils
from utils.scoring_metrics import ScoringMetrics
import json

class DayByDayStockPredictionModel():

    def __init__(self, company_significant_texts = None, company_relevant_days = None):
        # Dictionary containing for each company its relevant days (a relevant day is a day in which a stock movement has occured)
        # companyRelevantDays =  { "company_i_name": [ relevant_date_1 ,...., relevant_date_n],
        #                           .....
        #                           "company_n_name: [ relevant_date_1 ,...., relevant_date_m]
        #                        }
        # todo : maybe create a class for the CompanyRelevantDay data structure
        if company_relevant_days is None:
            self.companyRelevantDays = {}
        else:
            self.companyRelevantDays = company_relevant_days

        # Dictionary containing for each company a list of relevant words
        # companySignificantTexts =  { "company_i_name": {
        #                                                 "date_1": [ significant_text_1, ..., significant_text_n ],
        #                                                  ...
        #                                                 "date_n": [ significant_text_1, ..., significant_text_n ]
        #                                                }
        #                                   .....
        #                              "company_n_name: {
        #                                                 "date_1": [ significant_text_1, ..., significant_text_n ],
        #                                                  ...
        #                                                 "date_n": [ significant_text_1, ..., significant_text_n ]
        #                                                }
        #                             }
        if company_significant_texts is None:
            self.companySignificantTexts = {}
        else:
            self.companySignificantTexts = company_significant_texts

    @classmethod
    def from_json(cls,significant_texts_per_company_json_file):
        stock_prediction_model = DayByDayStockPredictionModel()
        stock_prediction_model.companySignificantTexts = significant_texts_per_company_json_file
        return stock_prediction_model


    # Launches one elastic search significant-text query per company (for each company, the query has all the company's the relevant dates)
    def set_companySignificantTexts(self, es_port, timeout, es_index, es_index_size, foreground_to_background_index_threshold, significant_text_field, max_words_per_company):
        for company in self.companyRelevantDays:
            # Verify that the foregroundset size is not close to the backgroundset (that makes the significant-text's quality bad)
            # TODO : move MAX_NB_ARTICLES_PER_DAY to the config file
            MAX_NB_ARTICLES_PER_DAY = 3000
            foreground_set_size = len(self.companyRelevantDays[company]) * MAX_NB_ARTICLES_PER_DAY
            foreground_to_background_proportion = foreground_set_size / es_index_size

            self.companySignificantTexts[company] = {}
            for date in self.companyRelevantDays[company]:

                # If the foregroundset size is small enough, we make the request without a sampler
                if foreground_to_background_proportion < foreground_to_background_index_threshold:
                    # Get the elastic search significant text for the relevant days of one company
                    self.companySignificantTexts[company][date] = ElasticSearchUtils.get_es_significant_texts_by_dates(
                        es_port=es_port,es_index=es_index, timeout=timeout,articles_dates=[date],
                        field=significant_text_field, max_nb_words=max_words_per_company)

                # If the foregroundset size is too big, we make the request with a sampler
                else:
                    # We make the ES request with a sampler
                    # Get the elastic search significant text for the relevant days of one company
                    sample_size = es_index_size * foreground_to_background_index_threshold
                    self.companySignificantTexts[company][date] = ElasticSearchUtils.get_es_significant_texts_by_dates_with_sampler(
                        es_port=es_port,es_index=es_index, timeout=timeout,articles_dates=[date],
                        field=significant_text_field, max_nb_words=max_words_per_company, sample_size=sample_size)

    '''
    Output format :
    {
        "company_1_name" : [
            {
                "train_date_1": ...,
                "test_date_CONST": ...,
                "similarity_score": ...,
            },
            ...
            {
                "train_date_n": ...,
                "test_date_CONST": ...,
                "similarity_score": ...,
            }          
        ],
        ...,
        "company_n_name": [
            ....
        ]
        
    }
    '''
    def similarity_score(self, testset_date, single_day_testset_significant_texts):
        json_output = {}
        # Compare it to each company's set of significant-texts
        for company in self.companySignificantTexts:
            json_output[company] = []
            for idx,date in enumerate(self.companySignificantTexts[company]):
                company_single_day_significant_texts = self.companySignificantTexts[company][date]
                # Launch the comparison metric : Jaccard Similarity
                #company_similarity_score = jaccard_score(y_true=one_company_significant_texts,y_pred=one_day_significant_texts)
                company_similarity_score = ScoringMetrics.jaccard_similarity(company_single_day_significant_texts,single_day_testset_significant_texts)
                # Fill output
                json_output[company].append({})
                json_output[company][idx]["train_date"] = date
                json_output[company][idx]["test_date_const"] = testset_date
                json_output[company][idx]["similarity_score"] = company_similarity_score

        return json_output
        #TODO : peut-être faire un notebook et lancer tous les histos (l'alternative ES est chiante parce qu'il faut un index par entreprise, et il y a une centaine d'entreprises)









