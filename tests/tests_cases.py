import unittest

from models.models import CreateDaysRanges, HourOperator, RangeHour, ParseData, RangeDay, Company, RangeInside, \
    RangeContinuous, RangeMoreOneRange


class HourOperatorTest(unittest.TestCase):

    def test_should_convert_range_in_hour_zero_when_last_minute_is_one(self):
        hour_operator = HourOperator()
        hours = hour_operator.convert_range_in_hour_zero("10:01")
        self.assertEqual(hours, "10:00")

    def test_should_subtract_hour_when_receive_hour_start_and_hour_end(self):
        hour_operator = HourOperator()
        hours = hour_operator.restart_hour('10:00', "20:00")
        self.assertEqual(hours, 10)

    def test_should_subtract_even_on_different_days(self):
        hour_operator = HourOperator()
        hours = hour_operator.restart_hour('17:00', "03:00")
        self.assertEqual(hours, 10)

    def test_raise_an_exception_when_the_format_is_wrong(self):
        hour_operator = HourOperator()
        self.assertRaises(ValueError, hour_operator.restart_hour, 'a', "03:00")


class RangeHourTest(unittest.TestCase):

    def test_count_amount_hours_when_exist_start_and_end_hour(self):
        first_range_hour = RangeHour('00:00', "09:00", 25)
        second_range_hour = RangeHour('10:00', "18:00", 25)
        first_amount_hours = first_range_hour.get_amount_hours()
        second_amount_hours = second_range_hour.get_amount_hours()
        self.assertEqual(first_amount_hours, 9)
        self.assertEqual(second_amount_hours, 8)


class ParseDataTest(unittest.TestCase):

    def test_should_parse_when_receive_data(self):
        data = "IVAR=MO01:00-00:00,TH02:00-14:00,SU20:00-21:00"
        parse = ParseData()
        employee, days = parse.parse(data)
        self.assertEqual(employee, "IVAR")
        self.assertEqual(days, ["MO01:00-00:00", "TH02:00-14:00", "SU20:00-21:00"])

    def test_should_get_employee_and_days_when_receive_data(self):
        data = "IVAR=MO01:00-00:00,TH02:00-14:00,SU20:00-21:00"
        parse = ParseData()
        employee, days = parse.get_employee_and_days(data)
        self.assertEqual(employee, "IVAR")
        self.assertEqual(days, "MO01:00-00:00,TH02:00-14:00,SU20:00-21:00")


class RangeDayTest(unittest.TestCase):

    def test_should_add_hour_when_create_new_hour(self):
        create_days_range = CreateDaysRanges()
        first_range = create_days_range.validate_range('Monday', 'Friday')
        range_day = RangeDay(first_range)
        range_hour = RangeHour('00:01', '09:00', 25)
        range_day.add_hour(range_hour)
        self.assertEqual(range_day.range_hours, [range_hour])

    def test_should_order_range_hour_when_create_new_hour(self):
        create_days_range = CreateDaysRanges()
        first_range = create_days_range.validate_range('Monday', 'Friday')
        range_day = RangeDay(first_range)
        first_range_hour = RangeHour('09:01', '18:00', 25)
        second_range_hour = RangeHour('00:01', '09:00', 15)
        range_day.add_hour(first_range_hour)
        range_day.add_hour(second_range_hour)
        self.assertEqual(range_day.range_hours, [second_range_hour, first_range_hour])

    def test_should_sum_value_range_hours_when_receive_range_weekend(self):
        create_days_range = CreateDaysRanges()
        first_range = create_days_range.validate_range('Saturday', 'Sunday')
        range_day = RangeDay(first_range)
        first_range_hour = RangeHour('00:01', '09:00', 30)
        second_range_hour = RangeHour('09:01', '18:00', 20)
        thirds_range_hour = RangeHour('18:01', '00:00', 25)
        range_day.add_hour(first_range_hour)
        range_day.add_hour(second_range_hour)
        range_day.add_hour(second_range_hour)
        range_day.add_hour(thirds_range_hour)
        first_sum_value_hour = range_day.get_sum_value_range_hours("10:00", "12:00")
        second_sum_value_hour = range_day.get_sum_value_range_hours("10:00", "19:00")
        thirds_sum_value_hour = range_day.get_sum_value_range_hours("01:00", "00:00")
        self.assertEqual(first_sum_value_hour, 40)
        self.assertEqual(second_sum_value_hour, 185)
        self.assertEqual(thirds_sum_value_hour, 570)

    def test_should_sum_value_range_hours_when_receive_range_inside_weekend(self):
        create_days_range = CreateDaysRanges()
        first_range = create_days_range.validate_range('Monday', 'Friday')
        range_day = RangeDay(first_range)
        first_range_hour = RangeHour('00:01', '09:00', 25)
        second_range_hour = RangeHour('09:01', '18:00', 15)
        thirds_range_hour = RangeHour('18:01', '00:00', 20)
        range_day.add_hour(first_range_hour)
        range_day.add_hour(second_range_hour)
        range_day.add_hour(second_range_hour)
        range_day.add_hour(thirds_range_hour)
        first_sum_value_hour = range_day.get_sum_value_range_hours("10:00", "13:00")
        second_sum_value_hour = range_day.get_sum_value_range_hours("10:00", "19:00")
        thirds_sum_value_hour = range_day.get_sum_value_range_hours("01:00", "00:00")
        self.assertEqual(first_sum_value_hour, 45)
        self.assertEqual(second_sum_value_hour, 140)
        self.assertEqual(thirds_sum_value_hour, 455)

    def test_search_current_range_when_hour(self):
        create_days_range = CreateDaysRanges()
        first_range = create_days_range.validate_range('Monday', 'Friday')
        range_day = RangeDay(first_range)
        first_range_hour = RangeHour('09:01', '18:00', 25)
        second_range_hour = RangeHour('00:01', '09:00', 15)
        third_range_hour = RangeHour('18:01', '00:00', 15)
        range_day.add_hour(first_range_hour)
        range_day.add_hour(second_range_hour)
        range_day.add_hour(third_range_hour)
        current_zero = range_day.get_current_range("05:00")
        current = range_day.get_current_range("10:00")
        next_current = range_day.get_current_range("19:00")
        self.assertEqual(current_zero, 0)
        self.assertEqual(current, 1)
        self.assertEqual(next_current, 2)

    def test_should_parse_twenty_for_hour_when_receive_hour(self):
        create_days_range = CreateDaysRanges()
        first_range = create_days_range.validate_range('Monday', 'Friday')
        range_day = RangeDay(first_range)
        twenty_four = range_day.parse_twenty_for_hour("00:00")
        without_twenty_four = range_day.parse_twenty_for_hour("15:00")
        self.assertEqual(twenty_four, "24:00")
        self.assertEqual(without_twenty_four, "15:00")


class CreateDaysRangesTest(unittest.TestCase):

    def test_should_validate_range_all_days_of_week_when_day_range_is_monday_to_friday(self):
        create_day_range = CreateDaysRanges()
        days_range = create_day_range.validate_range('Monday', 'Friday')
        self.assertEqual(days_range, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])

    def test_should_validate_range_no_duplicate_range_when_repeat_same_range(self):
        create_day_range = CreateDaysRanges()
        create_day_range.validate_range('Monday', 'Friday')
        repeat_range = create_day_range.validate_range('Monday', 'Friday')
        self.assertIsNone(repeat_range)


class RangeInsideTest(unittest.TestCase):

    def test_should_calculate_values_hour_when_range_is_inside(self):
        range_inside = RangeInside()
        first_range_hour = RangeHour('00:01', '09:00', 30)
        second_range_hour = RangeHour('09:01', '18:00', 20)
        thirds_range_hour = RangeHour('18:01', '00:00', 25)
        range_hour = [first_range_hour, second_range_hour, thirds_range_hour]
        current_range = 0
        sum_value_hour = range_inside.calculate_values_hour(range_hour, current_range, "02:00", "04:00")
        current_range = 1
        second_sum_value_hour = range_inside.calculate_values_hour(range_hour, current_range, "12:00", "14:00")
        current_range = 2
        third_sum_value_hour = range_inside.calculate_values_hour(range_hour, current_range, "19:00", "21:00")
        self.assertEqual(sum_value_hour, 60)
        self.assertEqual(second_sum_value_hour, 40)
        self.assertEqual(third_sum_value_hour, 50)


class RangeContinuousTest(unittest.TestCase):

    def test_should_calculate_values_hour_when_range_is_continuos(self):
        range_continuous = RangeContinuous()
        first_range_hour = RangeHour('00:01', '09:00', 30)
        second_range_hour = RangeHour('09:01', '18:00', 20)
        thirds_range_hour = RangeHour('18:01', '00:00', 25)
        range_hour = [first_range_hour, second_range_hour, thirds_range_hour]
        current_range = 0
        sum_value_hour = range_continuous.calculate_values_hour(range_hour, current_range, "08:00", "11:00")
        current_range = 1
        second_sum_value_hour = range_continuous.calculate_values_hour(range_hour, current_range, "16:00", "20:00")
        self.assertEqual(sum_value_hour, 70)
        self.assertEqual(second_sum_value_hour, 90)


class RangeMoreOneRangeTest(unittest.TestCase):

    def test_should_calculate_values_hour_when_range_is_more_than_one(self):
        range_more_one = RangeMoreOneRange()
        first_range_hour = RangeHour('00:01', '09:00', 30)
        second_range_hour = RangeHour('09:01', '18:00', 20)
        thirds_range_hour = RangeHour('18:01', '00:00', 25)
        range_hour = [first_range_hour, second_range_hour, thirds_range_hour]
        current_range = 0
        sum_value_hour = range_more_one.calculate_values_hour(range_hour, current_range, "08:00", "21:00")
        self.assertEqual(sum_value_hour, 285)


class CompanyTest(unittest.TestCase):

    def test_should_find_day_range_when_find_day(self):
        create_day_range = CreateDaysRanges()
        first_days_range = create_day_range.validate_range('Monday', 'Friday')
        second_days_range = create_day_range.validate_range('Saturday', 'Sunday')
        first_day_range = RangeDay(first_days_range)
        second_day_range = RangeDay(second_days_range)
        company = Company('ACME', [first_day_range, second_day_range])
        day_range = company.get_day_range('MO')
        day_range_incorrect = company.get_day_range('YE')
        self.assertIsInstance(day_range, RangeDay)
        self.assertIsNone(day_range_incorrect)

