"""
Google Calendar MCP Tools - Updated for Access Token Authentication

This module provides MCP tools for interacting with Google Calendar API using access token auth.
"""

import datetime
import logging
import asyncio
import re
from typing import List, Optional, Dict, Any

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from auth.token_auth import get_authenticated_google_service, GoogleAuthenticationError
from core.session_server import register_tool_with_transport
from core.utils import handle_http_errors

# Configure module logger
logger = logging.getLogger(__name__)

# Required scopes for Calendar operations
CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events"
]


# Helper function to ensure time strings for API calls are correctly formatted
def _correct_time_format_for_api(
    time_str: Optional[str], param_name: str
) -> Optional[str]:
    if not time_str:
        return None

    logger.info(
        f"_correct_time_format_for_api: Processing {param_name} with value '{time_str}'"
    )

    # Handle date-only format (YYYY-MM-DD)
    if len(time_str) == 10 and time_str.count("-") == 2:
        try:
            # Validate it's a proper date
            datetime.datetime.strptime(time_str, "%Y-%m-%d")
            # For date-only, append T00:00:00Z to make it RFC3339 compliant
            formatted = f"{time_str}T00:00:00Z"
            logger.info(
                f"Formatting date-only {param_name} '{time_str}' to RFC3339: '{formatted}'"
            )
            return formatted
        except ValueError:
            logger.warning(
                f"{param_name} '{time_str}' looks like a date but is not valid YYYY-MM-DD. Using as is."
            )
            return time_str

    # Specifically address YYYY-MM-DDTHH:MM:SS by appending 'Z'
    if (
        len(time_str) == 19
        and time_str[10] == "T"
        and time_str.count(":") == 2
        and not (
            time_str.endswith("Z") or ("+" in time_str[10:]) or ("-" in time_str[10:])
        )
    ):
        try:
            # Validate the format before appending 'Z'
            datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
            logger.info(
                f"Formatting {param_name} '{time_str}' by appending 'Z' for UTC."
            )
            return time_str + "Z"
        except ValueError:
            logger.warning(
                f"{param_name} '{time_str}' looks like it needs 'Z' but is not valid YYYY-MM-DDTHH:MM:SS. Using as is."
            )
            return time_str

    # If it already has timezone info or doesn't match our patterns, return as is
    logger.info(f"{param_name} '{time_str}' doesn't need formatting, using as is.")
    return time_str


@handle_http_errors("list_calendars", is_read_only=True)
async def list_calendars() -> str:
    """
    Retrieves a list of calendars accessible to the authenticated user.

    Returns:
        str: A formatted list of the user's calendars (summary, ID, primary status).
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "list_calendars")
        
        logger.info(f"[list_calendars] Invoked")

        calendar_list_response = await asyncio.to_thread(
            lambda: service.calendarList().list().execute()
        )
        items = calendar_list_response.get("items", [])
        if not items:
            return "No calendars found."

        calendars_summary_list = [
            f"- \"{cal.get('summary', 'No Summary')}\"{' (Primary)' if cal.get('primary') else ''} (ID: {cal['id']})"
            for cal in items
        ]
        text_output = (
            f"Successfully listed {len(items)} calendars:\n"
            + "\n".join(calendars_summary_list)
        )
        logger.info(f"Successfully listed {len(items)} calendars.")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error listing calendars: {e}")
        return f"Error listing calendars: {str(e)}"


@handle_http_errors("get_events", is_read_only=True)
async def get_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 25,
) -> str:
    """
    Retrieves a list of events from a specified Google Calendar within a given time range.

    Args:
        calendar_id (str): The ID of the calendar to query. Use 'primary' for the user's primary calendar. Defaults to 'primary'. Calendar IDs can be obtained using `list_calendars`.
        time_min (Optional[str]): The start of the time range (inclusive) in RFC3339 format (e.g., '2024-05-12T10:00:00Z' or '2024-05-12'). If omitted, defaults to the current time.
        time_max (Optional[str]): The end of the time range (exclusive) in RFC3339 format. If omitted, events starting from `time_min` onwards are considered (up to `max_results`).
        max_results (int): The maximum number of events to return. Defaults to 25.

    Returns:
        str: A formatted list of events (summary, start and end times, link) within the specified range.
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "get_events")
        
        logger.info(
            f"[get_events] Raw time parameters - time_min: '{time_min}', time_max: '{time_max}'"
        )

        # Ensure time_min and time_max are correctly formatted for the API
        formatted_time_min = _correct_time_format_for_api(time_min, "time_min")
        effective_time_min = formatted_time_min or (
            datetime.datetime.utcnow().isoformat() + "Z"
        )
        if time_min is None:
            logger.info(
                f"time_min not provided, defaulting to current UTC time: {effective_time_min}"
            )
        else:
            logger.info(
                f"time_min processing: original='{time_min}', formatted='{formatted_time_min}', effective='{effective_time_min}'"
            )

        effective_time_max = _correct_time_format_for_api(time_max, "time_max")
        if time_max:
            logger.info(
                f"time_max processing: original='{time_max}', formatted='{effective_time_max}'"
            )

        logger.info(
            f"[get_events] Final API parameters - calendarId: '{calendar_id}', timeMin: '{effective_time_min}', timeMax: '{effective_time_max}', maxResults: {max_results}"
        )

        events_result = await asyncio.to_thread(
            lambda: service.events()
            .list(
                calendarId=calendar_id,
                timeMin=effective_time_min,
                timeMax=effective_time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        items = events_result.get("items", [])
        if not items:
            return f"No events found in calendar '{calendar_id}' for the specified time range."

        event_details_list = []
        for item in items:
            summary = item.get("summary", "No Title")
            start_time = item["start"].get("dateTime", item["start"].get("date"))
            end_time = item["end"].get("dateTime", item["end"].get("date"))
            link = item.get("htmlLink", "No Link")
            event_id = item.get("id", "No ID")
            # Include the start/end date, and event ID in the output so users can copy it for modify/delete operations
            event_details_list.append(
                f'- "{summary}" (Starts: {start_time}, Ends: {end_time}) ID: {event_id} | Link: {link}'
            )

        text_output = (
            f"Successfully retrieved {len(items)} events from calendar '{calendar_id}':\n"
            + "\n".join(event_details_list)
        )
        logger.info(f"Successfully retrieved {len(items)} events.")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return f"Error getting events: {str(e)}"


@handle_http_errors("create_event", is_read_only=False)
async def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    timezone: Optional[str] = None,
    attachments: Optional[List[str]] = None,
) -> str:
    """
    Creates a new event.

    Args:
        summary (str): Event title.
        start_time (str): Start time (RFC3339, e.g., "2023-10-27T10:00:00-07:00" or "2023-10-27" for all-day).
        end_time (str): End time (RFC3339, e.g., "2023-10-27T11:00:00-07:00" or "2023-10-28" for all-day).
        calendar_id (str): Calendar ID (default: 'primary').
        description (Optional[str]): Event description.
        location (Optional[str]): Event location.
        attendees (Optional[List[str]]): Attendee email addresses.
        timezone (Optional[str]): Timezone (e.g., "America/New_York").
        attachments (Optional[List[str]]): List of Google Drive file URLs or IDs to attach to the event.

    Returns:
        str: Confirmation message of the successful event creation with event link.
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "create_event")
        
        logger.info(f"[create_event] Invoked. Summary: {summary}")
        logger.info(f"[create_event] Incoming attachments param: {attachments}")
        
        # If attachments value is a string, split by comma and strip whitespace
        if attachments and isinstance(attachments, str):
            attachments = [a.strip() for a in attachments.split(',') if a.strip()]
            logger.info(f"[create_event] Parsed attachments list from string: {attachments}")
            
        event_body: Dict[str, Any] = {
            "summary": summary,
            "start": (
                {"date": start_time}
                if "T" not in start_time
                else {"dateTime": start_time}
            ),
            "end": (
                {"date": end_time} if "T" not in end_time else {"dateTime": end_time}
            ),
        }
        if location:
            event_body["location"] = location
        if description:
            event_body["description"] = description
        if timezone:
            if "dateTime" in event_body["start"]:
                event_body["start"]["timeZone"] = timezone
            if "dateTime" in event_body["end"]:
                event_body["end"]["timeZone"] = timezone
        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        if attachments:
            # Accept both file URLs and file IDs. If a URL, extract the fileId.
            event_body["attachments"] = []
            drive_service = None
            try:
                drive_service = service._http and build("drive", "v3", http=service._http)
            except Exception as e:
                logger.warning(f"Could not build Drive service for MIME type lookup: {e}")
            for att in attachments:
                file_id = None
                if att.startswith("https://"):
                    # Match /d/<id>, /file/d/<id>, ?id=<id>
                    match = re.search(r"(?:/d/|/file/d/|id=)([\w-]+)", att)
                    file_id = match.group(1) if match else None
                    logger.info(f"[create_event] Extracted file_id '{file_id}' from attachment URL '{att}'")
                else:
                    file_id = att
                    logger.info(f"[create_event] Using direct file_id '{file_id}' for attachment")
                if file_id:
                    file_url = f"https://drive.google.com/open?id={file_id}"
                    mime_type = "application/vnd.google-apps.drive-sdk"
                    title = "Drive Attachment"
                    # Try to get the actual MIME type and filename from Drive
                    if drive_service:
                        try:
                            file_metadata = await asyncio.to_thread(
                                lambda: drive_service.files().get(fileId=file_id, fields="mimeType,name").execute()
                            )
                            mime_type = file_metadata.get("mimeType", mime_type)
                            filename = file_metadata.get("name")
                            if filename:
                                title = filename
                                logger.info(f"[create_event] Using filename '{filename}' as attachment title")
                            else:
                                logger.info("[create_event] No filename found, using generic title")
                        except Exception as e:
                            logger.warning(f"Could not fetch metadata for file {file_id}: {e}")
                    event_body["attachments"].append({
                        "fileUrl": file_url,
                        "title": title,
                        "mimeType": mime_type,
                    })
            created_event = await asyncio.to_thread(
                lambda: service.events().insert(
                    calendarId=calendar_id, body=event_body, supportsAttachments=True
                ).execute()
            )
        else:
            created_event = await asyncio.to_thread(
                lambda: service.events().insert(calendarId=calendar_id, body=event_body).execute()
            )
        link = created_event.get("htmlLink", "No link available")
        confirmation_message = f"Successfully created event '{created_event.get('summary', summary)}'. Link: {link}"
        logger.info(
                f"Event created successfully. ID: {created_event.get('id')}, Link: {link}"
            )
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return f"Error creating event: {str(e)}"


@handle_http_errors("modify_event", is_read_only=False)
async def modify_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    timezone: Optional[str] = None,
) -> str:
    """
    Modifies an existing event.

    Args:
        event_id (str): The ID of the event to modify.
        calendar_id (str): Calendar ID (default: 'primary').
        summary (Optional[str]): New event title.
        start_time (Optional[str]): New start time (RFC3339, e.g., "2023-10-27T10:00:00-07:00" or "2023-10-27" for all-day).
        end_time (Optional[str]): New end time (RFC3339, e.g., "2023-10-27T11:00:00-07:00" or "2023-10-28" for all-day).
        description (Optional[str]): New event description.
        location (Optional[str]): New event location.
        attendees (Optional[List[str]]): New attendee email addresses.
        timezone (Optional[str]): New timezone (e.g., "America/New_York").

    Returns:
        str: Confirmation message of the successful event modification with event link.
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "modify_event")
        
        logger.info(f"[modify_event] Invoked. Event ID: {event_id}")

        # Build the event body with only the fields that are provided
        event_body: Dict[str, Any] = {}
        if summary is not None:
            event_body["summary"] = summary
        if start_time is not None:
            event_body["start"] = (
                {"date": start_time}
                if "T" not in start_time
                else {"dateTime": start_time}
            )
            if timezone is not None and "dateTime" in event_body["start"]:
                event_body["start"]["timeZone"] = timezone
        if end_time is not None:
            event_body["end"] = (
                {"date": end_time} if "T" not in end_time else {"dateTime": end_time}
            )
            if timezone is not None and "dateTime" in event_body["end"]:
                event_body["end"]["timeZone"] = timezone
        if description is not None:
            event_body["description"] = description
        if location is not None:
            event_body["location"] = location
        if attendees is not None:
            event_body["attendees"] = [{"email": email} for email in attendees]
        if (
            timezone is not None
            and "start" not in event_body
            and "end" not in event_body
        ):
            # If timezone is provided but start/end times are not, we need to fetch the existing event
            # to apply the timezone correctly. This is a simplification; a full implementation
            # might handle this more robustly or require start/end with timezone.
            # For now, we'll log a warning and skip applying timezone if start/end are missing.
            logger.warning(
                "[modify_event] Timezone provided but start_time and end_time are missing. Timezone will not be applied unless start/end times are also provided."
            )

        if not event_body:
            message = "No fields provided to modify the event."
            logger.warning(f"[modify_event] {message}")
            raise Exception(message)

        # Log the event ID for debugging
        logger.info(
            f"[modify_event] Attempting to update event with ID: '{event_id}' in calendar '{calendar_id}'"
        )

        # Try to get the event first to verify it exists
        try:
            await asyncio.to_thread(
                lambda: service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )
            logger.info(
                "[modify_event] Successfully verified event exists before update"
            )
        except HttpError as get_error:
            if get_error.resp.status == 404:
                logger.error(
                    f"[modify_event] Event not found during pre-update verification: {get_error}"
                )
                message = f"Event not found during verification. The event with ID '{event_id}' could not be found in calendar '{calendar_id}'. This may be due to incorrect ID format or the event no longer exists."
                raise Exception(message)
            else:
                logger.warning(
                    f"[modify_event] Error during pre-update verification, but proceeding with update: {get_error}"
                )

        # Proceed with the update
        updated_event = await asyncio.to_thread(
            lambda: service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event_body)
            .execute()
        )

        link = updated_event.get("htmlLink", "No link available")
        confirmation_message = f"Successfully modified event '{updated_event.get('summary', summary)}' (ID: {event_id}). Link: {link}"
        logger.info(
            f"Event modified successfully. ID: {updated_event.get('id')}, Link: {link}"
        )
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error modifying event: {e}")
        return f"Error modifying event: {str(e)}"


@handle_http_errors("delete_event", is_read_only=False)
async def delete_event(event_id: str, calendar_id: str = "primary") -> str:
    """
    Deletes an existing event.

    Args:
        event_id (str): The ID of the event to delete.
        calendar_id (str): Calendar ID (default: 'primary').

    Returns:
        str: Confirmation message of the successful event deletion.
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "delete_event")
        
        logger.info(f"[delete_event] Invoked. Event ID: {event_id}")

        # Log the event ID for debugging
        logger.info(
            f"[delete_event] Attempting to delete event with ID: '{event_id}' in calendar '{calendar_id}'"
        )

        # Try to get the event first to verify it exists
        try:
            await asyncio.to_thread(
                lambda: service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )
            logger.info(
                "[delete_event] Successfully verified event exists before deletion"
            )
        except HttpError as get_error:
            if get_error.resp.status == 404:
                logger.error(
                    f"[delete_event] Event not found during pre-delete verification: {get_error}"
                )
                message = f"Event not found during verification. The event with ID '{event_id}' could not be found in calendar '{calendar_id}'. This may be due to incorrect ID format or the event no longer exists."
                raise Exception(message)
            else:
                logger.warning(
                    f"[delete_event] Error during pre-delete verification, but proceeding with deletion: {get_error}"
                )

        # Proceed with the deletion
        await asyncio.to_thread(
            lambda: service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        )

        confirmation_message = f"Successfully deleted event (ID: {event_id}) from calendar '{calendar_id}'."
        logger.info(f"Event deleted successfully. ID: {event_id}")
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return f"Error deleting event: {str(e)}"


@handle_http_errors("filter_events_by_date_range", is_read_only=True)
async def filter_events_by_date_range(
    start_date: str,
    end_date: str,
    calendar_id: str = "primary",
    keyword: Optional[str] = None,
    max_results: int = 50,
    include_all_day: bool = True,
) -> str:
    """
    Filters events within a specific date range with optional keyword search.

    This tool provides enhanced filtering capabilities specifically for date range queries,
    with additional options for keyword filtering and all-day event inclusion.

    Args:
        start_date (str): Start of date range (YYYY-MM-DD or RFC3339 format, e.g., '2024-05-12' or '2024-05-12T10:00:00Z').
        end_date (str): End of date range (YYYY-MM-DD or RFC3339 format, e.g., '2024-05-20' or '2024-05-20T18:00:00Z').
        calendar_id (str): The ID of the calendar to query. Defaults to 'primary'.
        keyword (Optional[str]): Filter events by keyword in title or description.
        max_results (int): Maximum number of events to return. Defaults to 50.
        include_all_day (bool): Whether to include all-day events. Defaults to True.

    Returns:
        str: A formatted list of filtered events within the specified date range.
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "filter_events_by_date_range")

        logger.info(f"[filter_events_by_date_range] Filtering events from {start_date} to {end_date}")

        # Format the date range for API
        formatted_start = _correct_time_format_for_api(start_date, "start_date")
        formatted_end = _correct_time_format_for_api(end_date, "end_date")

        # If end_date is date-only, set it to end of day to be inclusive
        if len(end_date) == 10 and end_date.count("-") == 2:
            try:
                datetime.datetime.strptime(end_date, "%Y-%m-%d")
                formatted_end = f"{end_date}T23:59:59Z"
                logger.info(f"Converting end_date to end of day: {formatted_end}")
            except ValueError:
                pass

        logger.info(f"[filter_events_by_date_range] API call with timeMin: {formatted_start}, timeMax: {formatted_end}")

        events_result = await asyncio.to_thread(
            lambda: service.events()
            .list(
                calendarId=calendar_id,
                timeMin=formatted_start,
                timeMax=formatted_end,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        items = events_result.get("items", [])
        if not items:
            return f"No events found in calendar '{calendar_id}' between {start_date} and {end_date}."

        # Apply additional filtering
        filtered_events = []
        for item in items:
            summary = item.get("summary", "No Title")
            description = item.get("description", "")
            start_time = item["start"].get("dateTime", item["start"].get("date"))
            end_time = item["end"].get("dateTime", item["end"].get("date"))

            # Filter all-day events if requested
            if not include_all_day and "T" not in start_time:
                continue

            # Filter by keyword if provided
            if keyword and keyword.lower() not in summary.lower() and keyword.lower() not in description.lower():
                continue

            link = item.get("htmlLink", "No Link")
            event_id = item.get("id", "No ID")
            location = item.get("location", "")

            event_type = "All-day" if "T" not in start_time else "Timed"
            location_str = f" | Location: {location}" if location else ""

            filtered_events.append(
                f'- "{summary}" ({event_type}) (Starts: {start_time}, Ends: {end_time}){location_str} | ID: {event_id} | Link: {link}'
            )

        if not filtered_events:
            filter_desc = f" matching keyword '{keyword}'" if keyword else ""
            all_day_desc = " (excluding all-day events)" if not include_all_day else ""
            return f"No events found{filter_desc}{all_day_desc} in calendar '{calendar_id}' between {start_date} and {end_date}."

        filter_info = []
        if keyword:
            filter_info.append(f"keyword: '{keyword}'")
        if not include_all_day:
            filter_info.append("excluding all-day events")

        filter_text = f" (filtered by: {', '.join(filter_info)})" if filter_info else ""

        text_output = (
            f"Found {len(filtered_events)} events{filter_text} in calendar '{calendar_id}' between {start_date} and {end_date}:\n"
            + "\n".join(filtered_events)
        )

        logger.info(f"Successfully filtered {len(filtered_events)} events from {len(items)} total events.")
        return text_output

    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error filtering events by date range: {e}")
        return f"Error filtering events by date range: {str(e)}"


@handle_http_errors("get_event", is_read_only=True)
async def get_event(
    event_id: str,
    calendar_id: str = "primary"
) -> str:
    """
    Retrieves the details of a single event by its ID from a specified Google Calendar.

    Args:
        event_id (str): The ID of the event to retrieve. Required.
        calendar_id (str): The ID of the calendar to query. Defaults to 'primary'.

    Returns:
        str: A formatted string with the event's details.
    """
    try:
        service = await get_authenticated_google_service("calendar", "v3", "get_event")

        logger.info(f"[get_event] Invoked. Event ID: {event_id}")

        event = await asyncio.to_thread(
            lambda: service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        )
        summary = event.get("summary", "No Title")
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        link = event.get("htmlLink", "No Link")
        description = event.get("description", "No Description")
        location = event.get("location", "No Location")
        attendees = event.get("attendees", [])
        attendee_emails = ", ".join([a.get("email", "") for a in attendees]) if attendees else "None"
        event_details = (
            f'Event Details:\n'
            f'- Title: {summary}\n'
            f'- Starts: {start}\n'
            f'- Ends: {end}\n'
            f'- Description: {description}\n'
            f'- Location: {location}\n'
            f'- Attendees: {attendee_emails}\n'
            f'- Event ID: {event_id}\n'
            f'- Link: {link}'
        )
        logger.info(f"[get_event] Successfully retrieved event {event_id}.")
        return event_details

    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting event: {e}")
        return f"Error getting event: {str(e)}"

# Register tools with the transport manager
register_tool_with_transport("list_calendars", list_calendars)
register_tool_with_transport("get_events", get_events)
register_tool_with_transport("filter_events_by_date_range", filter_events_by_date_range)
register_tool_with_transport("create_event", create_event)
register_tool_with_transport("modify_event", modify_event)
register_tool_with_transport("delete_event", delete_event)
register_tool_with_transport("get_event", get_event)

logger.info("Calendar tools registered with session-aware transport")