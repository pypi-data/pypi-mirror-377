import io
import time
from typing import Union


class PikaMarker:
    """Helper class for writing marker lines to a PIKA marker file.

    This class manages a file handle and provides a convenient method
    to append formatted marker lines. The file is opened in append mode
    on initialization and closed automatically on deletion.

    Example:
        >>> marker = PikaMarker("markers.log")
        >>> marker.appendMarker("start", "initialization", "🚀")
        >>> marker.close()
    """

    def __init__(self, path: str):
        """Create a new marker file for PIKA.

        Args:
            path (str): Path to the marker file. The file is opened in
                append mode with UTF-8 encoding.
        """
        self.path = path
        self.file = open(path, "a", encoding="utf-8")
    
    def appendMarker(self, name: str, additional: str, icon: str, timestamp: float=None):
        """Append a formatted marker line to the file.

        Args:
            name (str): The marker name.
            additional (str): Optional additional information.
            icon (str): An optional icon (e.g., emoji or symbol).
            timestamp (float, optional): UNIX timestamp. If ``None``,
                the current time is used.
        """
        appendPikaMarker(self.file, name, additional, icon, timestamp)

    def close(self):
        """Close the file if it’s open."""
        if self.file:
            self.file.close()
            self.file = None

    def __del__(self):
        """Ensure the file is closed on deletion."""
        self.close()


def appendPikaMarker(fp_or_path: Union[str, io.TextIOBase], name: str, additional: str="", icon: str="", timestamp: float=None):
    """Append a marker line to a file or file-like object.

    The marker line is written in CSV format:

    ```
    <timestamp>,"<icon>","<name>","<additional>"
    ```

    If a file path is given, the file is opened in append mode. If a file
    object is provided, the marker is written directly.

    Args:
        fp_or_path (Union[str, io.TextIOBase]): File path or open text
            file object to append to.
        name (str): The marker name.
        additional (str, optional): Additional information (default: ``""``).
        icon (str, optional): Icon or symbol associated with the marker
            (default: ``""``).
        timestamp (float, optional): UNIX timestamp. If ``None``,
            the current time is used.

    Raises:
        ValueError: If ``fp_or_path`` is not a string or a file-like object.
    """
    if timestamp is None:
        timestamp = time.time()    
    line = f'{timestamp},"{icon}","{name}","{additional}"\n'

    if isinstance(fp_or_path, io.TextIOBase):
        fp_or_path.write(line)
    elif isinstance(fp_or_path, str):
        with open(fp_or_path, "a", encoding="utf-8") as fh:
            fh.write(line)
    else:
        raise ValueError("fp_or_path must be a file path (str) or a file pointer (TextIOBase)")            
