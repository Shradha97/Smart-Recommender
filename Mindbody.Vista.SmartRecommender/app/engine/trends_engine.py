from app.settings import BOOKINGS_DATA_PATH, SEARCH_LOG_DATA_PATH
import pandas as pd


class TrendsEngine:
    def get_hourly_booking_trends(self, category):
        booking_df = self._get_booking_data(category)
        booking_trend_df = self._calculate_hourly_aggregates(booking_df, category, 'Classtime')
        return booking_trend_df

    def get_hourly_search_log_trends(self, category):
        search_log_df = self._get_search_log_data(category)
        search_log_trend_df = self._calculate_hourly_aggregates(search_log_df, category, 'SEARCHTIME')
        return search_log_trend_df

    def _calculate_hourly_aggregates(self, df, category, column_name):
        trends_list = []
        df[column_name] = pd.to_datetime(df[column_name])

        for start_hour in range(5, 21):
            aggregate_at_time_slot_df = df.loc[
                (df[column_name].dt.hour >= int(start_hour))
                & (df[column_name].dt.hour < int(start_hour) + 1)
                ]

            if not aggregate_at_time_slot_df.empty:
                trends_list.append(
                    (
                        category,
                        pd.to_datetime(int(start_hour), format='%H').time(),
                        pd.to_datetime(int(start_hour) + 1, format='%H').time(),
                        pd.to_datetime(aggregate_at_time_slot_df[column_name]).dt.time,
                        len(aggregate_at_time_slot_df),
                    )
                )
        return self._list_to_df(trends_list, column_name)
    
    @staticmethod
    def _get_booking_data(category):
        df = pd.read_csv(BOOKINGS_DATA_PATH)
        return df.loc[df['PARENTCATEGORY'] == category]

    @staticmethod
    def _get_search_log_data(category):
        df = pd.read_csv(SEARCH_LOG_DATA_PATH)
        return df.loc[df['CATEGORY'] == category]

    @staticmethod
    def _list_to_df(trends_list, time_type):
        if time_type == 'Classtime':
            aggregate_type = 'Bookings_Aggregate'
        else:
            aggregate_type = 'Search_Aggregate'

        df = pd.DataFrame(trends_list, columns=['Category', 'Time_Slot_Start', 'Time_Slot_End', time_type,
                                                aggregate_type])
        return df
