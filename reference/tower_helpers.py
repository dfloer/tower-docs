def nice_money(n: int) -> str:
    return f"${n * 100:,.0f}"

def floor_conv(n: int) -> str:
    """
    Converts from a game-file floor number to the number displayed in game.
    So 0=B10, 10=1, 24=15, 109=100, etc.
    Args:
        n (int): Floor number to convert.
    Returns:
        str: Floor name, including B for basement/underground floors.
    """
    x = n - 10
    e = ''
    if x < 0:
        e = 'B'
        x = abs(x)
    else:
        x += 1
    return f"{e}{x}"

def floor_dbg(n) -> str:
    """Same as floor_conv, except returns both 'game_floor:save_floor', useful for debugging."""
    return f"{floor_conv(n)}:{n}"    

def day_to_str(n: int, exact: bool = True) -> str:
    """
    Converts a day counter to a string representing the in-game day.
    Args:
        n (int): Day counter.
        exact (bool): If true, displays exactly like the game does. Optional, defaults to True.
    Returns:
        str: counter and the day, quarter and year in game, or the exact in-game representation.
    """
    y = n // 12
    d = n % 3
    q = n % 12 // 3
    yy = y + 1
    if str(yy)[-1] == 1 and yy != 11:
        suffix = "st"
    elif str(yy)[-1] == 2 and yy != 11:
        suffix = "nd"
    elif str(yy)[-1] == 3 and yy != 13:
        suffix = "rd"
    else:
        suffix = "th"
    year = f"{yy}{suffix}"
    day = d % 3
    quarter = f"{q + 1}Q"
    nice_day = "WE"
    if day == 0:
        nice_day = "1st WD"
    elif day == 1:
        nice_day = "2nd WD"
    if exact:
        return f"{nice_day}/{quarter}/{year} Year"
    return f"counter {n}: day = {nice_day} ({day}), quarter = {quarter}, year = {year}"

def tick_to_time(ticks: int, am_pm: bool = True) -> str:
    """Converts a time in ticks into a clock time."""
    periods = {7: [0, 400, 45], 12: [400, 2300, 4.5], 13: [1200, 2400, 36], 1: [2400, 2600, 108]}

    for start_hour, v in periods.items():
        start_ticks, end_ticks, seconds_per_tick = v
        if start_ticks <= ticks < end_ticks:
            seconds = ticks * seconds_per_tick
            hours = seconds // 3600
            minutes = seconds // 60
    h = int(start_hour + hours) % 24
    m = int(minutes % 60)
    # print(f"ticks: {ticks}, start_hour: {start_hour}, s: {seconds}, m: {minutes} ({m}), h: {hours} ({h})")
    if am_pm:
        half = "PM" if h >= 12 else "AM"
        if h in (12, 0):
            hr = 12
        else:
            hr = h % 12
        return f"{hr}:{m:02}{half}"
    return f"{h:02}:{m:02}"

def ticks_dbg(t: int):
    """Shows tick count, and time in brackets, 12 format"""
    t2t = tick_to_time(t, True)
    return f"{t}({t2t})"