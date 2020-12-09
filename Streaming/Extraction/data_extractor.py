import re

#temp :
from Streaming.Loading import DataLoadingManager
from Streaming.Preprocessing import PreprocessingManager

STOCK_MOVEMENT = {'UPWARD','DOWNWARD'}

class DataExtractor:

    def __init__(self):
        self.companyNames = []

    # For each company, we identify the days in which its stock price has moved up or down by at least a percentage P
    # between the day D and the day D-N, N being the cause_timeframe parameter (e.g for N = 1 D-N is the day before).
    # We then return a dictionary with the following format :
    # { "company_i_name": <Relevant days>, .... }
    '''
    :param stock_prices: 
        json list of stocks, each json object inside the list must contain the company name in object['event']['symbol']
        and the closing price as a float in object['event']['close']
    :param cause_timeframe: 
        the timeframe inside which stock_movement will be looked for.
        Format = nD (e.g 1D = 1 day before, 7D = 7 days before)
    :param stock_movement: 
        must be in {'UPWARD','DOWNWARD'}
    :param close_price_movement_threshold: 
        percentage by which the close price should have moved upward/downward between D and D-N for the day D
        to be registered as relevant
    :return: 
    '''
    def identify_relevant_days(self,stock_prices, cause_timeframe, stock_movement, close_price_movement_threshold):
        if stock_movement not in STOCK_MOVEMENT:
            raise ValueError("identify_relevant_days: stock_movement must be one of %s." % STOCK_MOVEMENT)
        #Pseudo-code :
        # - Pour chaque company :
        #       - placer le curseur à la N-ème occurence de cette company dans les stocks prices (avec N = cause_timeframe)
        #         typiquement si cause_timeframe = 1j alors il faut commencer à partir de la 2ème occurence pour faire des
        #         comparaisons d'1j
        #       - faire des comparaisons en avançant d'1j (qlq soit la cause_timeframe), si le mouvement est sup/inf au movement
        #         percentage, enregistrer la date
        #       - gérer les jours manquants et les weekends, comment ?
        # - Contre-fonctionnalités :
        #       - détecter le changement d'entreprise


        # V0 : FAIRE TOUT POUR UNE SEULE ENTREPRISE ET POUR UN STOCK_MOVEMENT = DOWNWARD
        stock_movement_dates = {}
        # verify cause_timeframe validity (yet to be done)
        # get the cursor index
        timeframe_index = int(re.search(r'\d+', cause_timeframe).group()) # = 1
        # place the cursor on the timeframe index
        stock_prices_cursor = 0
        for i in range(timeframe_index,len(stock_prices)):
            current_day_price = float(stock_prices[i]['event']['close'])
            comparison_day_price = float(stock_prices[i-timeframe_index]['event']['close'])
            close_price_movement = self.percentage_decrease_change(comparison_day_price,current_day_price)

            # close_price_movement < 0 <=> negative decrease <=> increase, since we're only tackling decrease in the baseline, this date won't be relative
            if close_price_movement > 0 and close_price_movement > close_price_movement_threshold:
                current_company = stock_prices[i]['event']['symbol']
                if current_company not in stock_movement_dates:
                    stock_movement_dates[current_company] = []
                stock_movement_dates[current_company].append(stock_prices[i]['event']['time'])

        return stock_movement_dates


    def percentage_decrease_change(self, original_number: float, new_number: float):
        return (original_number-new_number)/original_number

    # Merge FOX/FOXA ?

    if __name__ == '__main__':
        config_file = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/StockPredictor/config.json")
        print(config_file)
        CAUSE_TIMEFRAME = config_file['baseline']['dataset']['cause_timeframe']
        TRAIN_BOUNDARIES = config_file['baseline']['dataset']['train_boundaries']
        stock_prices = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/Dataset/one_company_stock_prices_sample.json")
        stock_prices = PreprocessingManager.preprocess_stock_prices(stock_prices, TRAIN_BOUNDARIES)

        stock_movement_dates = identify_relevant_days(stock_prices,CAUSE_TIMEFRAME, 'DOWNWARD', 0.01)

