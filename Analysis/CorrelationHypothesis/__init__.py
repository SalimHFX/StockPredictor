from Analysis.CorrelationHypothesis.day_by_day_model import DayByDayStockPredictionModel


class DayByDayModelCreationManager():
    @staticmethod
    def train_day_by_day_model(es_port, timeout, es_index, es_index_size, foreground_to_background_index_threshold, company_relevant_days,
                    significant_text_field="title", max_words_per_company="10"):

        stock_predictor_model = DayByDayStockPredictionModel(company_relevant_days=company_relevant_days)
        #print("stockPredictor.companyRelevantDays :",stock_predictor_model.companyRelevantDays)

        stock_predictor_model.set_companySignificantTexts(es_port=es_port, timeout=timeout, es_index=es_index, es_index_size=es_index_size,
                                                          foreground_to_background_index_threshold=foreground_to_background_index_threshold,
                                                          significant_text_field=significant_text_field, max_words_per_company=max_words_per_company)
        #print("stockPredictor.companySignificantTexts :",stock_predictor_model.companySignificantTexts)

        return stock_predictor_model

    @staticmethod
    def from_json(significant_texts_per_company_json_file):
        return DayByDayStockPredictionModel.from_json(significant_texts_per_company_json_file)

