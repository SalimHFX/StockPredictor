from Analysis.ModelCreation.model import StockPredictionModel
from elasticsearch import Elasticsearch
import json

class ModelCreationManager():
    @staticmethod
    def train_model(es_port, es_index, timeout, company_relevant_days, date_format, significant_text_field="title", max_words_per_company="10"):
        stock_predictor_model = StockPredictionModel(company_relevant_days)
        #print("stockPredictor.companyRelevantDays :",stock_predictor_model.companyRelevantDays)
        stock_predictor_model.set_companySignificantTexts(es_port, es_index, timeout, significant_text_field, max_words_per_company)
        #print("stockPredictor.companySignificantTexts :",stock_predictor_model.companySignificantTexts)
        return stock_predictor_model

    @staticmethod
    def from_json(significant_texts_per_company_json_file):
        return StockPredictionModel.from_json(significant_texts_per_company_json_file)

