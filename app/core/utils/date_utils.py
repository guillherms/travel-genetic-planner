from datetime import datetime, timedelta


class DateUtils:
    @staticmethod
    def get_day_abbr(date_obj: datetime) -> str:
        return date_obj.strftime("%a").lower()

    @staticmethod
    def get_trip_days(start_date: datetime, end_date: datetime) -> int:
        return (end_date - start_date).days + 1

    @staticmethod
    def get_date_range(start_date: datetime, end_date: datetime) -> list[datetime]:
        delta = (end_date - start_date).days
        return [start_date + timedelta(days=i) for i in range(delta + 1)]