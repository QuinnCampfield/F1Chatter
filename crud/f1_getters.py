import requests
from typing import List, Optional
from .f1_data_types import F1Session, F1Driver, F1Lap


def get_sessions(year: int = 2025, session_type: str = None, session_name: str = None, country_name: str = None) -> Optional[List[F1Session]]:
    """
    Fetch F1 sessions for a given year and return as structured data objects
    
    Args:
        year: The year to fetch sessions for (default: 2025)
        
    Returns:
        List of F1Session objects or None if request fails
    """
    link = "https://api.openf1.org/v1/sessions?"

    link += f"year={year}"
    if session_type:
        link += f"&session_type={session_type}"
    if session_name:
        link += f"&session_name={session_name}"
    if country_name:
        link += f"&country_name={country_name}"

    res = requests.get(link)
    
    sessions = None
    if res.status_code == 200:
        json_data = res.json()
        sessions = [F1Session(**session_data) for session_data in json_data]
        print(f"Retrieved {len(sessions)} sessions for {year}")
        
    else:
        print(f"Failed to fetch sessions. Status code: {res.status_code}")
    
    return sessions

def get_drivers(session_key: str = 'latest') -> Optional[List[F1Driver]]:
    """
    Fetch F1 Drivers for a given session key and return as structured data objects
    
    Args:
        session_key: The session key of the race or session (default: 'latest')
        
    Returns:
        List of F1Driver objects or None if request fails
    """
    link = f"https://api.openf1.org/v1/drivers?session_key={session_key}"

    res = requests.get(link)
    
    drivers = None
    if res.status_code == 200:
        json_data = res.json()
        # Convert JSON data to F1Driver objects
        drivers = [F1Driver(**driver_data) for driver_data in json_data]
        print(f"Retrieved {len(drivers)} drivers for session {session_key}")
        for driver in drivers[:3]:  # Print first 3 drivers
            print(f"  - {driver}")
        if len(drivers) > 3:
            print(f"  ... and {len(drivers) - 3} more drivers")
    else:
        print(f"Failed to fetch drivers. Status code: {res.status_code}")
    
    return drivers

def get_laps(session_key: str = 'latest', driver_number: int = None) -> Optional[List[F1Lap]]:
    """
    Fetch F1 laps for a given session key and return as structured data objects
    
    Args:
        session_key: The session key of the race or session (default: 'latest')
        driver_number: Optional driver number to filter laps (default: None for all drivers)
        
    Returns:
        List of F1Lap objects or None if request fails
    """
    link = f"https://api.openf1.org/v1/laps?session_key={session_key}"
    
    if driver_number:
        link += f"&driver_number={driver_number}"

    res = requests.get(link)
    
    laps = None
    if res.status_code == 200:
        json_data = res.json()
        # Convert JSON data to F1Lap objects
        laps = [F1Lap(**lap_data) for lap_data in json_data]
        print(f"Retrieved {len(laps)} laps for session {session_key}")
        for lap in laps[:3]:  # Print first 3 laps
            print(f"  - {lap}")
        if len(laps) > 3:
            print(f"  ... and {len(laps) - 3} more laps")
    else:
        print(f"Failed to fetch laps. Status code: {res.status_code}")
    
    return laps