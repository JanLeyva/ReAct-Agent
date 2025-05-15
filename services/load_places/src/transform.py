import polars as pl

data = pl.read_parquet(
    "/Users/esengineer/Documents/_dev/whatsapp-agent/services/load_places/250515_places.parquet"
)

# Clean closed places
data = data.filter(pl.col("business_status").is_in(["OPERATIONAL", None]))

# Filter just barcelona places
data = data.filter(data["formatted_address"].str.contains("Barcelona"))

# Keep just restaurants
data = data.filter(pl.col("types").list.contains("restaurant"))

def parse_time_range(time_str: str):
    # clean
    time_str = time_str.replace("\u2009", "")
    time_str = time_str.replace("\u202f", "")
    times = []
    for part in time_str.split(", "):
        if "–" in part:
            start_str, end_str = part.split("–")
            times.append((start_str, end_str))
        else:
            times.append(part)
    return times


def convert_time(time):
    formatted_schedule = {}
    for t in time:
        parts = t.split(": ")
        day = parts[0]
        hours_str = parts[1] if len(parts) > 1 else ""
        if hours_str.lower() == "closed":
            formatted_schedule[day] = "Closed"
        else:
            formatted_schedule[day] = parse_time_range(hours_str)

    return formatted_schedule


time_week = []
for weekday in data.select(pl.col("weekday_text")).iter_rows():
    if weekday[0]:
        time_week.append(convert_time(weekday[0]))
    else:
        time_week.append(None)

data.insert_column(29, pl.Series("time_week", time_week, strict=False))

