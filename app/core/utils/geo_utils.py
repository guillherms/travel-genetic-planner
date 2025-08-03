import math


class GeoUtils:
    @staticmethod
    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        return 2 * R * math.asin(math.sqrt(a))

    @staticmethod
    def estimated_travel_minutes(lat1, lon1, lat2, lon2, speed_kmh=30):
        distance_km = GeoUtils.haversine_km(lat1, lon1, lat2, lon2)
        return (distance_km / speed_kmh) * 60