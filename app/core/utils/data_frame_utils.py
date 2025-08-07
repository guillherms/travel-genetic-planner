import pandas as pd

class DataFrameUtils:
    
    @staticmethod
    def concatenate_dataframe(hotel_coordinates: tuple[float, float],
                              tourist_places_df:pd.DataFrame,) -> pd.DataFrame:
        
        hotel_df = pd.DataFrame([{
            'places': 'HOTEL',
            'latitude': hotel_coordinates[0],
            'longitude': hotel_coordinates[1],
            'mon': '00:00-23:59',
            'tue': '00:00-23:59',
            'wed': '00:00-23:59',
            'thu': '00:00-23:59',
            'fri': '00:00-23:59',
            'sat': '00:00-23:59',
            'sun': '00:00-23:59',
            'estimated_duration_min': 0,
            'priority': 0
        }])
        
        return pd.concat([hotel_df, tourist_places_df], ignore_index=True)
