# PIKA Marker Python
Python package to write PIKA marker files with timestamps.


# Installation

```
pip install -e .
```

## Usage 

In your Python code you can use the static function `appendPikaMarker` or create a `PikaMarker` object
to write into a marker file

```
from pika_marker import PikaMarker, appendPikaMarker

appendPikaMarker(
    "marker_file.csv",
    "my_marker",
    additional="additional info",
    icon="🔥",
    timestamp=None
)


marker = PikaMarker("marker_file.csv")
marker.appendMarker(
    "marker 2",
    additional="first marker from object",
    icon="🔥"
)
marker.close()
```

It also provides a CLI tool `append-pika-marker`

```
append-pika-marker --help             
usage: append-pika-marker [-h] [-a ADDITIONAL] [-i ICON] [-t TIMESTAMP] file name

Append a PIKA marker to a marker file.

positional arguments:
  file                  Path to the marker file
  name                  Name of the marker

options:
  -h, --help            show this help message and exit
  -a, --additional ADDITIONAL
                        Additional text
  -i, --icon ICON       Icon or emoji
  -t, --timestamp TIMESTAMP
                        Unix timestamp (defaults to current time)
```
