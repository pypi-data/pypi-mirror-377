import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CCMigsRequest:
    instmntType : str
    instmntMon: str
    referenceNo: str
    onePassToken: str
    callbackUrl: str
    cardCvv: str
    
    def to_json(self) -> str:
        """Convert the dataclass to a JSON string for the 'jsonData' field."""
        return json.dumps(self.__dict__)

    def to_form_payload(self) -> dict:
        """Return payload dictionary with jsonData as JSON string."""
        return {
            "jsonData": json.dumps(asdict(self))
        }
