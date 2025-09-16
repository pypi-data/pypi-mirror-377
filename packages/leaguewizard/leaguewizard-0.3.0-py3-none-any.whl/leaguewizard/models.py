from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Payload:
    """Class provides an abstract payload class."""

    def asdict(self) -> dict[str, Any]:
        """Return itself as json.

        Returns:
            dict: Serialized Payload class.

        """
        return asdict(self)


@dataclass
class Payload_ItemSets(Payload):
    """LCU schema used on /lol-item-sets/v1/item-sets/{accountId}/sets dataclass.

    Attributes:
        accountId (type): description
        itemSets (type): description
        timestamp (type): description

    """

    accountId: int
    itemSets: list[ItemSet] | None = None
    timestamp: int = 1


@dataclass
class ItemSet:
    """Summary of ItemSet.

    Attributes:
        associatedChampions (type): description
        blocks (type): description
        title (type): description

    """

    associatedChampions: list[int]
    blocks: list[Block]
    title: str


@dataclass
class Block:
    """Summary of Block.

    Attributes:
        items (type): description
        type (type): description

    """

    items: list[Item]
    type: str


@dataclass
class Item:
    """Summary of Item.

    Attributes:
        count (type): description
        id (type): description

    """

    count: int
    id: str


@dataclass
class Payload_Perks(Payload):
    """Summary of Payload_Perks.

    Attributes:
        name (type): description
        primaryStyleId (type): description
        subStyleId (type): description
        current (type): description
        selectedPerkIds (type): description

    """

    name: str
    primaryStyleId: int
    subStyleId: int
    current: bool
    selectedPerkIds: list[int] | None = None


@dataclass
class Payload_Spells(Payload):
    """Summary of Payload_Spells.

    Attributes:
        spell1Id (type): description
        spell2Id (type): description
        selectedSkinId (type): description

    """

    spell1Id: int
    spell2Id: int
    selectedSkinId: int


@dataclass
class EventSchema:
    """Summary of EventSchema.

    Attributes:
        actions (type): description
        localPlayerCellId (type): description
        myTeam (type): description

    """

    actions: list[Action]
    localPlayerCellId: int
    myTeam: list[Ally]


@dataclass
class Action:
    """Summary of Action.

    Attributes:
        actorCellId (type): description
        championId (type): description
        completed (type): description
        type (type): description

    """

    actorCellId: int
    championId: int
    completed: bool
    type: str


@dataclass
class Ally:
    """Summary of Ally.

    Attributes:
        assignedPosition (type): description
        cellId (type): description
        championId (type): description
        selectedSkinId (type): description
        summonerId (type): description
        wardSkinId (type): description

    """

    assignedPosition: str
    cellId: int
    championId: int
    selectedSkinId: int
    summonerId: int
    wardSkinId: int
