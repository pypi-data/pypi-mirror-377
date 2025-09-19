import logging
import sys
import os
import atexit
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import builtins
import time

# --- Global State Management ---
connection = None
_last_db_params = None # New: Store last used DB credentials for auto-reconnect
_schema_cache = {}
_last_printed = None
_original_print = builtins.print
_log_style = 'basic' # Default log style, can be changed by activate_auto_logging

# --- Custom Formatter for Console Output ---
class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter to control the console log output style
    based on the globally set _log_style variable.
    """
    def format(self, record):
        """Formats a log record according to the globally set style."""
        global _log_style
        iso_timestamp = datetime.utcnow().isoformat(timespec='microseconds') + 'Z'
        base_message = f"{record.levelname} {iso_timestamp} {record.getMessage()}"

        if _log_style == 'basic':
            return base_message

        detailed_info = {
            "timestamp": iso_timestamp,
            "level": record.levelname,
            "event": record.getMessage(),
            "function": record.funcName,
            "details": getattr(record, "details", None)
        }

        if _log_style == 'detailed':
            return json.dumps(detailed_info)

        if _log_style == 'kestra':
            if detailed_info["function"] or detailed_info["details"]:
                extra_details = json.dumps({k: v for k, v in detailed_info.items() if v and k not in ['timestamp', 'level', 'event']})
                return f"{base_message} | {extra_details}"
            return base_message
        
        return base_message # Fallback to basic

# --- Database Handler for Automatic Logging ---
class DatabaseLogHandler(logging.Handler):
    """
    A dynamic handler that sends log records to a PostgreSQL table based on a
    configurable mapping. This is used by the new activate_auto_logging function.
    """
    def __init__(self, schema, table, column_mapping, static_fields, db_connection):
        super().__init__()
        self.schema = schema
        self.table = table
        self.column_mapping = column_mapping
        self.static_fields = static_fields or {}
        self.connection = db_connection

    def emit(self, record):
        """
        This method is called for every log record. It formats the record and
        inserts it into the configured database table.
        """
        if not self.connection or self.connection.closed:
            return
            
        log_data = {}
        try:
            # 1. Add dynamic values from the log record
            for db_col, log_attr in self.column_mapping.items():
                if log_attr == 'timestamp':
                    log_data[db_col] = datetime.fromtimestamp(record.created)
                elif log_attr == 'status':
                    log_data[db_col] = record.levelname
                elif log_attr == 'description':
                    log_data[db_col] = record.getMessage()
                else:
                    log_data[db_col] = getattr(record, log_attr, None)
            
            # 2. Add all static field values
            log_data.update(self.static_fields)

            db_columns = list(log_data.keys())
            values_to_insert = list(log_data.values())

            query = sql.SQL("INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders})").format(
                schema=sql.Identifier(self.schema),
                table=sql.Identifier(self.table),
                columns=sql.SQL(', ').join(map(sql.Identifier, db_columns)),
                placeholders=sql.SQL(', ').join(sql.Placeholder() * len(values_to_insert))
            )

            with self.connection.cursor() as cursor:
                cursor.execute(query, values_to_insert)
            self.connection.commit()
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"--- CRITICAL: FAILED TO LOG TO DATABASE ---", file=sys.__stderr__)
            print(f"Error: {e}", file=sys.__stderr__)

_error_capture_handler = None

class ErrorCaptureHandler(logging.Handler):
    """
    A custom handler to capture structured data from WARNING, ERROR, 
    and CRITICAL logs.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = [] 

    def emit(self, record):
        """Stores structured error/warning information in a list."""
        error_data = {
            'timestamp': datetime.fromtimestamp(record.created),
            'level': record.levelname,
            'message': record.getMessage(),
            'hint': getattr(record, 'hint', 'No hint provided.')
        }
        self.errors.append(error_data)

def setup_error_capture():
    """
    Sets up a global handler to capture WARNING level and higher logs.
    """
    global _error_capture_handler
    if _error_capture_handler:
        return

    _error_capture_handler = ErrorCaptureHandler()
    # CHANGE: Now captures WARNING, ERROR, and CRITICAL
    _error_capture_handler.setLevel(logging.WARNING) 
    logging.getLogger().addHandler(_error_capture_handler)
    logging.info("Warning/Error summary capture has been activated.")

def get_captured_errors():
    """
    Retrieves a raw list of all captured logs.
    """
    global _error_capture_handler
    if _error_capture_handler:
        return _error_capture_handler.errors
    return None

def format_error_summary(errors_list):
    """
    Formats a list of error/warning dictionaries into a readable string summary.
    """
    if not errors_list:
        return "" # Return a blank string if there are no errors

    summary_parts = ["ISSUES SUMMARY (Warnings & Errors)"]
    for i, err in enumerate(errors_list, 1):
        summary_parts.append(f"\n--- Issue #{i} ---")
        summary_parts.append(f"  Timestamp: {err['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append(f"  Level    : {err['level']}")
        summary_parts.append(f"  Message  : {err['message']}")
    summary_parts.append("\n")
    return "\n".join(summary_parts)

# function you can call from your main script.
def get_formatted_summary():
    """
    Retrieves all captured warnings/errors and returns them as a single,
    formatted string. Returns a blank string if no issues were captured.
    """
    captured_issues = get_captured_errors()
    if not captured_issues:
        return ""
    return format_error_summary(captured_issues)

# --- Main Activation Function ---
def activate_auto_logging(schema: str, table: str, column_map: str, db_params: dict, static_fields: dict = None, level: str = 'basic', capture_prints: bool = True, capture_exceptions: bool = True):
    """
    Activates the fully automatic logging system. Call this once at the start.

    Args:
        schema (str): The database schema name for the log table.
        table (str): The database table name for the log table.
        column_map (str): Mapping of DB columns to DYNAMIC log attributes. Format: "db_col:log_attr,..."
        db_params (dict): DB credentials as a dictionary.
        static_fields (dict, optional): A dictionary of static column names and their values.
        level (str, optional): The console logging style ('basic', 'detailed', 'kestra'). Defaults to 'basic'.
        capture_prints (bool, optional): If True, captures all print() statements. Defaults to True.
        capture_exceptions (bool, optional): If True, captures all uncaught exceptions. Defaults to True.
    """
    global _log_style, connection, _last_db_params
    _log_style = level
    _last_db_params = db_params # Store credentials for auto-reconnect
    
    # --- CONFIGURE CONSOLE LOGGING ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Set the lowest level for the logger to process

    # 1. Remove any existing handlers to prevent duplicate logs
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
             root_logger.removeHandler(handler)

    # 2. Create handler for INFO level logs -> sends to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    # This filter ensures that only INFO (and lower) level messages are handled.
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    stdout_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(stdout_handler)

    # 3. Create handler for WARNING and above -> sends to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING) # This handler only processes WARNING, ERROR, CRITICAL
    stderr_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(stderr_handler)
    
    # --- DB, PRINT & EXCEPTION CAPTURE (No changes needed below this line) ---
    try:
        if not (connection and not connection.closed):
            connection = psycopg2.connect(**db_params)
            atexit.register(close_db_connection)
    except psycopg2.Error as e:
        logging.critical(f"Failed to connect to database: {e}")
        sys.exit(1)

    # Set up the Database Handler
    try:
        column_map_dict = dict(item.split(':', 1) for item in column_map.split(','))
        db_handler = DatabaseLogHandler(schema, table, column_map_dict, static_fields, connection)
        # Avoid adding the DB handler if one already exists
        if not any(isinstance(h, DatabaseLogHandler) for h in logging.getLogger().handlers):
            logging.getLogger().addHandler(db_handler)
    except Exception as e:
        logging.critical(f"Failed to set up database handler: {e}")
        return

    # Capture print() statements
    if capture_prints:
        _original_print_func = builtins.print
        def auto_log_print(*args, **kwargs):
            message = ' '.join(map(str, args))
            message_lower = message.lower() # Use a lowercase version for keyword matching

            # Automatically determine the log level based on keywords
            if any(keyword in message_lower for keyword in ['error', 'critical', 'failed', 'exception']):
                logging.error(message, extra={"details": {"source": "print"}})
            elif 'warning' in message_lower:
                logging.warning(message, extra={"details": {"source": "print"}})
            else:
                logging.info(message, extra={"details": {"source": "print"}})

            _original_print_func(*args, **kwargs) # Call the original print function
        builtins.print = auto_log_print

    # Capture uncaught exceptions
    if capture_exceptions:
        def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.excepthook = handle_uncaught_exception

    logging.info(f"Automatic Logger Activated. Console style: '{level}'. DB Target: '{schema}.{table}'.")

# --- Original Core Database Functions (for backward compatibility) ---

def get_db_params(db_params=None):
    """Retrieves DB credentials from a dict or falls back to .env file."""
    if db_params:
        return db_params
    load_dotenv()
    return {
        "host": os.getenv("DB_HOST"), "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"), "password": os.getenv("DB_PASSWORD")
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def connect_to_db(db_params=None):
    """Establishes a global connection and stores the params for auto-reconnect."""
    global connection, _last_db_params
    if connection and not connection.closed:
        return
    
    params = get_db_params(db_params)
    _last_db_params = params # Store the parameters for future use
    
    try:
        connection = psycopg2.connect(**params)
        atexit.register(close_db_connection)
    except psycopg2.Error as e:
        logging.critical(f"Failed to connect to database via connect_to_db: {e}")
        sys.exit(1)


def close_db_connection():
    """Closes the global DB connection and removes the DB handler."""
    global connection
    if connection and not connection.closed:
        for handler in logging.getLogger().handlers[:]:
            if isinstance(handler, DatabaseLogHandler):
                logging.getLogger().removeHandler(handler)
        connection.close()
        builtins.print("Database connection closed.")

def get_column_types(schema_name, table_name):
    """Retrieves and caches column names and their data types for a given table."""
    db_health_check() # Ensure connection is active before query
    cache_key = f"{schema_name}.{table_name}"
    if cache_key in _schema_cache: return _schema_cache[cache_key]
    if not connection or connection.closed: return {}
    with connection.cursor() as cursor:
        try:
            query = sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = %s AND table_name = %s")
            cursor.execute(query, (schema_name, table_name))
            _schema_cache[cache_key] = {row[0]: row[1] for row in cursor.fetchall()}
            return _schema_cache[cache_key]
        except psycopg2.Error as e:
            logging.error(f"Could not fetch schema for {cache_key}: {e}")
            return {}

def _process_values(schema_name, table_name, columns, values):
    """Internal helper for the original print_log function."""
    if not values or ('current_timestamp' not in values and 'last_print' not in values):
        return values
    column_types = get_column_types(schema_name, table_name)
    processed_values = list(values)
    now_dt = None
    for i, value in enumerate(processed_values):
        if value == 'last_print':
            global _last_printed
            processed_values[i] = _last_printed
            continue
        if value == 'current_timestamp':
            if now_dt is None: now_dt = datetime.utcnow()
            column_name = columns[i]
            data_type = column_types.get(column_name, '').lower()
            if 'timestamp' in data_type: processed_values[i] = now_dt
            elif data_type in ('text', 'varchar', 'json', 'jsonb'): processed_values[i] = now_dt.isoformat()
            else: processed_values[i] = now_dt
    return processed_values

def validate_columns(schema_name, table_name, columns):
    """Checks if a list of columns exists in the specified database table."""
    existing_columns = get_column_types(schema_name, table_name).keys()
    if not existing_columns:
        logging.warning(
            f"Could not validate columns for {schema_name}.{table_name}, schema unavailable.",
            extra={"function": "validate_columns"}
        )
        return
    invalid_cols = set(columns) - set(existing_columns)
    if invalid_cols:
        raise ValueError(f"Invalid columns for table '{schema_name}.{table_name}': {invalid_cols}")

def log_event(message, function, details=None):
    """A standardized helper function to create a structured log entry."""
    logging.info(message, extra={"function": function, "details": details})

def _safe_json(obj):
    """A helper to make objects JSON-serializable, specifically handling datetimes."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def print_log(schema_name, table_name, columns, values, log_detail_column=None, returning_column=None):
    """Legacy function to manually insert a log record."""
    db_health_check() # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection for print_log.")
        return None
    processed_values = _process_values(schema_name, table_name, columns, values)
    with connection.cursor() as cursor:
        try:
            part1 = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(processed_values))
            )
            if returning_column:
                part2 = sql.SQL(" RETURNING {}").format(sql.Identifier(returning_column))
                query = part1 + part2
            else:
                query = part1
            
            cursor.execute(query, processed_values)
            connection.commit()
            if returning_column:
                return cursor.fetchone()[0]
        except psycopg2.Error as error:
            connection.rollback()
            logging.error(f"Insert Error in print_log: {error}")
            return None

def update_log(schema_name, table_name, condition_column, condition_value, columns, values):
    """Updates an existing record in the database."""
    db_health_check() # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "update_log"})
        return
    processed_values = _process_values(schema_name, table_name, columns, values)
    with connection.cursor() as cursor:
        try:
            set_clause = sql.SQL(', ').join(
                sql.SQL('{} = %s').format(sql.Identifier(col)) for col in columns
            )
            query = sql.SQL("UPDATE {}.{} SET {} WHERE {} = %s").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                set_clause,
                sql.Identifier(condition_column)
            )
            cursor.execute(query, processed_values + [condition_value])
            connection.commit()
        except psycopg2.Error as error:
            logging.error(f"Update Error: {error}", extra={"function": "update_log"})
            connection.rollback()

def upsert_log(schema_name, table_name, unique_key_column, unique_key_value, update_columns, update_values, log_detail_column=None):
    """Performs an 'upsert' (update or insert)."""
    db_health_check() # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "upsert_log"})
        return
    with connection.cursor() as cursor:
        try:
            query = sql.SQL("SELECT 1 FROM {}.{} WHERE {} = %s").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.Identifier(unique_key_column)
            )
            cursor.execute(query, [unique_key_value])
            exists = cursor.fetchone()
            
            if exists:
                update_log(schema_name, table_name, unique_key_column, unique_key_value, update_columns, update_values)
            else:
                all_cols = [unique_key_column] + update_columns
                all_vals = [unique_key_value] + update_values
                print_log(schema_name, table_name, all_cols, all_vals, log_detail_column=log_detail_column)
        except psycopg2.Error as error:
            logging.error(f"Upsert Error: {error}", extra={"function": "upsert_log"})

def delete_log(schema_name, table_name, condition_column, condition_value):
    """Deletes a record from a database table based on a simple condition."""
    db_health_check() # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "delete_log"})
        return
    with connection.cursor() as cursor:
        try:
            query = sql.SQL("DELETE FROM {}.{} WHERE {} = %s").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
                sql.Identifier(condition_column)
            )
            cursor.execute(query, [condition_value])
            connection.commit()
        except psycopg2.Error as error:
            logging.error(f"Delete Error: {error}", extra={"function": "delete_log"})
            connection.rollback()

def get_next_value(sequence_name):
    """
    Fetches the next value from a specified PostgreSQL sequence, ensuring a unique ID.
    This is the recommended way to generate primary keys to avoid race conditions.

    Args:
        sequence_name (str): The fully qualified name of the sequence 
                             (e.g., 'schema.sequence_name'). This is a required argument.

    Returns:
        int: The next unique ID from the sequence, or None if an error occurs.
    """
    db_health_check()  # Ensure the connection is active before proceeding.
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "get_next_process_id"})
        return None

    with connection.cursor() as cursor:
        try:
            # Safely execute the query to get the next value from the sequence.
            query = sql.SQL("SELECT nextval(%s)")
            cursor.execute(query, (sequence_name,))
            
            new_id = cursor.fetchone()[0]
            
            # The commit is important to ensure the sequence is advanced for other sessions.
            connection.commit() 
            
            return new_id
            
        except psycopg2.Error as error:
            logging.error(f"Error fetching nextval from '{sequence_name}': {error}", extra={"function": "get_next_process_id"})
            connection.rollback()  # Rollback transaction on error.
            return None


def calculate_aggregate(schema_name, table_name, column_name, operation):
    """
    Calculates an aggregate value (max, min, or average) for a specific column.

    Args:
        schema_name (str): The database schema name.
        table_name (str): The database table name.
        column_name (str): The name of the column to perform the calculation on.
        operation (str): The aggregate operation to perform. 
                         Valid options are 'max', 'min', or 'average'.

    Returns:
        The result of the aggregate function (could be Decimal, int, float), 
        or None if an error occurs or the table is empty.
    """
    db_health_check()  # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "calculate_aggregate"})
        return None

    # Validate the operation and get the corresponding SQL function
    valid_operations = {
        'max': sql.SQL('MAX'),
        'min': sql.SQL('MIN'),
        'average': sql.SQL('AVG')
    }
    
    op_sql = valid_operations.get(operation.lower())
    if not op_sql:
        logging.error(f"Invalid operation '{operation}'. Use 'max', 'min', or 'average'.")
        raise ValueError(f"Invalid operation '{operation}'. Use 'max', 'min', or 'average'.")

    with connection.cursor() as cursor:
        try:
            # Construct the query safely to prevent SQL injection
            query = sql.SQL("SELECT {operation}({column}) FROM {schema}.{table}").format(
                operation=op_sql,
                column=sql.Identifier(column_name),
                schema=sql.Identifier(schema_name),
                table=sql.Identifier(table_name)
            )
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            # fetchone() returns a tuple, e.g., (Decimal('123.45'),) or (None,) for empty table
            return result[0] if result else None
            
        except psycopg2.Error as error:
            logging.error(f"Aggregate calculation error: {error}", extra={"function": "calculate_aggregate"})
            connection.rollback()  # Rollback in case of error
            return None



def fetch_latest_value(schema_name, table_name, target_column, order_by_column):
    """Fetches the most recent value from a specific column based on an ordering column."""
    db_health_check() # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "fetch_latest_value"})
        return None
    with connection.cursor() as cursor:
        try:
            query = sql.SQL("SELECT {target} FROM {schema}.{table} ORDER BY {order_col} DESC LIMIT 1").format(
                target=sql.Identifier(target_column),
                schema=sql.Identifier(schema_name),
                table=sql.Identifier(table_name),
                order_col=sql.Identifier(order_by_column)
            )
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else None
        except psycopg2.Error as error:
            logging.error(f"Fetch Error: {error}", extra={"function": "fetch_latest_value"})
            return None

def bulk_insert_from_csv(schema_name, table_name, csv_path):
    """Efficiently bulk inserts data into a table from a CSV file."""
    db_health_check() # Ensure connection is active
    if not connection or connection.closed:
        logging.error("No active DB connection.", extra={"function": "bulk_insert_from_csv"})
        return
    with connection.cursor() as cursor:
        try:
            with open(csv_path, 'r') as f:
                next(f)  # Skip the header row
                copy_sql = sql.SQL("COPY {}.{} FROM STDIN WITH CSV").format(
                    sql.Identifier(schema_name), sql.Identifier(table_name))
                cursor.copy_expert(sql=copy_sql, file=f)
            connection.commit()
        except (psycopg2.Error, FileNotFoundError) as error:
            logging.error(f"Bulk insert error: {error}", extra={"function": "bulk_insert_from_csv"})
            connection.rollback()

def db_health_check():
    """
    Performs a health check on the database connection.
    If the connection is closed or stale, it attempts to reconnect automatically
    using the last known database credentials.
    """
    global connection
    try:
        # Case 1: Connection is explicitly closed or was never established.
        if not connection or connection.closed:
            logging.info("DB connection is closed or uninitialized. Attempting to reconnect...")
            connect_to_db(_last_db_params)
            logging.info("DB reconnected successfully.")
            return True # connect_to_db will exit on failure, so if we are here, it worked.

        # Case 2: Connection object exists, but might be stale.
        # A simple query will raise an exception if the connection is dead.
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True

    except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
        logging.warning(f"DB connection was stale ({e}). Attempting to reconnect...")
        try:
            connect_to_db(_last_db_params)
            logging.info("DB reconnected successfully after stale connection.")
            return True # Reconnection successful
        except Exception as recon_e:
            logging.error(f"Failed to reconnect to the database: {recon_e}")
            return False # Reconnection failed
    except Exception as e:
        logging.error(f"An unexpected error occurred during DB health check: {e}")
        return False