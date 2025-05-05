from datetime import datetime, timedelta
import pandas as pd


def sla_tracker(df):
    # SLA threshold (30 days ago from today)
    sla_threshold = datetime.today() - timedelta(days=30)

    # Convert Timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

    # Flag overdue entries
    df['Overdue'] = df['Timestamp'] < sla_threshold

    return df


