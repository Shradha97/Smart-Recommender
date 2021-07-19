from app.engine.trends_engine import TrendsEngine
from app.engine.time_slot_insight_engine import TimeSlotInsightEngine


class TimeSlotInsightManager:
    def __init__(
            self,
            trends_engine: TrendsEngine,
            time_slot_insight_engine: TimeSlotInsightEngine
    ):
        self.trends_engine = trends_engine
        self.time_slot_insight_engine = time_slot_insight_engine

    def get_time_slot_insights(self, studio_id, category):
        # get booking and search trends
        booking_trends_df = self.trends_engine.get_hourly_booking_trends(category)
        search_trends_df = self.trends_engine.get_hourly_search_log_trends(category)

        # get ranked time slot insights
        time_slot_insights = self.time_slot_insight_engine.time_slot_insights(booking_trends_df,
                                                                              search_trends_df,
                                                                              category)
        time_slot_insights.insert(0, 'Studio_Id', studio_id)

        # converting results to json
        json_recommendation_result = (time_slot_insights.groupby(['Category', 'Studio_Id'], as_index=False)
                                      .apply(lambda x: [x[['Time_Slot_Start', 'Time_Slot_End', 'Rank']].to_dict('records')])
                                      .rename(columns={None: 'Time_Slot_Insights'})
                                      .to_json(orient='records'))

        return json_recommendation_result
