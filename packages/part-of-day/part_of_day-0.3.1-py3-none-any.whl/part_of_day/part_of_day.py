from datetime import datetime, timezone
from enum import Enum

from astral import Observer
from astral.sun import sun


class PartOfDay(str, Enum):
    DAY = "Day"
    NIGHT = "Night"


class PartOfDayCalculator:
    def __init__(self, latitude, longitude) -> None:
        self.observer = Observer(latitude=latitude, longitude=longitude)

    def get_part_of_day(self, dt: datetime | None) -> PartOfDay:
        if dt is None:
            dt = datetime.now(timezone.utc)

        try:
            times_of_day = sun(self.observer, dt)
        except ValueError as e:
            if len(e.args) > 0:
                if e.args[0] == "Sun never reaches 6 degrees below the horizon, at this location.":
                    return PartOfDay.DAY
                elif e.args[0] == "Sun is always below the horizon on this day, at this location.":
                    return PartOfDay.NIGHT
            raise

        current_time = dt.time()
        if times_of_day["sunrise"].time() < times_of_day["sunset"].time():
            if times_of_day["sunrise"].time() <= current_time and current_time <= times_of_day["sunset"].time():
                return PartOfDay.DAY
            else:
                return PartOfDay.NIGHT
        else:
            if times_of_day["sunrise"].time() <= current_time or current_time <= times_of_day["sunset"].time():
                return PartOfDay.DAY
            else:
                return PartOfDay.NIGHT

    def is_it_day(self, dt: datetime | None) -> bool:
        if dt is None:
            dt = datetime.now(timezone.utc)

        return self.get_current() == PartOfDay.DAY

    def is_it_night(self, dt: datetime | None) -> bool:
        if dt is None:
            dt = datetime.now(timezone.utc)

        return not self.is_it_day(dt)
