import datetime
import locale

def meta(ctx, cmdline):
    action = ctx.new_action()
    action.text = time(cmdline)
    return action

def time(formatting):
    fmt, *set_locale = formatting.split('>>')

    # save current locale to restore it later
    current_locale = locale.getlocale()[0]

    # Handle locale and get modifiers if any
    locale_setting = None
    modifiers = []
    day_offset = 0

    if set_locale:
        # Check for |+n syntax
        if '|' in set_locale[0]:
            locale_part, offset_part = set_locale[0].split('|')
            locale_setting = locale_part
            if offset_part.startswith('+'):
                try:
                    day_offset = int(offset_part[1:])
                except ValueError:
                    print(f"Invalid offset format: {offset_part}")
            elif offset_part.startswith('-'):
                try:
                    day_offset = int(offset_part)  # minus sign is already included
                except ValueError:
                    print(f"Invalid offset format: {offset_part}")
        else:
            # Handle original / syntax for modifiers
            parts = set_locale[0].split('/')
            locale_setting = parts[0]
            modifiers = parts[1:] if len(parts) > 1 else []

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

        # Set locale
        if locale_setting == 'de_DE':
            locale.setlocale(locale.LC_ALL, 'de_DE')
        elif locale_setting == 'en_GB':
            locale.setlocale(locale.LC_ALL, 'en_GB')
        else:
            try:
                print("Try setting locale to " + locale_setting)
                locale.setlocale(locale.LC_ALL, locale_setting)
            except locale.Error:
                print("Locale " + locale_setting + " not found")
                print("Current locale is " + current_locale)
                print(locale.getlocale())
                alllocale = locale.locale_alias
                for k in alllocale.keys():
                    print('locale[%s] %s' % (k, alllocale[k]))
                return
            print(locale_setting)
    else:
        print(current_locale + " is the current locale")
        print(locale.getlocale())

    # Get current time and apply offset
    now = datetime.datetime.now()
    if day_offset != 0:
        now = now + datetime.timedelta(days=day_offset)

    # Replace %W with %V for ISO week numbers (01-53)
    if 'KW %W' in fmt:
        # Get ISO week number
        iso_year, iso_week, iso_day = now.isocalendar()
        # Replace %W with the actual ISO week number
        fmt = fmt.replace('KW %W', f'KW {iso_week:02d}')

    formatted = now.strftime(fmt)

    # restore current locale
    locale.setlocale(locale.LC_ALL, current_locale)

    return formatted
