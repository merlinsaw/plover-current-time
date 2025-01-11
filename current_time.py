import datetime
import locale
import json
import os
import logging

# Set up logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'current_time.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize state files
STATE_FILE = os.path.join(os.path.dirname(__file__), 'date_state.json')
OFFSET_FILE = os.path.join(os.path.dirname(__file__), 'date_offset.json')

def initialize_state():
    """Initialize or reset state files"""
    try:
        # Initialize date_state.json if it doesn't exist or is invalid
        if not os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'w') as f:
                json.dump({'day_offset': 0}, f)
        
        # Initialize date_offset.json if it doesn't exist or is invalid
        if not os.path.exists(OFFSET_FILE):
            with open(OFFSET_FILE, 'w') as f:
                json.dump({'offset': 0}, f)
                
        logging.info("State files initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing state files: {str(e)}")

def meta(ctx, cmdline):
    """Main entry point for Plover"""
    try:
        # Ensure state is initialized
        initialize_state()
        
        action = ctx.new_action()
        action.text = time(cmdline)
        return action
    except Exception as e:
        logging.error(f"Error in meta function: {str(e)}")
        raise

def time(formatting):
    """Format time with optional locale and modifiers"""
    try:
        fmt, *set_locale = formatting.split('>>')

        # save current locale to restore it later
        current_locale = locale.getlocale()[0]
        logging.debug(f"Current locale: {current_locale}")

        # Handle locale and get modifiers if any
        locale_setting = None
        day_offset = 0

        if set_locale:
            locale_part = set_locale[0]
            
            # Handle direct offset syntax (|+n or |-n)
            if '|' in locale_part:
                locale_setting, offset_part = locale_part.split('|')
                try:
                    day_offset = int(offset_part)  # Will handle both +n and -n
                    logging.debug(f"Direct offset applied: {day_offset}")
                except ValueError:
                    logging.error(f"Invalid offset format: {offset_part}")
            
            # Handle modifier syntax (U, E, O, A)
            else:
                parts = locale_part.split('/')
                locale_setting = parts[0]
                modifiers = parts[1:] if len(parts) > 1 else []
                logging.debug(f"Modifiers found: {modifiers}")

                # Calculate offset from modifiers
                for mod in modifiers:
                    if mod == 'U':  # Forward one day (+1)
                        day_offset += 1
                    elif mod == 'E':  # Backward one day (-1)
                        day_offset -= 1
                    elif mod == 'O':  # Forward one week (+7)
                        day_offset += 7
                    elif mod == 'A':  # Backward one week (-7)
                        day_offset -= 7
                logging.debug(f"Total modifier offset: {day_offset}")

            # Set locale
            if locale_setting:
                try:
                    if locale_setting == 'de_DE':
                        locale.setlocale(locale.LC_ALL, 'de_DE')
                    elif locale_setting == 'en_GB':
                        locale.setlocale(locale.LC_ALL, 'en_GB')
                    else:
                        locale.setlocale(locale.LC_ALL, locale_setting)
                    logging.debug(f"Locale set to: {locale_setting}")
                except locale.Error as e:
                    logging.error(f"Failed to set locale {locale_setting}: {str(e)}")
                    return f"[Locale Error: {locale_setting}]"

        # Get current time and apply offset
        now = datetime.datetime.now()
        if day_offset != 0:
            now = now + datetime.timedelta(days=day_offset)
            logging.debug(f"Applied time offset: {day_offset} days")

        # Replace %W with %V for ISO week numbers (01-53)
        if 'KW %W' in fmt:
            iso_year, iso_week, iso_day = now.isocalendar()
            fmt = fmt.replace('KW %W', f'KW {iso_week:02d}')

        formatted = now.strftime(fmt)
        logging.debug(f"Formatted output: {formatted}")

        # restore current locale
        locale.setlocale(locale.LC_ALL, current_locale)

        return formatted
    except Exception as e:
        logging.error(f"Error in time function: {str(e)}")
        return f"[Error: {str(e)}]"

# Initialize state when module is loaded
initialize_state()
