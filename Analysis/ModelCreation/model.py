from utils.elastic_search_methods import ElasticSearchUtils
from utils.scoring_metrics import ScoringMetrics
import json

class StockPredictionModel():

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
        # companySignificantTexts =  { "company_i_name": [ {"significant_text": .., "score":..}, ..., {"significant_text": .., "score":..} ],
        #                              .....
        #                              "company_n_name: [ {"significant_text": .., "score":..}, ..., {"significant_text": .., "score":..} ]
        #                            }
        # on va faire en sorte que ce soit plutôt comme ça :
        # companySignificantTexts =  { "company_i_name": [ significant_text_1, ..., significant_text_n ],
        #                                   .....
        #                              "company_n_name: [ significant_text_1, ..., significant_text_n ]
        #                             }
        if company_significant_texts is None:
            self.companySignificantTexts = {}
        else:
            self.companySignificantTexts = company_significant_texts

    @classmethod
    def from_json(cls,significant_texts_per_company_json_file):
        stock_prediction_model = StockPredictionModel()
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

            # If the foregroundset size is small enough, we make the request without a sampler
            if foreground_to_background_proportion < foreground_to_background_index_threshold:
                # Get the elastic search significant text for the relevant days of one company
                self.companySignificantTexts[company] = ElasticSearchUtils.get_es_significant_texts_by_dates(
                    es_port=es_port,es_index=es_index, timeout=timeout,articles_dates=self.companyRelevantDays[company],
                    field=significant_text_field, max_nb_words=max_words_per_company)

            # If the foregroundset size is too big, we make the request with a sampler
            else:
                # We make the ES request with a sampler
                # Get the elastic search significant text for the relevant days of one company
                sample_size = es_index_size * foreground_to_background_index_threshold
                self.companySignificantTexts[company] = ElasticSearchUtils.get_es_significant_texts_by_dates_with_sampler(
                    es_port=es_port,es_index=es_index, timeout=timeout,articles_dates=self.companyRelevantDays[company],
                    field=significant_text_field, max_nb_words=max_words_per_company, sample_size=sample_size)

    def predict_stock_movement(self, testset_significant_texts_per_day, similarity_threshold):
        # For each day in the test set, we compare the significant-texts to every company's list of significant-texts through a Jaccard Similarity operation.
        # If the similarity score between a given company's significant-texts and the test set's significant-texts is higher than the SIMILARITY_THRESHOLD, we conclude that
        # that company will experience a stock_price loss in the timeframe corresponding to the TRAIN_TIMEFRAME_WINDOW (i.e if the model was trained on D-1 articles,
        # a similary score > SIMILARITY_THRESHOLD means that company will experience a stock_price loss in the next day that's higher than the CLOSE_PRICE_MOVEMENT_THRESHOLD)

        y_pred = []
        # Go through the test set's daily significant-texts
        for idx,day in enumerate(testset_significant_texts_per_day):
            # Store the day in the prediction array
            y_pred.append({})
            y_pred[idx]['date'] = day
            y_pred[idx]['companies'] = {}
            # Group the significant-texts of the day in one array
            one_day_significant_texts = testset_significant_texts_per_day[day][:10]
            # Compare it to each company's set of significant-texts
            for company in self.companySignificantTexts:
                one_company_significant_texts = self.companySignificantTexts[company]
                # Launch the comparison metric : Jaccard Similarity
                #company_similarity_score = jaccard_score(y_true=one_company_significant_texts,y_pred=one_day_significant_texts)
                company_similarity_score = ScoringMetrics.jaccard_similarity(one_company_significant_texts,one_day_significant_texts)
                # Store the company with its class prediction
                if(company_similarity_score >= similarity_threshold):
                    y_pred[idx]['companies'][company] = 1
                else:
                    y_pred[idx]['companies'][company] = 0
        print("y_pred = ",y_pred)

        return y_pred


if __name__ == '__main__':
    # Load the model from json
    with open('../../Saved Models/model_v1_20200501_20200930.json') as json_file:
        model_significant_texts = json.load(json_file)

    stock_predictor = StockPredictionModel.from_json(model_significant_texts)

    # Load the testset from json
    with open('../TestSetCreation/testset_significant_texts_per_day_v1_20201001_20201025.json') as json_file:
        testset = json.load(json_file)

    # Predict stock movements
    y_pred = stock_predictor.predict_stock_movement(testset,0.1)
    print("y_pred = ",y_pred)
    '''
    with open('y_pred_jaccard_0.1.json', 'w') as f:
        json.dump(y_pred, f)
    '''








