from dataclasses import dataclass, field
from typing import Any


@dataclass
class Currencies:
    keys: int = 0
    metal: float = 0.0


@dataclass
class Entity:
    name: str = ""
    id: int = 0
    color: str = ""


@dataclass
class ItemDocument:
    appid: int
    baseName: str
    defindex: int
    id: str
    imageUrl: str
    marketName: str
    name: str
    # origin: None
    originalId: str
    price: dict
    quality: Entity
    summary: str
    # class: list
    slot: str
    tradable: bool
    craftable: bool


@dataclass
class Listing:
    id: str
    steamid: str
    appid: int
    currencies: dict[str, Any]
    value: dict
    details: str
    listedAt: int
    bumpedAt: int
    intent: str
    count: int
    status: str
    source: str
    item: dict[str, Any]
    user: dict = field(default_factory=dict)  # Made optional for API compatibility
    userAgent: dict = field(default_factory=dict)
    tradeOffersPreferred: bool = None
    buyoutOnly: bool = None
    archived: bool = field(default=False)  # Added for API compatibility
