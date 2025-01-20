"""Plover plugin for inserting current time with modifiers."""

import datetime
import locale
import json
import os
import logging
from pathlib import Path
from typing import Union, Tuple, List, Optional
import tempfile
import atexit

DEBUG = False  # if false disable logging

# Set up logging with fallback for __file__
try:
    log_dir = Path(tempfile.gettempdir()) / 'plover_current_time_modal'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / 'date_modifiers.log'
except Exception as e:
    log_path = Path(tempfile.gettempdir()) / 'date_modifiers.log'

logging.basicConfig(
    filename=str(log_path),
    level=logging.DEBUG if DEBUG else logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define the maximum number of strokes in any translation
LONGEST_KEY = 52  # Base stroke plus 51 modifiers

# Modifier mapping
MODIFIERS = {
    'U': 1,    # Forward one day
    'E': -1,   # Backward one day
    'O': 7,    # Forward one week
    'A': -7,   # Backward one week
    'AO': -28, # Backward on Month
    'EU': 28   # Forward on Month
}

# Valid stroke patterns
STROKE_PATTERNS = {
    'Z-TZ': ('{^}%Y-%m-%d_', 'ISO format date YYYY-MM-DD_'),
    'Z-Z': ('{^}%A', 'Weekday name'),
    'Z-DZ': ('{^}KW %W: %A %d.%m.%Y %H:%M', 'Date with time and week'),
    'Z-D': ('{^}KW %W: %A %d.%m.%Y', 'Date with week')
}

# State files for persistence
STATE_DIR = Path(tempfile.gettempdir()) / 'plover_current_time_modal'
try:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    if DEBUG:
        logging.error(f"Error creating state directory: {str(e)}")

DATE_OFFSET_FILE = STATE_DIR / 'date_offset.json'

def load_state() -> int:
    """Load the current state from files.
    
    Returns:
        int: The current day offset, 0 if no state found
    """
    try:
        if DATE_OFFSET_FILE.exists():
            try:
                with open(DATE_OFFSET_FILE, 'r', encoding='utf-8') as f:
                    offset_data = json.load(f)
                    return offset_data.get('offset', 0)
            except Exception:
                pass
    except Exception:
        pass
    return 0

def save_state(offset: int) -> None:
    """Save the current state to files.
    
    Args:
        offset: The day offset to save
    """
    try:
        temp_file = DATE_OFFSET_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({'offset': offset}, f)
        temp_file.replace(DATE_OFFSET_FILE)
    except Exception as e:
        if DEBUG:
            logging.error(f"Error saving state: {str(e)}")

def cleanup_state():
    """Clean up state files."""
    try:
        if DATE_OFFSET_FILE.exists():
            DATE_OFFSET_FILE.unlink()
    except Exception:
        pass

# Register cleanup
atexit.register(cleanup_state)

def format_time(formatting: str, locale_setting: str = 'de_DE', day_offset: int = 0) -> str:
    """Format time with optional locale and modifiers.
    
    Args:
        formatting: strftime format string
        locale_setting: locale to use for formatting (default: 'de_DE')
        day_offset: number of days to offset from current date (default: 0)
    
    Returns:
        str: The formatted time string or an error message
    """
    try:
        # save current locale to restore it later
        current_locale = locale.getlocale()[0]

        # Set locale
        try:
            locale.setlocale(locale.LC_ALL, locale_setting)
        except locale.Error:
            return f"[Locale Error: {locale_setting}]"

        try:
            # Get current time with offset
            now = datetime.datetime.now()
            # Only use the provided offset, don't add stored state
            target_date = now + datetime.timedelta(days=day_offset)
            
            # Use ISO week number directly
            if 'KW %W' in formatting:
                iso_year, iso_week, iso_day = target_date.isocalendar()
                formatting = formatting.replace('KW %W', f'KW {iso_week:02d}')

            return target_date.strftime(formatting)
        except ValueError as e:
            return f"[Format Error: {str(e)}]"
        finally:
            # restore current locale
            try:
                locale.setlocale(locale.LC_ALL, current_locale or '')
            except locale.Error:
                pass

    except Exception as e:
        return f"[Error: {str(e)}]"

def parse_stroke_pattern(key: Union[str, Tuple[str, ...], List[str]]) -> Optional[str]:
    """Parse a stroke pattern and return the formatted time.
    
    Args:
        key: The stroke pattern to parse
        
    Returns:
        Optional[str]: The formatted time string or None if invalid pattern
    """
    try:
        if not isinstance(key, (tuple, list)) or not key:
            return None

        # Extract base stroke and modifiers
        base_stroke = key[0]
        modifiers = key[1:] if len(key) > 1 else []
        
        # Check for any unrecognized modifiers - they act as force exit
        for mod in modifiers:
            if mod not in MODIFIERS:
                save_state(0)  # Reset state
                return None
        
        # Calculate offset from modifiers using sum()
        day_offset = sum(MODIFIERS.get(mod, 0) for mod in modifiers)
        
        # Save the current offset state
        save_state(day_offset)
        
        # Handle different stroke patterns
        if base_stroke in STROKE_PATTERNS:
            format_str, _ = STROKE_PATTERNS[base_stroke]
            # Use the current offset only, don't add stored state
            return format_time(format_str, 'de_DE', day_offset)
        
        return None

    except Exception:
        return None

def lookup(key: Union[str, Tuple[str, ...], List[str]]) -> Optional[str]:
    """Lookup function for Plover dictionary interface.
    
    Args:
        key: Either a string format ('time:format>>locale') or a stroke pattern
        
    Returns:
        Optional[str]: The formatted time string or None if invalid input
    """
    try:
        # Handle string format (time:format>>locale)
        if isinstance(key, str):
            parts = key.split(':')
            if len(parts) != 2 or parts[0] != 'time':
                return None

            formatting = parts[1]
            # Check for locale in the format string (format>>locale)
            locale_parts = formatting.split('>>')
            if len(locale_parts) > 1:
                formatting, locale_setting = locale_parts
                if not locale_setting:  # Handle empty locale
                    locale_setting = 'de_DE'
            else:
                locale_setting = 'de_DE'

            return format_time(formatting, locale_setting)
        
        # Handle stroke pattern
        return parse_stroke_pattern(key)

    except Exception:
        return None

def reverse_lookup(text: str) -> List[str]:
    """Reverse lookup function for Plover dictionary interface.
    
    Args:
        text: The text to look up
        
    Returns:
        List[str]: Empty list as reverse lookup is not supported
    """
    return []
