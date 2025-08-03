class TimeUtils:
    @staticmethod
    def parse_time_range(time_str):
        if isinstance(time_str, str) and '-' in time_str:
            start, end = time_str.split('-')
            h1, m1 = map(int, start.split(':'))
            h2, m2 = map(int, end.split(':'))
            return h1 * 60 + m1, h2 * 60 + m2
        return None, None