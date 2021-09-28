import time
from datetime import datetime as dt
import datetime
# from dateutil.parser import parse

class DateTimeTools():
    @staticmethod
    def get_date_no_year(split_character='-'):
        #TODO 返回當前的日期
        return dt.now().strftime(f"%m{split_character}%d")

    @staticmethod
    def get_date(split_character='-'):
        #TODO 返回當前的日期
        return dt.now().strftime(f"%Y{split_character}%m{split_character}%d")

    @staticmethod
    def get_yesterday_date():
        return (dt.now().today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    @staticmethod
    def get_specific_date(days=1):
        return (dt.now().today() - datetime.timedelta(days=days)).strftime("%m-%d")

    @staticmethod
    def get_current_year():
        return dt.now().year

    @staticmethod
    def get_datetime():
        #TODO 返回當前的日期與時分秒
        return dt.now().strftime("%Y-%m-%d-%H:%M:%S")

    @staticmethod
    def get_current_datetime():
        return dt.now()

    @staticmethod
    def get_current_date():
        return dt.now().date()

    @staticmethod
    def get_current_date_format():
        return time.strftime("%Y_%m_%d")

    @staticmethod
    def format_date(datetime_date):
        return dt.strftime(datetime_date, '%Y-%m-%d')

    @staticmethod
    def format_str_date_extra(str_date):
        format_str = f"{str(dt.date.today().year)[2:4]}/{str_date}"
        return dt.strptime(format_str, '%y/%m/%d').strftime("%Y-%m-%d")
    
    # @staticmethod
    # def format_str_date(str_date):
    #     return parse(str_date)

    @staticmethod
    def format_str_time(str_time):
        return dt.strptime(str_time, '%H/%M').strftime('%H:%M')

    @classmethod
    def get_datetime_convert_to_timestamp(cls, str_datetime):
        return dt.timestamp(dt.strptime(str_datetime, '%Y-%m-%d %H:%M:%S'))

    @staticmethod
    def convert_second_to_datetime(seconds):
        return dt.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def convert_timestamp_to_datetime(timestamp):
        # return dt.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return dt.fromtimestamp(timestamp).strftime('%Y-%m-%d')
