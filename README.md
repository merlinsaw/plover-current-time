# Current time 1.0.2

> Plover plugin for inserting the current time in an `strftime()` format

This can be used to indicate the current time when writing, useful for keeping track of when a transcription started, or when notible events occur; such as breaks.

## Installation

Install from the Plover plugins manager.

## Usage and Examples

| Dictionary Entry | Description |
| ---- | ---- |
| `"T*EUPL": "{:time:%H:%M:%S}",` | Output current time in 24-Hour format. | 
| `"SO*FL": "{:time:%Y-%m-%dT%H:%M:%S.%f%z}",` | Output current time in ISO-8601 format. | 
| `"TKA*ET": "{:time:%A, %d %B, %Y},"` | Output current date in a nice human readable format. |
| `"PWRAEBG": "\n(break started: {:time:%H:%M:%S}{^})\n",` | Note that a break has started and at what time. |
| `"PWRA*EBG": "\n(break ended: {:time:%H:%M:%S}{^})\n",` | Note that the break has ended and at what time. |

Optionally, you can define a locale to get more specific output. The locale should be available on your system, and it can be specified after the separator `>>`, like this:

| Dictionary Entry | Description |
| ---- | ---- |
| `"TKA*/TUPL": "{:time:%A, %d %B, %Y>>de_DE}",` | Output current date in german. | 
| `"TP*E/KHA": "{:time:%A, %d %B, %Y>>es_ES}",` | Output current date in spanish. | 

## Default Commands and Formats

The plugin comes with several default commands:

| Command | Format | Example Output |
| ---- | ---- | ---- |
| `Z-Z` | `%A` | Donnerstag |
| `Z-TZ` | `%Y-%m-%d_` | 2025-01-09_ |
| `Z-D` | `KW %W: %A %d.%m.%Y` | KW 02: Donnerstag 09.01.2025 |
| `Z-DZ` | `KW %W: %A %d.%m.%Y %H:%M:%S` | KW 02: Donnerstag 09.01.2025 18:34:05 |

Format Specifiers:
- `%Y`: Year with century (e.g., 2025)
- `%m`: Month as zero-padded number (01-12)
- `%d`: Day of the month as zero-padded number (01-31)
- `%A`: Full weekday name (e.g., Donnerstag)
- `%W`: ISO week number (00-53)
- `%H`: Hour (24-hour clock) as zero-padded number (00-23)
- `%M`: Minute as zero-padded number (00-59)
- `%S`: Second as zero-padded number (00-59)

## Date Modifiers

The plugin supports various modifiers for date navigation:

| Modifier | Description |
| ---- | ---- |
| `Z-D/E` | Previous day (-1 day) |
| `Z-D/U` | Next day (+1 day) |
| `Z-D/O` | Next week (+7 days) |
| `Z-D/A` | Previous week (-7 days) |
| `Z-Z/O` | Next week's weekday (+7 days) |
| `Z-Z/A` | Previous week's weekday (-7 days) |

Multiple modifiers can be chained:
- Day navigation: Up to 28 days (e.g., `Z-D/E/E` for -2 days)
- Week navigation: Up to 52 weeks (e.g., `Z-D/O/O` for +14 days)