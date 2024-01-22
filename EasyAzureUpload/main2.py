def StringChallange(string):
    times = string.split("-")
    time1, time2 = times[0], times[1]

    # Convert times to 24-hour format
    time1 = convert_to_24_hour_format(time1)
    time2 = convert_to_24_hour_format(time2)

    # Calculate the total minutes
    minutes1 = get_minutes(time1)
    minutes2 = get_minutes(time2)
    total_minutes = minutes2 - minutes1

    # Adjust for cases where the second time is smaller than the first time
    if total_minutes < 0:
        total_minutes += 24 * 60

    return total_minutes

def convert_to_24_hour_format(time):
    hour, minute = time[:-2].split(":")
    hour = int(hour)
    minute = int(minute)
    if time[-2:] == "pm" and hour != 12:
        hour += 12
    return (hour, minute)

def get_minutes(time):
    hour, minute = time
    return hour * 60 + minute
