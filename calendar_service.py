from datetime import date, timedelta

import pandas as pd

COLUMNS = ["Date", "Platform", "Status", "Caption"]


def build_calendar(ideas, start_date=None, platforms=None, days_between=1, **kwargs):
    """Turn a list of post ideas into a content calendar DataFrame.

    ideas: list of strings, or list of dicts with keys like
           'caption' / 'idea' / 'title' / 'platform'.
    """
    start = start_date or date.today()
    if hasattr(start, "date") and not isinstance(start, date):
        start = start.date()
    platforms = platforms or ["Instagram"]
    if isinstance(platforms, str):
        platforms = [platforms]

    rows = []
    for i, idea in enumerate(ideas or []):
        if isinstance(idea, dict):
            caption = (
                idea.get("caption")
                or idea.get("idea")
                or idea.get("title")
                or idea.get("text")
                or ""
            )
            platform = idea.get("platform") or platforms[i % len(platforms)]
        else:
            caption = str(idea)
            platform = platforms[i % len(platforms)]

        rows.append(
            {
                "Date": start + timedelta(days=i * days_between),
                "Platform": platform,
                "Status": "Draft",
                "Caption": caption,
            }
        )

    return pd.DataFrame(rows, columns=COLUMNS)


def calendar_to_csv(df):
    """Convert the calendar DataFrame to CSV bytes for st.download_button."""
    return df.to_csv(index=False).encode("utf-8")