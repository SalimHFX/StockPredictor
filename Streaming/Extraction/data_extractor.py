import json


STOCK_MOVEMENT = {'UPWARD','DOWNWARD'}

class DataExtractor:

    def __init__(self):
        self.companyNames = []

    # For each company, we identify the days in which its stock price has moved up or down by at least a percentage P
    # between the day D and the day D-N, N being the cause_timeframe parameter (e.g for N = 1 D-N is the day before).
    # We then return a dictionary with the following format :
    # { "company_i_name": <Relevant days>, .... }
    @staticmethod
    def identify_relevant_days(stock_prices, cause_timeframe, stock_movement, movement_percentage):
        if stock_movement not in STOCK_MOVEMENT:
            raise ValueError("identify_relevant_days: stock_movement must be one of %s." % STOCK_MOVEMENT)
        #Pseudo-code :
        # -
        return





    # Merge FOX/FOXA ?
