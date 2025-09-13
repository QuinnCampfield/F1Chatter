from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class F1Session:
    """Class representing an F1 session"""

    meeting_key: int
    session_key: int
    location: str
    date_start: str
    date_end: str
    session_type: str
    session_name: str
    country_key: int
    country_code: str
    country_name: str
    circuit_key: int
    circuit_short_name: str
    gmt_offset: str
    year: int

    def get_start_datetime(self) -> datetime:
        return datetime.fromisoformat(self.date_start.replace("Z", "+00:00"))

    def get_end_datetime(self) -> datetime:
        return datetime.fromisoformat(self.date_end.replace("Z", "+00:00"))

    def __str__(self) -> str:
        return f"{self.session_name} - {self.location} ({self.session_type}) - {self.date_start}"


@dataclass
class F1Driver:
    """Class representing an F1 driver"""

    meeting_key: int
    session_key: int
    driver_number: int
    broadcast_name: str
    full_name: str
    name_acronym: str
    team_name: str
    team_colour: str
    first_name: str
    last_name: str
    headshot_url: str
    country_code: Optional[str]

    def get_team_colour_hex(self) -> str:
        """Return team colour as a proper hex color code"""
        return f"#{self.team_colour}"

    def get_display_name(self) -> str:
        """Return a formatted display name"""
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"#{self.driver_number} {self.full_name} ({self.name_acronym}) - {self.team_name}"


@dataclass
class F1Lap:
    """Class representing an F1 lap"""

    meeting_key: int
    session_key: int
    driver_number: int
    lap_number: int
    date_start: Optional[str]
    duration_sector_1: Optional[float]
    duration_sector_2: Optional[float]
    duration_sector_3: Optional[float]
    i1_speed: Optional[int]
    i2_speed: Optional[int]
    is_pit_out_lap: bool
    lap_duration: Optional[float]
    segments_sector_1: List[Optional[int]]
    segments_sector_2: List[Optional[int]]
    segments_sector_3: List[Optional[int]]
    st_speed: Optional[int]

    def get_start_datetime(self) -> Optional[datetime]:
        """Return the lap start time as a datetime object"""
        if self.date_start:
            return datetime.fromisoformat(self.date_start.replace("Z", "+00:00"))
        return None

    def get_total_lap_time(self) -> Optional[float]:
        """Return the total lap duration in seconds"""
        return self.lap_duration

    def get_sector_times(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Return sector times as a tuple (sector_1, sector_2, sector_3)"""
        return (self.duration_sector_1, self.duration_sector_2, self.duration_sector_3)

    def get_speeds(self) -> tuple[Optional[int], Optional[int], Optional[int]]:
        """Return speeds as a tuple (i1_speed, i2_speed, st_speed)"""
        return (self.i1_speed, self.i2_speed, self.st_speed)

    def is_complete_lap(self) -> bool:
        """Check if this is a complete lap with all sector times"""
        return all(
            time is not None
            for time in [
                self.duration_sector_1,
                self.duration_sector_2,
                self.duration_sector_3,
            ]
        )

    def get_average_speed(self) -> Optional[float]:
        """Calculate average speed from available speed measurements"""
        speeds = [
            speed
            for speed in [self.i1_speed, self.i2_speed, self.st_speed]
            if speed is not None
        ]
        return sum(speeds) / len(speeds) if speeds else None

    def __str__(self) -> str:
        lap_time_str = f"{self.lap_duration:.3f}s" if self.lap_duration else "N/A"
        return f"Lap #{self.lap_number} - Driver #{self.driver_number} - {lap_time_str}"
