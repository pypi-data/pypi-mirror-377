from typing import Optional

from dataclasses_json import dataclass_json
from pydantic.dataclasses import Field, dataclass

from pmr_elirobots_msgs.header import Header


@dataclass_json
@dataclass
class JointCommand:
    """Position command to robot joints"""

    joint1: Optional[float] = None
    joint2: Optional[float] = None
    joint3: Optional[float] = None
    joint4: Optional[float] = None
    joint5: Optional[float] = None
    joint6: Optional[float] = None

    @property
    def as_list(self):
        return [
            self.joint1,
            self.joint2,
            self.joint3,
            self.joint4,
            self.joint5,
            self.joint6,
        ]

    def to_json(self):
        pass

    def from_json(self):
        pass


@dataclass_json
@dataclass
class JointCommandMsg:
    """Joint command with message header"""

    cmd: JointCommand = Field(default_factory=JointCommand)
    header: Header = Field(default_factory=Header)

    def to_json(self, *args) -> str:
        return ""

    @classmethod
    def from_json(cls, *args):
        return cls()
