# Google Workspace MCP Server

A comprehensive Model Context Protocol (MCP) server for Google Workspace services including Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, Tasks, and Chat with OAuth2 authentication.

## Features

- **Gmail Operations**: List labels, search messages, send emails, get message content
- **Google Drive**: File management, content access, and file creation
- **Google Calendar**: Event management and calendar operations
- **Google Docs**: Document creation and content access
- **Google Sheets**: Spreadsheet operations, data reading and creation
- **Google Slides**: Presentation management and creation
- **Google Forms**: Form creation and management
- **Google Tasks**: Task list and task management
- **Google Chat**: Space management and messaging
- **OAuth2 Authentication**: Secure access via Google Access Tokens
- **Stateless Architecture**: Each request is independent with Bearer token authentication
- **Service Filtering**: Enable specific services as needed

## Quick Start

### Starting the Server

```bash
# Start HTTP server on port 30000 (default)
python google_workspace_mcp_stateless.py

# Start on custom port
python google_workspace_mcp_stateless.py --port 8080

# Start with debug logging
python google_workspace_mcp_stateless.py --log-level DEBUG

# Enable specific services only
python google_workspace_mcp_stateless.py --tools gmail,drive,calendar

# Install and run from PyPI
pip install workspace-mcp-http
workspace-mcp-http
```

The server provides these endpoints:
- **`POST /mcp/`** - Main MCP endpoint for tool execution
- **`GET /health`** - Health check endpoint

### Authentication

All requests require a Google Access Token via Authorization header:

```bash
Authorization: Bearer ya29.your-google-access-token
```

[Set up Google OAuth2](https://developers.google.com/workspace/guides/auth-overview) and obtain access tokens with appropriate scopes.

## Tools

The server provides 25 tools for comprehensive Google Workspace API access. Each tool requires `Authorization: Bearer <token>` header.

### Gmail Tools

#### 1. gmail_list_labels
List all Gmail labels.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
      "name": "gmail_list_labels",
      "arguments": {}
    }
  }'
```

#### 2. gmail_search_messages
Search Gmail messages.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "gmail_search_messages",
      "arguments": {
        "query": "is:unread from:important@example.com",
        "max_results": 20
      }
    }
  }'
```

#### 3. gmail_get_message_content
Get detailed information about a specific Gmail message.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "gmail_get_message_content",
      "arguments": {
        "message_id": "1234567890abcdef"
      }
    }
  }'
```

#### 4. gmail_send_message
Send a Gmail message.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "4",
    "method": "tools/call",
    "params": {
      "name": "gmail_send_message",
      "arguments": {
        "to": "recipient@example.com",
        "subject": "Hello from Google Workspace MCP",
        "body": "This email was sent via the MCP server!"
      }
    }
  }'
```

### Google Drive Tools

#### 5. drive_list_files
List Google Drive files.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "5",
    "method": "tools/call",
    "params": {
      "name": "drive_list_files",
      "arguments": {
        "query": "name contains \"project\"",
        "max_results": 15
      }
    }
  }'
```

#### 6. drive_get_file_content
Get Google Drive file content.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "6",
    "method": "tools/call",
    "params": {
      "name": "drive_get_file_content",
      "arguments": {
        "file_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
      }
    }
  }'
```

#### 7. drive_create_file
Create a Google Drive file.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "7",
    "method": "tools/call",
    "params": {
      "name": "drive_create_file",
      "arguments": {
        "name": "my-document.txt",
        "content": "Hello, this is my new document content!",
        "parent_folder_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
      }
    }
  }'
```

### Google Calendar Tools

#### 8. calendar_list_events
List Google Calendar events.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "8",
    "method": "tools/call",
    "params": {
      "name": "calendar_list_events",
      "arguments": {
        "max_results": 25
      }
    }
  }'
```

#### 9. calendar_list_calendars
List Google Calendars.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "9",
    "method": "tools/call",
    "params": {
      "name": "calendar_list_calendars",
      "arguments": {}
    }
  }'
```

#### 10. calendar_create_event
Create a Google Calendar event.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "10",
    "method": "tools/call",
    "params": {
      "name": "calendar_create_event",
      "arguments": {
        "summary": "Team Meeting",
        "start_time": "2024-01-15T10:00:00-08:00",
        "end_time": "2024-01-15T11:00:00-08:00"
      }
    }
  }'
```

### Google Docs Tools

#### 11. docs_get_document
Get Google Docs document.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "11",
    "method": "tools/call",
    "params": {
      "name": "docs_get_document",
      "arguments": {
        "document_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
      }
    }
  }'
```

#### 12. docs_create_document
Create a Google Docs document.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "12",
    "method": "tools/call",
    "params": {
      "name": "docs_create_document",
      "arguments": {
        "title": "My New Document",
        "content": "This is the initial content of my document."
      }
    }
  }'
```

### Google Sheets Tools

#### 13. sheets_get_spreadsheet
Get Google Sheets spreadsheet.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "13",
    "method": "tools/call",
    "params": {
      "name": "sheets_get_spreadsheet",
      "arguments": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
      }
    }
  }'
```

#### 14. sheets_read_values
Read values from Google Sheets.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "14",
    "method": "tools/call",
    "params": {
      "name": "sheets_read_values",
      "arguments": {
        "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
        "range_name": "A1:D10"
      }
    }
  }'
```

#### 15. sheets_create_spreadsheet
Create a Google Sheets spreadsheet.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "15",
    "method": "tools/call",
    "params": {
      "name": "sheets_create_spreadsheet",
      "arguments": {
        "title": "My New Spreadsheet"
      }
    }
  }'
```

### Google Slides Tools

#### 16. slides_get_presentation
Get Google Slides presentation.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "16",
    "method": "tools/call",
    "params": {
      "name": "slides_get_presentation",
      "arguments": {
        "presentation_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
      }
    }
  }'
```

#### 17. slides_create_presentation
Create a Google Slides presentation.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "17",
    "method": "tools/call",
    "params": {
      "name": "slides_create_presentation",
      "arguments": {
        "title": "My New Presentation"
      }
    }
  }'
```

### Google Tasks Tools

#### 18. tasks_list_task_lists
List Google Tasks task lists.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "18",
    "method": "tools/call",
    "params": {
      "name": "tasks_list_task_lists",
      "arguments": {}
    }
  }'
```

#### 19. tasks_list_tasks
List tasks from a Google Tasks list.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "19",
    "method": "tools/call",
    "params": {
      "name": "tasks_list_tasks",
      "arguments": {
        "task_list_id": "@default"
      }
    }
  }'
```

#### 20. tasks_create_task
Create a task in Google Tasks.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "20",
    "method": "tools/call",
    "params": {
      "name": "tasks_create_task",
      "arguments": {
        "task_list_id": "@default",
        "title": "Complete project documentation",
        "notes": "Review and finalize all documentation for the project"
      }
    }
  }'
```

### Google Forms Tools

#### 21. forms_create_form
Create a Google Form.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "21",
    "method": "tools/call",
    "params": {
      "name": "forms_create_form",
      "arguments": {
        "title": "Customer Feedback Survey"
      }
    }
  }'
```

#### 22. forms_get_form
Get Google Form information.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "22",
    "method": "tools/call",
    "params": {
      "name": "forms_get_form",
      "arguments": {
        "form_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
      }
    }
  }'
```

### Google Chat Tools

#### 23. chat_list_spaces
List Google Chat spaces.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "23",
    "method": "tools/call",
    "params": {
      "name": "chat_list_spaces",
      "arguments": {}
    }
  }'
```

#### 24. chat_send_message
Send a message to Google Chat.

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "24",
    "method": "tools/call",
    "params": {
      "name": "chat_send_message",
      "arguments": {
        "space_name": "spaces/AAAAxxxxxxx",
        "text": "Hello from the Google Workspace MCP Server!"
      }
    }
  }'
```

## List Available Tools

Get the complete list of available tools:

```bash
curl -X POST http://localhost:30000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ya29.your-google-access-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": "tools-list",
    "method": "tools/list",
    "params": {}
  }'
```

## Installation

### From PyPI
```bash
pip install workspace-mcp-http
workspace-mcp-http
```

### From Source
```bash
pip install -r requirements.txt
python google_workspace_mcp_stateless.py
```

## Authentication Setup

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable required APIs (Gmail, Drive, Calendar, etc.)

2. **Set up OAuth2:**
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Configure OAuth consent screen
   - Download client configuration

3. **Required Scopes:**
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/drive
   https://www.googleapis.com/auth/calendar
   https://www.googleapis.com/auth/documents
   https://www.googleapis.com/auth/spreadsheets
   https://www.googleapis.com/auth/presentations
   https://www.googleapis.com/auth/tasks
   https://www.googleapis.com/auth/forms.body
   https://www.googleapis.com/auth/chat.spaces
   ```

4. **Get Access Token:**
   - Use Google OAuth2 flow to obtain access tokens
   - Pass tokens via `Authorization: Bearer` header

## Usage with Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "python",
      "args": ["/path/to/google_workspace_mcp_stateless.py"],
      "env": {
        "GOOGLE_ACCESS_TOKEN": "ya29.your-google-access-token"
      }
    }
  }
}
```

## Configuration

### Environment Variables

```bash
# Optional - server will get token from Authorization header if not set
GOOGLE_ACCESS_TOKEN=ya29.your-google-access-token

# Server Configuration
PORT=30000
LOG_LEVEL=INFO
```

### Service Filtering

Enable specific services only:

```bash
# Enable only Gmail and Drive
python google_workspace_mcp_stateless.py --tools gmail,drive

# Enable Calendar, Docs, and Sheets
python google_workspace_mcp_stateless.py --tools calendar,docs,sheets
```

Available services: `gmail`, `drive`, `calendar`, `docs`, `sheets`, `slides`, `forms`, `tasks`, `chat`

## Use Cases

### Email Management
- Search and filter Gmail messages
- Send automated emails
- Manage labels and organization
- Extract email content and metadata

### Document Collaboration
- Create and manage Google Docs
- Access document content
- Automate document workflows
- Sync content across services

### Data Analysis
- Read and write Google Sheets data
- Create automated reports
- Manage spreadsheet operations
- Export data for analysis

### Project Management
- Manage Google Tasks and task lists
- Create calendar events and schedules
- Track project milestones
- Coordinate team activities

### Communication
- Manage Google Chat spaces
- Send automated notifications
- Create Google Forms for feedback
- Coordinate team communications

## Error Handling

The server provides detailed error messages for common issues:
- **401**: Invalid or expired Google access token
- **403**: Insufficient permissions or missing scopes
- **404**: Resource not found (document, file, etc.)
- **429**: Rate limit exceeded
- **500**: Internal server errors

## Google Workspace Concepts

### File IDs
Google Drive, Docs, Sheets, and Slides use unique file IDs:
- Found in URLs: `https://docs.google.com/document/d/{FILE_ID}/edit`
- Format: Long alphanumeric string (e.g., `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`)

### Resource Names
Google Chat spaces use resource names:
- Format: `spaces/{SPACE_ID}`
- Example: `spaces/AAAAxxxxxxx`

### Time Formats
Calendar events use RFC3339 format:
- Format: `YYYY-MM-DDTHH:MM:SS±HH:MM`
- Example: `2024-01-15T10:00:00-08:00`

## Development

### Run in Development Mode
```bash
python google_workspace_mcp_stateless.py --log-level DEBUG --port 8080
```

### Testing
```bash
python test_token_auth.py
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.