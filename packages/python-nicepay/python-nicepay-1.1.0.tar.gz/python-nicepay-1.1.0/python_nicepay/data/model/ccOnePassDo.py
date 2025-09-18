import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CCOnePassDo():
    amt: int
    referenceNo: str
    instmntType: str
    instmntMon: str
    onePassToken: str
    cardCvv: str
    recurrOpt: str
    payMethod: str = "01"

    def to_dict(self) -> dict:
        """Convert the dataclass to a Python dict."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert the dataclass to a JSON string for the 'jsonData' field."""
        return json.dumps(self.__dict__)
