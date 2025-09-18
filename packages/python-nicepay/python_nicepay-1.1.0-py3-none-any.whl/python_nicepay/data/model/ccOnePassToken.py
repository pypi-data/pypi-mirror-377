import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CCOnePassToken:
    iMid: str
    referenceNo: str
    amt: int
    cardNo: str
    cardExpYymm: str
    cardHolderEmail: Optional[str] = None
    cardHolderNm: Optional[str] = None
    merchantToken: Optional[str] = None

    def to_json(self) -> str:
        """Convert the dataclass to a JSON string for the 'jsonData' field."""
        return json.dumps(self.__dict__)

    def to_form_payload(self) -> dict:
        """Return payload dictionary with jsonData as JSON string."""
        return {
            "jsonData": json.dumps(asdict(self))
        }
