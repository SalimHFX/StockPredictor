from Analysis.TestSetCreation.testset_creator import  TestSetCreator

class TestSetManager():
    @staticmethod
    def create_testset_significant_texts(es_port, es_index, timeout, field, max_nb_words, test_boundaries,date_format):
        testset_significant_texts_per_day = TestSetCreator.get_testset_daily_significant_texts(es_port, es_index,timeout, field, max_nb_words,test_boundaries,date_format)
        return testset_significant_texts_per_day

    @staticmethod
    def create_y_true(test_boundaries, date_format, testset_company_relevant_dates):
        y_true = TestSetCreator.create_y_true(test_boundaries, date_format, testset_company_relevant_dates)
        return y_true
