import traceback

from models.models import CreateDaysRanges, RangeHour, RangeDay, Company, PayCalculator, ReadFile


def create_ranges_days_and_hours():
    create_days_range = CreateDaysRanges()
    first_range = create_days_range.validate_range('Monday', 'Friday')
    second_range = create_days_range.validate_range('Saturday', 'Sunday')

    first_day_one_hour_interval = RangeHour('00:01', '09:00', 25)
    first_day_second_hour_interval = RangeHour('09:01', '18:00', 15)
    first_day_third_hour_interval = RangeHour('18:01', '00:00', 20)
    second_day_one_hour_interval = RangeHour('00:01', '09:00', 30)
    second_day_second_hour_interval = RangeHour('09:01', '18:00', 20)
    second_day_third_hour_interval = RangeHour('18:01', '00:00', 25)

    first_day_range = RangeDay(first_range)
    first_day_range.add_hour(first_day_one_hour_interval)
    first_day_range.add_hour(first_day_second_hour_interval)
    first_day_range.add_hour(first_day_third_hour_interval)

    second_day_range = RangeDay(second_range)
    second_day_range.add_hour(second_day_one_hour_interval)
    second_day_range.add_hour(second_day_second_hour_interval)
    second_day_range.add_hour(second_day_third_hour_interval)
    return [first_day_range, second_day_range]


def create_company():
    days_ranges = create_ranges_days_and_hours()
    company = Company('ACME', days_ranges)
    return company


def extract_to_data():
    file = ReadFile()
    data = file.read('data.txt')
    return data


def main():
    data = extract_to_data()
    company = create_company()
    payment_calculator = PayCalculator(company)
    for row in data:
        try:
            payments_for_employee = payment_calculator.calculate_payments(row)
            print(f'The amount to pay {payments_for_employee["employee"]} is: {payments_for_employee["pay_total"]} USD')
        except Exception as e:
            print(f'ERROR read data from row {row}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e))
