from dataclasses import dataclass
from typing import Dict, Optional, Any

@dataclass
class Prices:
    byn: Optional[str] = None
    usd: Optional[str] = None
    per_meter: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Prices':
        return cls(
            byn=data.get('byn'),
            usd=data.get('usd'),
            per_meter=data.get('per_meter')
        )

@dataclass
class ListingItem:
    id: str
    parameters: str
    prices: Prices
    address: str
    photo_url: str
    area: Optional[float] = None  # Площадь в м²

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListingItem':
        return cls(
            id=data['id'],
            parameters=data['parameters'],
            prices=Prices.from_dict(data['prices']),
            address=data['address'],
            photo_url=data['photo_url'],
            area=data.get('area')  # Площадь может отсутствовать в старых данных
        )

