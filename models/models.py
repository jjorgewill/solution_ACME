import datetime
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
FORMAT_HOUR_MINUTES = "%H:%M"


class Possibilities(Enum):
    INSIDE = 0
    CONTINUOUS = 1
    MORE_ONE_RANGE = 2


class HourOperator:
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def restart_hour(self, start, end):
        start = self.convert_range_in_hour_zero(start)
        hour_start = datetime.datetime.strptime(start, FORMAT_HOUR_MINUTES)
        hour_end = datetime.datetime.strptime(end, FORMAT_HOUR_MINUTES)
        hours = hour_end - hour_start
        return hours.seconds//3600

    @staticmethod
    def convert_range_in_hour_zero(hour):
        hour = hour.split(":")
        return hour[0] + ":00"


class CalculateStrategy(ABC):

    @abstractmethod
    def calculate_values_hour(self, range_hours, current_range, start, end):
        pass


class RangeInside(CalculateStrategy):
    def __init__(self):
        self.hour_operator = HourOperator()

    def calculate_values_hour(self, range_hours, current_range, start, end):
        result_hours = self.hour_operator.restart_hour(start, end)
        sum_value_pay_per_hours = result_hours * range_hours[current_range].value
        return sum_value_pay_per_hours


class RangeContinuous(CalculateStrategy):
    def __init__(self):
        self.hour_operator = HourOperator()

    def calculate_values_hour(self, range_hours, current_range, start, end):
        result_hours = self.hour_operator.restart_hour(start, range_hours[current_range].end)
        sum_value_pay_per_hours = result_hours * range_hours[current_range].value
        result_hours = self.hour_operator.restart_hour(range_hours[current_range+1].start, end)
        sum_value_pay_per_hours += result_hours * range_hours[current_range+1].value
        return sum_value_pay_per_hours


class RangeMoreOneRange(CalculateStrategy):

    def __init__(self):
        self.hour_operator = HourOperator()

    def calculate_values_hour(self, range_hours, current_range, start, end):
        result_hours = self.hour_operator.restart_hour(start, range_hours[current_range].end)
        sum_value_pay_per_hours = result_hours * range_hours[current_range].value
        current_range += 1
        while len(range_hours) - 1 > current_range:
            result_hours = self.hour_operator.restart_hour(range_hours[current_range].start,
                                                           range_hours[current_range].end)
            sum_value_pay_per_hours += result_hours * range_hours[current_range].value
            current_range += 1
        result_hours = self.hour_operator.restart_hour(range_hours[current_range].start, end)
        sum_value_pay_per_hours += result_hours * range_hours[current_range].value
        return sum_value_pay_per_hours


class FactoryCalculateMethod:

    @classmethod
    def get_calculate_method(cls, calculate):
        switcher = {
          Possibilities.INSIDE.value: RangeInside(),
          Possibilities.CONTINUOUS.value: RangeContinuous(),
          Possibilities.MORE_ONE_RANGE.value: RangeMoreOneRange()
        }
        return switcher.get(calculate, Possibilities.INSIDE)


class RangeHour:

    def __init__(self, start, end, value):
        self.start = start
        self.end = end
        self.value = value

    def get_amount_hours(self):
        hour_operator = HourOperator()
        result_time = hour_operator.restart_hour(self.start, self.end)
        return result_time


class RangeDay:

    def __init__(self, range_day):
        self.range_day = range_day
        self.range_hours = list()
        self.hour_operator = HourOperator()

    def add_hour(self, hour):
        if hour not in self.range_hours:
            self.range_hours.append(hour)
            self.range_hours = sorted(self.range_hours, key=lambda hour_day: hour_day.start)

    def get_sum_value_range_hours(self, start, end):
        current_range = self.get_current_range(start)
        last_range = self.get_current_range(end)
        calculate = FactoryCalculateMethod()
        calculate_sum_hour = calculate.get_calculate_method(last_range - current_range)
        sum_value_pay_per_hours = calculate_sum_hour.calculate_values_hour(self.range_hours, current_range, start, end)
        return sum_value_pay_per_hours

    def get_current_range(self, hour_search):
        hour_search = self.parse_twenty_for_hour(hour_search)
        find = 0
        for current_range in self.range_hours:
            hour_end = self.parse_twenty_for_hour(current_range.end)
            if current_range.start <= hour_search <= hour_end:
                return find
            find += 1

    @staticmethod
    def parse_twenty_for_hour(current_hour):
        return "24:00" if current_hour == "00:00" else current_hour


class ParseData:

    def parse(self, data):
        employee, days = self.get_employee(data)
        return employee, days.split(",")

    @staticmethod
    def get_employee(data):
        employ = data.split("=")
        return employ[0], employ[1]


class Company:

    def __init__(self, name, day_ranges):
        self.name = name
        self.day_ranges = day_ranges

    def get_day_range(self, day_find):
        for day_range in self.day_ranges:
            for day in day_range.range_day:
                if day.upper().startswith(day_find):
                    return day_range
        return None


class CreateDaysRanges:

    def __init__(self):
        self.ranges_days = list()

    def validate_range(self, start, end):
        range_days = DAYS[DAYS.index(start):DAYS.index(end)+1]
        if range_days not in self.ranges_days:
            self.ranges_days.append(range_days)
            return range_days
        return None


class PayCalculator:

    def __init__(self, company):
        self.parse_data = ParseData()
        self.company = company

    def calculate_payments(self, data):
        employ, days = self.parse_data.parse(data)
        pays_for_employee = {'employee': employ, "pay_total": 0}
        for row in days:
            day_find = row[:2]
            hours = row[2:].split("-")
            day_range = self.company.get_day_range(day_find)
            value_to_pay = day_range.get_sum_value_range_hours(hours[0], hours[1])
            pays_for_employee["pay_total"] += value_to_pay
        return pays_for_employee


class ReadFile:

    @staticmethod
    def read(path):
        file = open(path, 'r')
        lines = file.read().splitlines()
        file.close()
        return lines
