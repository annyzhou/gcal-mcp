# gcal-mcp

A Google Calendar MCP server using OAuth2 bearer token auth via the Dedalus MCP framework.

## Tools

### Calendars
- `gcal_list_calendars` - List all calendars accessible by the user
- `gcal_get_calendar` - Get details of a specific calendar
- `gcal_create_calendar` - Create a secondary calendar
- `gcal_delete_calendar` - Delete a secondary calendar
- `gcal_clear_calendar` - Clear a calendar (deletes all events)
- `gcal_patch_calendar` - Patch calendar metadata
- `gcal_update_calendar` - Update calendar metadata (full replace)

### Calendar List
- `gcal_calendarlist_get` - Get a calendar list entry
- `gcal_calendarlist_insert` - Insert an existing calendar into the user's calendar list
- `gcal_calendarlist_delete` - Remove a calendar from the user's calendar list
- `gcal_calendarlist_patch` - Patch a calendar list entry
- `gcal_calendarlist_update` - Update a calendar list entry (full replace)

### Events
- `gcal_list_events` - List events from a calendar
- `gcal_get_event` - Get a specific event by ID
- `gcal_search_events` - Search for events by text query
- `gcal_get_event_instances` - Get instances of a recurring event
- `gcal_create_event` - Create an event
- `gcal_delete_event` - Delete an event
- `gcal_patch_event` - Patch an event (partial update)
- `gcal_update_event` - Update an event (full replace)
- `gcal_quick_add_event` - Quick add an event from a text string
- `gcal_move_event` - Move an event to another calendar
- `gcal_import_event` - Import an event (creates a private copy)

### Free/Busy
- `gcal_get_freebusy` - Query free/busy information for calendars

### Settings
- `gcal_get_settings` - Get user's calendar settings
- `gcal_get_setting` - Get a specific calendar setting

### Colors
- `gcal_get_colors` - Get available calendar and event colors

### Watch (Webhooks)
- `gcal_channels_stop` - Stop watching a channel
- `gcal_events_watch` - Watch for changes to Events resources
- `gcal_calendarlist_watch` - Watch for changes to CalendarList resources
- `gcal_settings_watch` - Watch for changes to Settings resources

## Authentication

Google Calendar API requires OAuth2. The access token is provided at runtime via Dedalus credential exchange.

Required OAuth scopes:
- `https://www.googleapis.com/auth/calendar` - Full calendar access
- `https://www.googleapis.com/auth/calendar.events` - Event access

## Usage

### Prerequisites

1. A Dedalus API key (`dsk-live-*` or `dsk-test-*`)
2. The `dedalus-labs` Python SDK installed

### Environment Variables

```bash
DEDALUS_API_KEY=dsk-live-your-key-here
DEDALUS_API_URL=https://api.dedaluslabs.ai
DEDALUS_AS_URL=https://as.dedaluslabs.ai
```

### Example Client

See [`src/_client.py`](src/_client.py) for a complete example client that handles the OAuth browser flow.

The first time you use the MCP server, you'll be prompted to authorize Google Calendar access via OAuth.

### OAuth Flow

1. On first request, you'll receive an `AuthenticationError` with a `connect_url`
2. Open the URL in a browser to authorize Google Calendar access
3. After authorization, retry the request - credentials are now stored
4. Subsequent requests will work without re-authorization

## Local Development

```bash
cd gcal-mcp
uv sync
uv run python src/main.py
```

## API Reference

- [Google Calendar API Overview](https://developers.google.com/calendar/api/guides/overview)
- [Google Calendar API Reference](https://developers.google.com/calendar/api/v3/reference)
