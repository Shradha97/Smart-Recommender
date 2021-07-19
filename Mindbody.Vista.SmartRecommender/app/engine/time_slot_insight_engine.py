from numpy import trapz
import pandas as pd


class TimeSlotInsightEngine:
    def time_slot_insights(self, booking_trends_df, search_trends_df, category):
        # for category in category_list:
        ranked_time_slot_insights_df = self.get_area_between_trends(booking_trends_df, search_trends_df, category)
        return ranked_time_slot_insights_df

    def get_area_between_trends(self, booking_trends_df, search_trends_df, category):
        demand_supply_gap_approx = []
        categories = search_trends_df['Category'].unique()
        print(categories)

        for category in categories:
            for index, row in search_trends_df.iterrows():
                time_slot_start = row['Time_Slot_Start']
                time_slot_end = row['Time_Slot_End']

                booking_trend_row = booking_trends_df.loc[(booking_trends_df['Time_Slot_Start'].isin([time_slot_start,
                                                                                                      time_slot_end]))]
                search_trend_row = search_trends_df.loc[(search_trends_df['Time_Slot_Start'].isin([time_slot_start,
                                                                                                   time_slot_end]))]

                if booking_trend_row.empty:
                    booking_aggregate_pair = [0, 0]
                elif len(booking_trend_row) == 1:
                    booking_aggregate_pair = [booking_trend_row['Bookings_Aggregate'].iloc[0], 0]
                else:
                    booking_aggregate_pair = [booking_trend_row['Bookings_Aggregate'].iloc[0],
                                              booking_trend_row['Bookings_Aggregate'].iloc[1]]

                if search_trend_row.empty:
                    search_aggregate_pair = [0, 0]
                elif len(search_trend_row) == 1:
                    search_aggregate_pair = [search_trend_row['Search_Aggregate'].iloc[0], 0]
                else:
                    search_aggregate_pair = [search_trend_row['Search_Aggregate'].iloc[0],
                                             search_trend_row['Search_Aggregate'].iloc[1]]

                demand_supply_gap_area = abs(trapz(search_aggregate_pair, dx=1) -
                                             trapz(booking_aggregate_pair, dx=1))

                demand_supply_gap_approx.append(
                    (
                        category,
                        search_trend_row['Search_Aggregate'].iloc[0],
                        time_slot_start,
                        time_slot_end,
                        demand_supply_gap_area,
                    )
                )

        demand_supply_gap_approx_df = self._list_to_df(demand_supply_gap_approx)
        ranked_recommended_time_slots = self.rerank_time_slots(demand_supply_gap_approx_df)
        return ranked_recommended_time_slots

    @staticmethod
    def rerank_time_slots(time_slots_df):
        ranked_by_aggregate_and_area = time_slots_df.sort_values(['Search_Aggregate', 'Demand_Supply_Gap_Approx'],
                                                                 ascending=[False, False]).reset_index(drop=True)
        ranked_by_aggregate_and_area["Rank"] = ranked_by_aggregate_and_area.index + 1

        # dropping unnecessary columns
        ranked_by_aggregate_and_area = ranked_by_aggregate_and_area.drop(
            ['Demand_Supply_Gap_Approx']
            , axis=1)
        return ranked_by_aggregate_and_area

    @staticmethod
    def _list_to_df(required_list):
        df = pd.DataFrame(required_list,
                          columns=['Category', 'Search_Aggregate', 'Time_Slot_Start', 'Time_Slot_End',
                                   'Demand_Supply_Gap_Approx'])
        return df
