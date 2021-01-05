from sklearn.metrics import accuracy_score, recall_score, precision_score

class ModelEvaluator():
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
        accuracies = []
        precisions = []
        recalls = []
        for i in range(len(y_true)):
            # Accuracy
            accuracies.append(accuracy_score(list(y_true[i]['companies'].values()),list(y_pred[i]['companies'].values())))
            # Precision
            precisions.append(precision_score(list(y_true[i]['companies'].values()),list(y_pred[i]['companies'].values())))
            # Recall
            recalls.append(recall_score(list(y_true[i]['companies'].values()),list(y_pred[i]['companies'].values())))

        #mean_accuracy = sum(accuracies) / len(accuracies)
        #mean_precision = sum(precisions) / len(precisions)
        #mean_recall = sum(recalls) / len(recalls)

        #return mean_accuracy, mean_precision, mean_recall
        return accuracies, precisions, recalls
