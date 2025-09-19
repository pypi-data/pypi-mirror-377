# 🍒 easy\_cherry: Your Python Toolkit for Effortless Operations

**easy\_cherry** is a powerful, developer-friendly Python utility library designed to streamline common yet complex operational tasks. It provides an intelligent, high-level interface for sending rich Slack notifications and a robust, one-line activation system for automated PostgreSQL logging.

Born from the need to eliminate repetitive boilerplate code, `easy_cherry` handles the tedious aspects of API interactions, data formatting, and event capturing. This allows you to focus on your core application logic while maintaining best-in-class monitoring and communication capabilities.

[](https://www.google.com/search?q=https://badge.fury.io/py/easy-cherry)
[](https://opensource.org/licenses/MIT)
[](https://www.google.com/search?q=https://pypi.org/project/easy-cherry/)

-----

## \#\# Core Features

The library is built around two primary, independent pillars of functionality: intelligent Slack integration and automated database logging.

### \#\#\# 🤖 Intelligent Slack Notifications

This module acts as a smart wrapper around the official Slack SDK, simplifying communication workflows.

  * **Effortless Targeting**: Forget looking up user or channel IDs. Send messages directly using familiar identifiers like **email addresses** (`jane.doe@example.com`), **real names** (`Jane Doe`), **channel names** (`#devops-alerts`), or standard IDs. The library resolves them automatically.
  * **Smart Text Formatting**: Seamlessly pass **HTML strings** to the notifier. It automatically detects and converts them into Slack's `mrkdwn` format for clean, readable messages without extra flags.
  * **Rich Block Kit Helpers**: Build professional, visually appealing messages with easy-to-use static methods like `.create_header_block()` and `.create_fields_section()`. These helpers simplify the construction of Slack's JSON-based Block Kit.
  * **Bulk Operations**: Send the **same message or files to multiple recipients** in a single command. You can also **attach multiple files** from local paths to a single notification with ease.
  * **Robust & Resilient**: Features **built-in caching** for user and channel lookups to reduce API calls, configurable timeouts, and detailed, per-recipient API responses for granular error handling.

### \#\#\# 🐘 Automated Database Logging

This module provides a "fire-and-forget" system for logging application events to a PostgreSQL database.

  * **One-Line Activation**: Call a single function, `activate_auto_logging()`, at the start of your script to instrument your entire application.
  * **Comprehensive Event Capture**: It automatically captures and redirects three key sources of runtime information:
    1.  **Standard `logging` Records**: All calls to `logging.info()`, `logging.warning()`, etc.
    2.  **`print()` Statements**: All output from the built-in `print()` function is captured as an INFO log.
    3.  **Unhandled Exceptions**: Catches and logs any uncaught exceptions as CRITICAL errors before the program exits.
  * **Structured & Dynamic**: Logs events with structured data like timestamps, log levels, and function names. A **flexible column map** allows you to dynamically route log attributes to specific database columns.
  * **Resilient Connection**: Includes **automatic reconnection logic with exponential backoff** to handle transient database interruptions, ensuring log data isn't lost.

-----

## \#\# Installation

`easy_cherry` is available on PyPI and can be installed with pip. This single command installs the library and all its required dependencies.

```bash
pip install --upgrade easy-cherry
```

-----

## \#\# Configuration

For security and portability, the library is designed to work with environment variables. Create a `.env` file in your project's root directory and `easy_cherry` (via `python-dotenv`) will automatically load the credentials.

#### **`.env` file example**

```ini
# .env

# == Credentials for PostgreSQL Database Logging ==
DB_HOST=your_db_host.com
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_secure_password

# == Token for Slack Notifications ==
# This is your Bot User OAuth Token, starting with "xoxb-"
# It requires the chat:write, users:read, users:read.email, and files:write scopes.
SLACK_BOT_TOKEN="xoxb-your-long-bot-token-here"
```

-----

## \#\# How to Use

### \#\#\# 1. Automated Database Logging

Call `activate_auto_logging` once at the very beginning of your main script. It will configure the root logger and remain active for the application's entire lifecycle.

#### **Quick Start: One-Line Activation**

```python
import os
import logging
from dotenv import load_dotenv
from easy_cherry import activate_auto_logging

# 1. Load credentials from your .env file
load_dotenv()
db_credentials = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# 2. Define how log attributes map to your database table columns
# The format is "db_column_name:log_attribute"
# Common attributes: timestamp, status, description, function, details
column_mapping = "log_timestamp:timestamp,status:status,description:description"

# 3. Activate the automatic logging system!
activate_auto_logging(
    schema='public',
    table='application_logs',
    column_map=column_mapping,
    db_params=db_credentials,
    level='detailed'  # Console log style: 'basic', 'detailed', or 'kestra'
)

# --- Your application logic now runs with auto-logging ---

logging.info("Application starting up.", extra={"details": {"pid": 1234}})
print("This print statement will be captured and logged to the database.")
logging.warning("Configuration value is missing, using default.")

try:
    # This division by zero will raise an unhandled exception
    # easy_cherry will log it as a CRITICAL error before the program exits
    result = 1 / 0
except Exception:
    # The exception is already logged by the system.
    # The application can now terminate gracefully.
    pass

logging.info("Application shutdown complete.")
```

### \#\#\# 2. Sending Slack Notifications

Instantiate the `SlackNotifier` class with your token to begin sending messages.

#### **Quick Start: Your First Notification**

```python
import os
from easy_cherry import SlackNotifier

# 1. Get your token from an environment variable
slack_token = os.getenv("SLACK_BOT_TOKEN")

# 2. Initialize the notifier
# For production, set log=False to suppress console output
notifier = SlackNotifier(token=slack_token, log=True)

# 3. Send a message to a channel by name
notifier.send("#general", "Hello from easy_cherry! 🍒")

# 4. Send a direct message to a user by their email
notifier.send("jane.doe@example.com", "Just a quick heads-up about the new report.")
```

#### **Advanced Usage: Rich Reports and Multiple Files**

Combine Block Kit helpers and file attachments to send detailed, professional reports.

```python
# A list of recipients to notify
recipients = ["#devops-alerts", "jane.doe@example.com"]

# 1. Build a rich message using Block Kit helpers
report_blocks = [
    notifier.create_header_block("🚀 System Performance Report - 12 Sept 2025"),
    {"type": "divider"},
    notifier.create_fields_section({
        "CPU Load": "12%",
        "Memory Usage": "58%",
        "Disk I/O": "320 MB/s",
        "Status": "✅ All Systems Operational"
    })
]

# 2. A list of local files to attach to the message
log_files = ["./logs/app.log", "./logs/db_backup.log"]

# 3. Send the blocks and files to all recipients in one command
results = notifier.send_blocks(
    recipients,
    report_blocks,
    fallback_text="System Performance Report is ready.",
    file_paths=log_files
)

# 4. Review the detailed results
print("--- Send Report ---")
for target, response in results.items():
    status = "✅ Success" if response and response.get("ok") else "❌ Failed"
    print(f"{status} for target: {target}")
```

-----

## \#\# Contributing

Contributions are welcome\! If you have a feature request, bug report, or want to improve the code, please feel free to open an issue or submit a pull request on our GitHub repository.