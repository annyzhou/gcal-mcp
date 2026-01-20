# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Google Calendar API tools for gcal-mcp.

Read and manage Google Calendar via the Google Calendar REST API.
Ref: https://developers.google.com/calendar/api/v3/reference
"""

from typing import Any
from urllib.parse import urlencode

from pydantic import BaseModel

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys

# -----------------------------------------------------------------------------
# Connection
# -----------------------------------------------------------------------------

gcal = Connection(
    name="gcal-mcp",  # Must match server slug for OAuth callback
    secrets=SecretKeys(token="GCAL_ACCESS_TOKEN"),
    base_url="https://www.googleapis.com/calendar/v3",
    auth_header_format="Bearer {api_key}",
)
 


class GCalResult(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


async def _request(
    method: HttpMethod,
    path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> GCalResult:
    """Make a Google Calendar API request and return result."""
    ctx = get_context()

    if params:
        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        if query_string:
            path = f"{path}?{query_string}"

    request = HttpRequest(method=method, path=path, body=body)
    response = await ctx.dispatch("gcal-mcp", request)

    if response.success:
        return GCalResult(success=True, data=response.response.body)

    msg = response.error.message if response.error else "Request failed"
    return GCalResult(success=False, error=msg)


@tool(description="List all calendars accessible by the user")
async def gcal_list_calendars() -> GCalResult:
    return await _request(
        HttpMethod.GET,
        "/users/me/calendarList",
        params={
            "minAccessRole": "reader",
        },
    )


@tool(description="Get details of a specific calendar")
async def gcal_get_calendar(calendar_id: str) -> GCalResult:
    return await _request(
        HttpMethod.GET,
        f"/calendars/{calendar_id}",
    )


@tool(description="Create a secondary calendar")
async def gcal_create_calendar(
    summary: str,
    description: str | None = None,
    time_zone: str | None = None,
    location: str | None = None,
) -> GCalResult:
    body: dict[str, Any] = {"summary": summary}
    if description is not None:
        body["description"] = description
    if time_zone is not None:
        body["timeZone"] = time_zone
    if location is not None:
        body["location"] = location

    return await _request(HttpMethod.POST, "/calendars", body=body)


@tool(description="Delete a secondary calendar")
async def gcal_delete_calendar(calendar_id: str) -> GCalResult:
    return await _request(HttpMethod.DELETE, f"/calendars/{calendar_id}")


@tool(description="Clear a calendar (deletes all events). Typically used for primary calendar.")
async def gcal_clear_calendar(calendar_id: str = "primary") -> GCalResult:
    return await _request(HttpMethod.POST, f"/calendars/{calendar_id}/clear")


@tool(description="Patch calendar metadata")
async def gcal_patch_calendar(calendar_id: str, patch: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.PATCH, f"/calendars/{calendar_id}", body=patch)


@tool(description="Update calendar metadata (full replace)")
async def gcal_update_calendar(calendar_id: str, calendar: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.PUT, f"/calendars/{calendar_id}", body=calendar)


@tool(description="Get a calendar list entry")
async def gcal_calendarlist_get(calendar_id: str) -> GCalResult:
    return await _request(HttpMethod.GET, f"/users/me/calendarList/{calendar_id}")


@tool(description="Insert an existing calendar into the user's calendar list")
async def gcal_calendarlist_insert(entry: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.POST, "/users/me/calendarList", body=entry)


@tool(description="Remove a calendar from the user's calendar list")
async def gcal_calendarlist_delete(calendar_id: str) -> GCalResult:
    return await _request(HttpMethod.DELETE, f"/users/me/calendarList/{calendar_id}")


@tool(description="Patch a calendar list entry")
async def gcal_calendarlist_patch(calendar_id: str, patch: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.PATCH, f"/users/me/calendarList/{calendar_id}", body=patch)


@tool(description="Update a calendar list entry (full replace)")
async def gcal_calendarlist_update(calendar_id: str, entry: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.PUT, f"/users/me/calendarList/{calendar_id}", body=entry)


@tool(description="Create an event")
async def gcal_create_event(
    calendar_id: str,
    event: dict[str, Any],
    send_updates: str | None = None,
    supports_attachments: bool | None = None,
) -> GCalResult:
    params: dict[str, Any] = {}
    if send_updates is not None:
        params["sendUpdates"] = send_updates
    if supports_attachments is not None:
        params["supportsAttachments"] = str(supports_attachments).lower()
    return await _request(HttpMethod.POST, f"/calendars/{calendar_id}/events", params=params, body=event)


@tool(description="Delete an event")
async def gcal_delete_event(
    calendar_id: str,
    event_id: str,
    send_updates: str | None = None,
) -> GCalResult:
    params: dict[str, Any] = {}
    if send_updates is not None:
        params["sendUpdates"] = send_updates
    return await _request(HttpMethod.DELETE, f"/calendars/{calendar_id}/events/{event_id}", params=params)


@tool(description="Patch an event (partial update)")
async def gcal_patch_event(
    calendar_id: str,
    event_id: str,
    patch: dict[str, Any],
    send_updates: str | None = None,
) -> GCalResult:
    params: dict[str, Any] = {}
    if send_updates is not None:
        params["sendUpdates"] = send_updates
    return await _request(HttpMethod.PATCH, f"/calendars/{calendar_id}/events/{event_id}", params=params, body=patch)


@tool(description="Update an event (full replace)")
async def gcal_update_event(
    calendar_id: str,
    event_id: str,
    event: dict[str, Any],
    send_updates: str | None = None,
) -> GCalResult:
    params: dict[str, Any] = {}
    if send_updates is not None:
        params["sendUpdates"] = send_updates
    return await _request(HttpMethod.PUT, f"/calendars/{calendar_id}/events/{event_id}", params=params, body=event)


@tool(description="Quick add an event from a text string")
async def gcal_quick_add_event(
    calendar_id: str,
    text: str,
    send_updates: str | None = None,
) -> GCalResult:
    params: dict[str, Any] = {"text": text}
    if send_updates is not None:
        params["sendUpdates"] = send_updates
    return await _request(HttpMethod.POST, f"/calendars/{calendar_id}/events/quickAdd", params=params)


@tool(description="Move an event to another calendar (changes organizer)")
async def gcal_move_event(
    source_calendar_id: str,
    event_id: str,
    destination_calendar_id: str,
    send_updates: str | None = None,
) -> GCalResult:
    params: dict[str, Any] = {"destination": destination_calendar_id}
    if send_updates is not None:
        params["sendUpdates"] = send_updates
    return await _request(HttpMethod.POST, f"/calendars/{source_calendar_id}/events/{event_id}/move", params=params)


@tool(description="Import an event (creates a private copy)")
async def gcal_import_event(
    calendar_id: str,
    event: dict[str, Any],
    supports_attachments: bool | None = None,
) -> GCalResult:
    params: dict[str, Any] = {}
    if supports_attachments is not None:
        params["supportsAttachments"] = str(supports_attachments).lower()
    return await _request(HttpMethod.POST, f"/calendars/{calendar_id}/events/import", params=params, body=event)


@tool(description="Stop watching a channel (channels.stop)")
async def gcal_channels_stop(channel: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.POST, "/channels/stop", body=channel)


@tool(description="Watch for changes to Events resources (requires webhook endpoint)")
async def gcal_events_watch(
    calendar_id: str,
    channel: dict[str, Any],
    time_min: str | None = None,
    time_max: str | None = None,
    single_events: bool | None = None,
) -> GCalResult:
    params: dict[str, Any] = {}
    if time_min is not None:
        params["timeMin"] = time_min
    if time_max is not None:
        params["timeMax"] = time_max
    if single_events is not None:
        params["singleEvents"] = str(single_events).lower()
    return await _request(HttpMethod.POST, f"/calendars/{calendar_id}/events/watch", params=params, body=channel)


@tool(description="Watch for changes to CalendarList resources (requires webhook endpoint)")
async def gcal_calendarlist_watch(channel: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.POST, "/users/me/calendarList/watch", body=channel)


@tool(description="Watch for changes to Settings resources (requires webhook endpoint)")
async def gcal_settings_watch(channel: dict[str, Any]) -> GCalResult:
    return await _request(HttpMethod.POST, "/users/me/settings/watch", body=channel)

@tool(description="List events from a calendar")
async def gcal_list_events(
    calendar_id: str = "primary",
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 25,
    single_events: bool = True,
    order_by: str = "startTime",
) -> GCalResult:
    max_results = max(1, min(2500, max_results))

    params: dict[str, Any] = {
        "maxResults": str(max_results),
        "singleEvents": str(single_events).lower(),
    }

    if time_min:
        params["timeMin"] = time_min
    if time_max:
        params["timeMax"] = time_max
    if single_events:
        params["orderBy"] = order_by

    return await _request(
        HttpMethod.GET,
        f"/calendars/{calendar_id}/events",
        params=params,
    )


@tool(description="Get a specific event by ID")
async def gcal_get_event(calendar_id: str, event_id: str) -> GCalResult:
    return await _request(
        HttpMethod.GET,
        f"/calendars/{calendar_id}/events/{event_id}",
    )


@tool(description="Search for events by text query")
async def gcal_search_events(
    query: str,
    calendar_id: str = "primary",
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 25,
) -> GCalResult:
    max_results = max(1, min(2500, max_results))

    params: dict[str, Any] = {
        "q": query,
        "maxResults": str(max_results),
        "singleEvents": "true",
        "orderBy": "startTime",
    }

    if time_min:
        params["timeMin"] = time_min
    if time_max:
        params["timeMax"] = time_max

    return await _request(
        HttpMethod.GET,
        f"/calendars/{calendar_id}/events",
        params=params,
    )


@tool(description="Get instances of a recurring event")
async def gcal_get_event_instances(
    calendar_id: str,
    event_id: str,
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 25,
) -> GCalResult:
    max_results = max(1, min(2500, max_results))

    params: dict[str, Any] = {
        "maxResults": str(max_results),
    }

    if time_min:
        params["timeMin"] = time_min
    if time_max:
        params["timeMax"] = time_max

    return await _request(
        HttpMethod.GET,
        f"/calendars/{calendar_id}/events/{event_id}/instances",
        params=params,
    )


@tool(description="Query free/busy information for calendars")
async def gcal_get_freebusy(
    time_min: str,
    time_max: str,
    calendar_ids: list[str] | None = None,
    time_zone: str | None = None,
) -> GCalResult:
    if calendar_ids is None:
        calendar_ids = ["primary"]

    body: dict[str, Any] = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": cal_id} for cal_id in calendar_ids],
    }

    if time_zone:
        body["timeZone"] = time_zone

    return await _request(
        HttpMethod.POST,
        "/freeBusy",
        body=body,
    )


@tool(description="Get user's calendar settings")
async def gcal_get_settings() -> GCalResult:
    return await _request(
        HttpMethod.GET,
        "/users/me/settings",
    )


@tool(description="Get a specific calendar setting")
async def gcal_get_setting(setting_id: str) -> GCalResult:
    return await _request(
        HttpMethod.GET,
        f"/users/me/settings/{setting_id}",
    )


@tool(description="Get available calendar and event colors")
async def gcal_get_colors() -> GCalResult:
    return await _request(
        HttpMethod.GET,
        "/colors",
    )


gcal_tools = [
    gcal_list_calendars,
    gcal_get_calendar,
    gcal_create_calendar,
    gcal_delete_calendar,
    gcal_clear_calendar,
    gcal_patch_calendar,
    gcal_update_calendar,
    gcal_calendarlist_get,
    gcal_calendarlist_insert,
    gcal_calendarlist_delete,
    gcal_calendarlist_patch,
    gcal_calendarlist_update,
    gcal_list_events,
    gcal_get_event,
    gcal_search_events,
    gcal_get_event_instances,
    gcal_create_event,
    gcal_delete_event,
    gcal_patch_event,
    gcal_update_event,
    gcal_quick_add_event,
    gcal_move_event,
    gcal_import_event,
    gcal_get_freebusy,
    gcal_get_settings,
    gcal_get_setting,
    gcal_settings_watch,
    gcal_get_colors,
    gcal_channels_stop,
    gcal_events_watch,
    gcal_calendarlist_watch,
]
