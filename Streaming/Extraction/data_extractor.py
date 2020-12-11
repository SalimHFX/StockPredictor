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

        # WARNING : Si cause_timeframe = J-1 le code assume que le stock_price en [i-1] date de J-1 si le stock_price en [i] date de J
        # donc il gère pas les trous
        # dit autrement il assume que les jours des stocks prices se suivent sans trou

        # V2 : Gérer les trous :  ne pas assumer que les jours se suivent toujours, toujours commencer à i=1, faire des comparaisons de date
        # en remontant l'index à partir de i-1
        # (e.g avec J-2 voir si il y a bien 2 jours entre [î] et [i-1])
        # s'il y a pile 2 jours c'est parfait
        # s'il y a moins de 2 jours, remonter l'index
        # s'il y a plus de 2 jours, prendre quand même cet index car on ne fera pas mieux (l'index étant trié par date) -> notifier qu'une comparaison a été faite
        # avec un trou

        # V1 : PLUSIEURS ENTREPRISES ET STOCK_MOVEMENT = DOWNWARD, assume que les indices sont quotidiens et se suivent sans trous
        stock_movement_dates = {}
        cause_timeframe = int(re.search(r'\d+', cause_timeframe).group())
        print('Cause timeframe is ',cause_timeframe)
        for i in range(cause_timeframe,len(stock_prices)):
            current_company = stock_prices[i]['event']['symbol']
            previous_company = stock_prices[i-cause_timeframe]['event']['symbol']
            if(current_company == previous_company):
                #Calculate the stock close price movement
                current_day_price = float(stock_prices[i]['event']['close'])
                comparison_day_price = float(stock_prices[i-cause_timeframe]['event']['close'])
                close_price_movement = self.percentage_decrease_change(comparison_day_price,current_day_price)
                print('Current company is {}, comparing current_day_price = {} to comparison_day_price = {}, close_price_movement is {}'.format(
                    current_company,current_day_price,comparison_day_price,close_price_movement
                ))

                #If it's over the threshold, store the date
                # close_price_movement < 0 <=> negative decrease <=> increase, since we're only tackling decrease in the baseline, this date won't be relative
                if close_price_movement > 0 and close_price_movement > close_price_movement_threshold:
                    if current_company not in stock_movement_dates:
                        stock_movement_dates[current_company] = []
                    stock_movement_dates[current_company].append(stock_prices[i]['event']['time'])

        return stock_movement_dates


    def percentage_decrease_change(self, original_number: float, new_number: float):
        return (original_number-new_number)/original_number

    if __name__ == '__main__':
        print('trace')

