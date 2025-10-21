from fastapi import APIRouter
from typing import List, Union, Dict
from .models import Event
from .file_storage import EventFileManager
from .event_analyzer import EventAnalyzer



router = APIRouter()

@router.get("", summary="Get All Events", response_model=List[Event])
def get_all_events():
    return EventFileManager.read_events_from_file()


@router.post("", summary="Create Event", response_model=Event, status_code=201)
def create_event(event: Event):
    #  Read current events from file
    events = EventFileManager.read_events_from_file()

    #  Check for duplicate ID
    if any(ev.get("id") == event.id for ev in events):
        raise HTTPException(status_code=400, detail="Event ID already exists")

    # Add the new event
    events.append(event.model_dump() if hasattr(event, "model_dump") else event.dict())

    # Write updated list to file
    EventFileManager.write_events_to_file(events)

    # Return the created event
    return event

@router.get("/filter", summary="Filter Events", response_model=List[Event])
def get_events_by_filter(
    date: str = None,
    organizer: str = None,
    status: str = None,
    event_type: str = None
):
    #  Read all events from file
    events = EventFileManager.read_events_from_file()

    # Apply filters one by one if provided
    filtered = []
    for ev in events:
        if date and ev.get("date") != date:
            continue
        if organizer:
            # organizer is nested; check name or email
            org = ev.get("organizer", {})
            if organizer.lower() not in str(org.get("name", "")).lower() \
               and organizer.lower() not in str(org.get("email", "")).lower():
                continue
        if status and ev.get("status", "").lower() != status.lower():
            continue
        if event_type and ev.get("type", "").lower() != event_type.lower():
            continue
        filtered.append(ev)

    return filtered


@router.get("/{event_id}", summary="Get Event By Id", response_model=Event)
def get_event_by_id(event_id: int):
    events = EventFileManager.read_events_from_file()
    for ev in events:
        if ev.get("id") == event_id:
            return ev
    # If not found, return a 404
    raise HTTPException(status_code=404, detail="Event not found")

@router.put("/{event_id}", summary="Update Event", response_model=Event)
def update_event(event_id: int, new_event: Event):
    # 1) Read existing events
    events = EventFileManager.read_events_from_file()

    # 2) Find the event by ID
    for i, ev in enumerate(events):
        if ev.get("id") == event_id:
            # 3) Make the path param authoritative
            #    (ignore/override any 'id' inside the body)
            payload = new_event.model_dump() if hasattr(new_event, "model_dump") else new_event.dict()
            payload["id"] = event_id

            # 4) Replace and persist
            events[i] = payload
            EventFileManager.write_events_to_file(events)
            return payload

    # 5) Not found → 404
    raise HTTPException(status_code=404, detail="Event Not found")

@router.delete("/{event_id}", summary="Delete Event")
def delete_event(event_id: int):
    # 1) Read current events
    events = EventFileManager.read_events_from_file()

    # 2) Remove the one with matching id
    new_events = [ev for ev in events if ev.get("id") != event_id]

    # 3) If nothing was removed -> 404
    if len(new_events) == len(events):
        raise HTTPException(status_code=404, detail="Event Not found")

    # 4) Persist the updated list
    EventFileManager.write_events_to_file(new_events)

    # 5) Return success message
    return {"message": "Event deleted successfully"}

from typing import List, Union, Dict  # make sure this line exists at the top
from .file_storage import EventFileManager
from .event_analyzer import EventAnalyzer


from typing import List, Union, Dict  # make sure this line exists at the top
from .file_storage import EventFileManager
from .event_analyzer import EventAnalyzer


@router.get(
    "/joiners/multiple-meetings",
    summary="Get Joiners Multiple Meetings",
    response_model=Union[List[str], Dict[str, str]],
)
def get_joiners_multiple_meetings():
    # Initialize analyzer instance
    analyzer = EventAnalyzer()

    events = EventFileManager.read_events_from_file()
    joiners = analyzer.get_joiners_multiple_meetings_method(events)

    if not joiners:
        return {"message": "No joiners attending at least 2 meetings"}

    return joiners
