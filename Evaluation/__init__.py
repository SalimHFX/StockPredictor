from Evaluation.model_evaluator import ModelEvaluator

class ModelEvaluationManager():

    '''
    y_pred/y_true : [ {
                        "date" : "2020-10-01",
                        "companies" : { 'company_1':0, ...., 'company_n':1 }
                      },
                      .....
                     {
                        "date" : "2020-10-25",
                        "companies" : { 'company_1':0, ...., 'company_n':1 }
                     }
                   ]
    '''
    @staticmethod
    def evaluate_model(y_true,y_pred):
        return ModelEvaluator.evaluate_model(y_true,y_pred)
