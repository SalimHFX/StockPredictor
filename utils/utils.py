from datetime import datetime, timedelta

class DateUtils():

    # Input example : date_interval = ["2020-10-01","2020-10-25"], date_format = "%Y-%m-%d"
    # Output = ["2020-10-01","2020-10-02",....,"2020-10-25"]
    @staticmethod
    def get_days_list_from_date_interval(date_interval:list,date_format:str):
        date_interval_start = datetime.strptime(date_interval[0],date_format)
        date_interval_end = datetime.strptime(date_interval[1],date_format)
        # List containing all the days of the test_boundaries interval in the date_format
        days_list = [datetime.strftime(date_interval_start + timedelta(days=x), date_format) for x in range((date_interval_end-date_interval_start).days + 1)]
        return days_list
