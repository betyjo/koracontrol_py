from fastapi import APIRouter
from state import set_tag, get_tag, get_all
from event_log import get_events

router = APIRouter()

@router.post("/set_tag")
def set_tag_api(data: dict):
    tag = data["tag"]
    value = data["value"]

    set_tag(tag, value)
    return {"status": "ok", "tag": tag, "value": value}


@router.get("/get_tag/{tag}")
def get_tag_api(tag: str):
    return {
        "tag": tag,
        "value": get_tag(tag)
    }


@router.get("/state")
def all_state():
    return get_all()

@router.get("/events")
def events():
    return get_events()