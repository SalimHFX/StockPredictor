import spacy
from spacy.tokens import Doc
from Streaming.Loading import DataLoadingManager
from Analysis.ModelCreation.model import StockPredictionModel

class SignificantTextsCleaner():

    @staticmethod
    # Lemmatize + Del stopwords/digits(int/float)
    def clean_model(model:StockPredictionModel):
        cleaned_model = StockPredictionModel()

        nlp = spacy.load("en_core_web_sm")
        for company in model.companySignificantTexts:
            words = model.companySignificantTexts[company]
            cleaned_words = []
            doc = Doc(nlp.vocab, words=words)

            [cleaned_words.append(word.lemma_) for word in doc if not word.is_stop and not SignificantTextsCleaner.is_number(str(word))]
            cleaned_model.companySignificantTexts[company] = cleaned_words

            #print("TEXT - LEMMA - POS - TAG - DEP - SHAPE - IS_ALPHA - IS_STOP")
            #print('-',token.text,'-', token.lemma_,'-', token.pos_,'-', token.tag_,'-', token.dep_,'-',token.shape_,'-', token.is_alpha,'-', token.is_stop)

            # Stop fed from being lemmatized as feed
            # apostrophes, points or numbers inside words make the word categorized as not alpha

        return cleaned_model




    @staticmethod
    # Lemmatize + Del stopwords/digits(int/float)
    def clean_model_from_json(json_model):
        cleaned_json_model = {}

        nlp = spacy.load("en_core_web_sm")
        for company in json_model:
            words = json_model[company]
            cleaned_words = []
            doc = Doc(nlp.vocab, words=words)

            [cleaned_words.append(word.lemma_) for word in doc if not word.is_stop and not SignificantTextsCleaner.is_number(str(word))]
            cleaned_json_model[company] = cleaned_words

            #print("TEXT - LEMMA - POS - TAG - DEP - SHAPE - IS_ALPHA - IS_STOP")
            #print('-',token.text,'-', token.lemma_,'-', token.pos_,'-', token.tag_,'-', token.dep_,'-',token.shape_,'-', token.is_alpha,'-', token.is_stop)

            # Stop fed from being lemmatized as feed
            # apostrophes, points or numbers inside words make the word categorized as not alpha

        return cleaned_json_model

    @staticmethod
    def is_number(s):
        return s.replace('.','',1).replace(',','',1).isdigit()



if __name__ == '__main__':
    model = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/StockPredictor/Saved Models/model_v1_20200501_20200930.json")
    testset = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/StockPredictor/Analysis/TestSetCreation/testset_significant_texts_per_day_v1_20201001_20201025.json")
    print(testset)
    cleaned_model = SignificantTextsCleaner.clean_model(testset)
    print(cleaned_model)
