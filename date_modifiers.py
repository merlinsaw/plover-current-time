import datetime
import locale
import json
import os
import logging


DEBUG = False # if false disable logging
# Set up logging with fallback for __file__
try:
    log_path = os.path.join(os.path.dirname(__file__), 'date_modifiers.log')
except NameError:
    log_path = os.path.join(os.getcwd(), 'date_modifiers.log')

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define the maximum number of strokes in any translation
LONGEST_KEY = 52  # Base stroke plus 51 modifiers


# Modifier mapping
MODIFIERS = {
    'U': 1,    # Forward one day
    'E': -1,   # Backward one day
    'O': 7,    # Forward one week
    'A': -7    # Backward one week
}

def format_time(formatting, locale_setting='de_DE'):
    """Format time with optional locale and modifiers"""
    try:
        # save current locale to restore it later
        current_locale = locale.getlocale()[0]
        if DEBUG:
            logging.debug(f"Current locale: {current_locale}")

        # Set locale
        try:
            locale.setlocale(locale.LC_ALL, locale_setting)
            if DEBUG:
                logging.debug(f"Locale set to: {locale_setting}")
        except locale.Error as e:
            logging.error(f"Failed to set locale {locale_setting}: {str(e)}")
            return f"[Locale Error: {locale_setting}]"

        # Get current time
        now = datetime.datetime.now()
        
        # Use ISO week number directly
        if 'KW %W' in formatting:
            iso_year, iso_week, iso_day = now.isocalendar()
            formatting = formatting.replace('KW %W', f'KW {iso_week:02d}')
            if DEBUG:
                logging.debug(f"ISO week number: {iso_week}")

        formatted = now.strftime(formatting)
        if DEBUG:
            logging.debug(f"Formatted output: {formatted}")

        # restore current locale
        locale.setlocale(locale.LC_ALL, current_locale)

        return formatted
    except Exception as e:
        logging.error(f"Error in format_time function: {str(e)}")
        return f"[Error: {str(e)}]"

def lookup(key):
    """Main lookup function for Plover"""
    assert len(key) <= LONGEST_KEY
    
    try:
        # If the last translation ended with {#}, we're in exit state, ignore all strokes
        if len(key) > 1 and '#' in key[:-1]:
            raise KeyError
        
        # Extract base stroke and modifiers
        base_stroke = key[0]
        modifiers = key[1:] if len(key) > 1 else []
        
        # Check if # is in modifiers to force exit
        force_exit = '#' in modifiers
        if force_exit:
            # Remove # from modifiers so it doesn't affect offset
            modifiers = [m for m in modifiers if m != '#']
        
        # Calculate offset from modifiers using sum()
        day_offset = sum(MODIFIERS.get(mod, 0) for mod in modifiers)
        if DEBUG:
            logging.debug(f"Base stroke: {base_stroke}, Modifiers: {modifiers}, Total day offset: {day_offset}")
        
        # Get current time with offset
        now = datetime.datetime.now()
        target_date = now + datetime.timedelta(days=day_offset)
        
        # Handle different stroke patterns
        if base_stroke == 'Z-TZ':
            # ISO format date with offset
            return f"{{^}}{{:time:%Y-%m-%d_>>de_DE|{day_offset}}}"
        elif base_stroke == 'Z-Z':
            # Day of month with locale
            return f"{{^}}{{:time:%A>>de_DE|{day_offset}}}"
        elif base_stroke == 'Z-DZ':
            # Date with time and week number
            iso_year, iso_week, iso_day = target_date.isocalendar()
            return f"{{^}}{{:time:KW %W: %A %d.%m.%Y %H:%M>>de_DE|{day_offset}}}"
        elif base_stroke == 'Z-D':
            # Original date format
            return f"{{^}}{{:time:KW %W: %A %d.%m.%Y>>de_DE|{day_offset}}}"
        
        raise KeyError
    except Exception as e:
        logging.error(f"Error in lookup function: {str(e)}")
        raise KeyError

def reverse_lookup(text):
    """Optional reverse lookup function"""
    # This could be implemented to return steno outlines for given text
    return []

# Basic dictionary interface
if __name__ == "__main__":
    # Test the dictionary functionality
    try:
        print(lookup(('Z-D',)))  # Current date
        print(lookup(('Z-D', 'U')))  # +1 day
        print(lookup(('Z-T-Z',)))  # ISO format
        print(lookup(('Z-Z',)))  # Day of month
        print(lookup(('Z-Z-D',)))  # Date with time
    except KeyError:
        print("Invalid stroke")
