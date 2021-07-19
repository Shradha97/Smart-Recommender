from app.engine.trends_engine import TrendsEngine
from app.engine.time_slot_insight_engine import TimeSlotInsightEngine
from app.manager.time_slot_insight_manager import TimeSlotInsightManager


def run_time_slot_insights_job(studio_id, category):
    time_slot_insight_manager = TimeSlotInsightManager(TrendsEngine(), TimeSlotInsightEngine())
    time_slot_json_results = time_slot_insight_manager.get_time_slot_insights(studio_id, category)

    return time_slot_json_results


if __name__ == '__main__':
    studio_id = 29390
    category = 'Yoga'

    run_time_slot_insights_job(studio_id, category)
