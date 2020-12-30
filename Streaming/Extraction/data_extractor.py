import re
from datetime import datetime
#to be deleter later, just for testing
from Streaming.Loading import DataLoadingManager

STOCK_MOVEMENT = {'UPWARD','DOWNWARD'}

class DataExtractor:

    '''
    Description :
        For each company, we identify the days in which its stock price has moved up or down by at least a percentage P
        between the day D and the day D-N, D-N being the train_timeframe_window parameter (e.g for D-N = D-1 we'll compare
        each stock price to the stock price of the same company of the day before)
    Params :
        @stock_prices: json list of stocks, each json object inside the list must contain the company name in object['event']['symbol']
          and the closing price as a float in object['event']['close']
        @train_timeframe_window: the timeframe inside which stock_movement will be looked for. Format = J-N (e.g J-3 = 3 days before)
        @stock_movement: must be in {'UPWARD','DOWNWARD'}
        @close_price_movement_threshold: percentage by which the close price should have moved upward/downward between D and D-N
          for the day D to be registered as relevant
    Return :
        Stock movement dates <Dictionary> :
        {
            'company_i_name': <List of relevant days>
        }
        Relevant day format <Dictionary> :
        { 'price_loss_date': 'YYYY-MM-DD', 'initial_date': 'YYYY-MM-DD'}
    '''
    def identify_relevant_days(self,stock_prices, train_timeframe_window, stock_movement, close_price_movement_threshold):
        if stock_movement not in STOCK_MOVEMENT:
            raise ValueError("identify_relevant_days: stock_movement must be one of %s." % STOCK_MOVEMENT)

        # V1 : PLUSIEURS ENTREPRISES && STOCK_MOVEMENT = DOWNWARD
        # Pour chaque stock_price i, on remonte en arrière à partir de (i-1) pour trouver un stock de comparaison. Le stock
        # de comparaison est le stock ayant la date correspondant exactement à (date[i]-train_timeframe_window) et qui
        # appartient à la même company. Si ce stock n'existe pas, on passe au stock suivant.
        # Si le stock de comparaison existe (même company + bonne date) on lance la comparaison des closing prices, si
        # il y a bien eu un mouvement downward > threshold, on enregistre les deux dates dans le dictionnaire de la key associée
        # à la company
        #TODO : L'algo pourrait être vachement simplifié, le cpt est inutile, il suffit pour un stock [i] de checker le stock [i-1], si la date est pas bonne on passe au stock suivant. Là on sort la bazooka sur un moustique

        stock_movement_dates = {}
        train_timeframe_window = int(re.search(r'\d+', train_timeframe_window).group())
        print('Train timeframe window is ',train_timeframe_window)
        for i in range(1,len(stock_prices)):
            # Get company names for comparison
            current_company = stock_prices[i]['event']['symbol']
            found_the_previous_date = False
            cpt = 1
            while i >= cpt and not found_the_previous_date:
                previous_company = stock_prices[i-cpt]['event']['symbol']
                # Verify that the comparison is done on the same company
                if current_company == previous_company:
                    # Get dates for comparison
                    date_format = '%Y-%m-%d'
                    current_stock_date = datetime.strptime(stock_prices[i]['event']['time'],date_format)
                    previous_stock_date = datetime.strptime(stock_prices[i-cpt]['event']['time'],date_format)
                    time_distance = (current_stock_date - previous_stock_date).days
                    if time_distance == train_timeframe_window:
                        found_the_previous_date = True
                        #Calculate the stock close price movement
                        current_day_price = float(stock_prices[i]['event']['close'])
                        comparison_day_price = float(stock_prices[i-cpt]['event']['close'])
                        close_price_movement = self.percentage_decrease_change(comparison_day_price,current_day_price)
                        '''
                        print('Current company is {}, comparing current_day_price = {} ({}) to comparison_day_price = {} ({}), close_price_movement is {}'.format(
                            current_company, current_day_price,current_stock_date, comparison_day_price,previous_stock_date,close_price_movement
                        ))
                        '''

                        #If it's over the threshold, store the date
                        # close_price_movement < 0 <=> negative decrease <=> increase, since we're only tackling decrease in the baseline, this date won't be relative
                        if close_price_movement > 0 and close_price_movement > close_price_movement_threshold:
                            if current_company not in stock_movement_dates:
                                stock_movement_dates[current_company] = []
                            stock_movement_dates[current_company].append(
                                {'price_loss_date':stock_prices[i]['event']['time'],'initial_date':stock_prices[i-cpt]['event']['time']})
                    else:
                        cpt += 1
                else:
                    break

        return stock_movement_dates




    '''
    Description :
        For each company, we identify the days in which its stock price has moved up or down by at least a percentage P
        between the day D and the day D-N, D-N being the train_timeframe_window parameter (e.g for D-N = D-1 we'll compare
        each stock price to the stock price of the same company of the day before)
    Params : 
        @stock_prices: json list of stocks, each json object inside the list must contain the company name in object['event']['symbol']
          and the closing price as a float in object['event']['close']
        @train_timeframe_window: the timeframe inside which stock_movement will be looked for. Format = J-N (e.g J-3 = 3 days before)
        @stock_movement: must be in {'UPWARD','DOWNWARD'}
        @close_price_movement_threshold: percentage by which the close price should have moved upward/downward between D and D-N 
          for the day D to be registered as relevant
    Return :
        Stock movement dates <Dictionary> :
        {
            'company_i_name': <List of relevant days>
        }
        Relevant day format <Dictionary> :
        { 'price_loss_date': 'YYYY-MM-DD', 'initial_date': 'YYYY-MM-DD'}
    '''
    def identify_relevant_days_old_version(self,stock_prices, train_timeframe_window, stock_movement, close_price_movement_threshold):
        if stock_movement not in STOCK_MOVEMENT:
            raise ValueError("identify_relevant_days: stock_movement must be one of %s." % STOCK_MOVEMENT)

        # V1 : PLUSIEURS ENTREPRISES && STOCK_MOVEMENT = DOWNWARD
        # Pour chaque stock_price i, on remonte en arrière à partir de (i-1) pour trouver le stock ayant la date la plus proche
        # de (date[i]-train_timeframe_window) et qui appartient à la même company.
        # (la date la plus proche c'est soit exactement la date[i]-train_timeframe_window soit une date inférieure)
        # Une fois le stock de comparaison trouvé (bonne date + même company) on lance la comparaison des closing prices, si
        # il y a bien eu un mouvement downward > threshold, on enregistre les deux dates dans le dictionnaire de la key associée
        # à la company
        stock_movement_dates = {}
        train_timeframe_window = int(re.search(r'\d+', train_timeframe_window).group())
        print('Train timeframe window is ',train_timeframe_window)
        for i in range(1,len(stock_prices)):
            # Get company names for comparison
            current_company = stock_prices[i]['event']['symbol']
            found_the_previous_date = False
            cpt = 1
            while i >= cpt and not found_the_previous_date:
                previous_company = stock_prices[i-cpt]['event']['symbol']
                # Verify that the comparison is done on the same company
                if current_company == previous_company:
                    # Get dates for comparison
                    date_format = '%Y-%m-%d'
                    current_stock_date = datetime.strptime(stock_prices[i]['event']['time'],date_format)
                    previous_stock_date = datetime.strptime(stock_prices[i-cpt]['event']['time'],date_format)
                    time_distance = (current_stock_date - previous_stock_date).days
                    print("time_distance = ",time_distance)
                    if time_distance >= train_timeframe_window:
                        found_the_previous_date = True
                        #Calculate the stock close price movement
                        current_day_price = float(stock_prices[i]['event']['close'])
                        comparison_day_price = float(stock_prices[i-cpt]['event']['close'])
                        close_price_movement = self.percentage_decrease_change(comparison_day_price,current_day_price)
                        print('Current company is {}, comparing current_day_price = {} ({}) to comparison_day_price = {} ({}), close_price_movement is {}'.format(
                            current_company, current_day_price,current_stock_date, comparison_day_price,previous_stock_date,close_price_movement
                        ))

                        #If it's over the threshold, store the date
                        # close_price_movement < 0 <=> negative decrease <=> increase, since we're only tackling decrease in the baseline, this date won't be relative
                        if close_price_movement > 0 and close_price_movement > close_price_movement_threshold:
                            if current_company not in stock_movement_dates:
                                stock_movement_dates[current_company] = []
                            stock_movement_dates[current_company].append(
                                {'price_loss_date':stock_prices[i]['event']['time'],'initial_date':stock_prices[i-cpt]['event']['time']})
                    else:
                        cpt += 1
                else:
                    break

        return stock_movement_dates


    def percentage_decrease_change(self, original_number: float, new_number: float):
        return (original_number-new_number)/original_number


if __name__ == '__main__':
    #stock_prices = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/Dataset/stock_prices/stock_prices_20200501_20200930.json")
    stock_prices = DataLoadingManager.load_data("/home/salim/Coding/Masters Project/Dataset/stock_prices_testing/stock_prices_sample_duplicate.json")
    data_extractor = DataExtractor()
    stock_movement_dates = data_extractor.identify_relevant_days(stock_prices,'D-1', 'DOWNWARD', 0.01)
    print(stock_movement_dates)

