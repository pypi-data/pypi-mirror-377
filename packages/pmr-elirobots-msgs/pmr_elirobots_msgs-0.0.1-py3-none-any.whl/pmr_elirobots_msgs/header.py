from pydantic.dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Header:
    """Simple msgs header"""

    timestamp: datetime = datetime.now()

    def to_json(self):
        pass

    def from_json(self):
        pass
