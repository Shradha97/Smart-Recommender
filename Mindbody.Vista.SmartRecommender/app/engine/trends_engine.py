from app.settings import BOOKINGS_DATA_PATH, SEARCH_LOG_DATA_PATH
import pandas as pd
import itertools

studio_categories = []


class TrendsEngine:
    def get_hourly_booking_trends(self, studio_id, category):
        booking_df = self._get_booking_data(studio_id, category)
        booking_trend_df = self._calculate_hourly_aggregates(booking_df, 'PARENTCATEGORY', 'Classtime')
        return booking_trend_df

    def get_hourly_search_log_trends(self, category):
        search_log_df = self._get_search_log_data(category)
        search_log_trend_df = self._calculate_hourly_aggregates(search_log_df, 'CATEGORY', 'SEARCHTIME')
        return search_log_trend_df

    def _calculate_hourly_aggregates(self, df, category_col, column_name):
        trends_list = []
        df[column_name] = pd.to_datetime(df[column_name])
        print()

        for start_hour, category in itertools.product(range(5, 21), df[category_col].unique()):
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

    def _get_booking_data(self, studio_id, category):
        global studio_categories
        df = pd.read_csv(BOOKINGS_DATA_PATH)
        studio_categories = self._get_categories_offered_by_studio(df, studio_id, 'PARENTCATEGORY')
        if not category:
            common_category_data = self._get_filtered_category_data(df, 'PARENTCATEGORY')
            most_popular_category_data = self._get_most_popular_category_data(common_category_data, 'PARENTCATEGORY')
            return most_popular_category_data
        return df.loc[df['PARENTCATEGORY'] == category]

    def _get_search_log_data(self, category):
        df = pd.read_csv(SEARCH_LOG_DATA_PATH)
        if not category:
            common_category_data = self._get_filtered_category_data(df, 'CATEGORY')
            most_popular_category_data = self._get_most_popular_category_data(common_category_data, 'CATEGORY')
            return most_popular_category_data
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

    @staticmethod
    def _get_filtered_category_data(data, column_name):
        global studio_categories
        top_categories = data[column_name].unique()
        common_categories = list(set(top_categories) & set(studio_categories))
        filtered_data = data.loc[data[column_name].isin(common_categories)]
        return filtered_data

    @staticmethod
    def _get_categories_offered_by_studio(data, studio_id, column_name):
        categories = data.loc[data['StudioId'] == int(studio_id)][column_name].unique()
        return categories

    @staticmethod
    def _get_common_categories(top_categories):
        global studio_categories
        common_categories = list(set(top_categories) & set(studio_categories))
        return common_categories

    @staticmethod
    def _get_most_popular_category_data(data, column_name, n=3):
        n = max(n, len(data[column_name].unique()))
        top_categories = data[column_name].value_counts()[:n].index.tolist()
        filtered_data = data.loc[data[column_name].isin(top_categories)]
        return filtered_data
