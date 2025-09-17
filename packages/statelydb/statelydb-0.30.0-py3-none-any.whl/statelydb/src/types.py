"""Shared types for the Stately Cloud SDK."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import TYPE_CHECKING, Callable, TypeVar, Union
from uuid import UUID

from grpclib import Status
from typing_extensions import Self

from statelydb.src.errors import StatelyError

if TYPE_CHECKING:
    from google.protobuf.message import Message

    from statelydb.lib.api.db.item_pb2 import Item as PBItem

StoreID = int
SchemaVersionID = int
SchemaID = int

AllKeyTypes = Union[UUID, str, int, bytes]
AnyKeyType = TypeVar("AnyKeyType", bound=AllKeyTypes)

Stopper = Callable[[], None]


class StatelyObject(ABC):
    """All generated object types must implement the StatelyObject interface."""

    @abstractmethod
    def marshal(self) -> Message:
        """Marshal the StatelyObject to its corresponding proto message."""

    @staticmethod
    @abstractmethod
    def unmarshal(proto_bytes: bytes | Message) -> StatelyObject:
        """Unmarshal proto bytes or message into their corresponding StatelyObject."""


class StatelyItem(ABC):
    """All generated item types must implement the StatelyItem interface."""

    # this is set during unmarshalling to ensure that the key path
    # is not changed during the lifetime of the object.
    # You can see the check below in the marshal method.
    _primary_key_path: str | None = None

    def __init__(self) -> None:
        """
        Constructor for StatelyItem. This runs any setup that is common to
        all StatelyItems.
        """
        self._primary_key_path = None

    @abstractmethod
    def key_path(self) -> str:
        """Returns the Key Path of the current Item."""

    @abstractmethod
    def marshal(self) -> PBItem:
        """Marshal the StatelyItem to a protobuf Item."""

    def check_item_key_reuse(self) -> None:
        """Verify that the Key Path of the Item has not changed since it was read from StatelyDB."""
        if (
            self._primary_key_path is not None
            and self._primary_key_path != self.key_path()
        ):
            msg = (
                f'{self.item_type()} was read with Key Path: "{self._primary_key_path}" '
                f'but is being written with Key Path: "{self.key_path()}". '
                f"If you intend to move your {self.item_type()}, you should delete the "
                f"original and create a new one. If you intend to create a new {self.item_type()} "
                f"with the same data, you should create a new instance of {self.item_type()} "
                "rather than reusing the read result."
            )
            raise StatelyError(
                stately_code="ItemReusedWithDifferentKeyPath",
                code=3,  # InvalidArgument
                message=msg,
            )

    @staticmethod
    @abstractmethod
    def unmarshal(proto_bytes: bytes) -> StatelyItem:
        """Unmarshal proto bytes into their corresponding StatelyItem."""

    @staticmethod
    @abstractmethod
    def item_type() -> str:
        """Return the type of the item."""


class BaseTypeMapper(ABC):
    """
    TypeMapper is an interface that is implemented by Stately generated schema code
    unmarshalling concrete Stately schema from generic
    protobuf items that are received from the API.
    """

    @staticmethod
    @abstractmethod
    def unmarshal(item: PBItem) -> StatelyItem:
        """Unmarshal a generic protobuf item into a concrete schema type."""


class StatelyEnum(IntEnum):
    """
    Base class for a custom int-based enum that supports undefined values
    and is compatible with static type checkers. This allows it to be forwards compatible
    with new enum values added in the Stately schema.
    """

    @classmethod
    def _missing_(cls, value: object) -> Self:
        """Handle creation of enum instances with undefined values."""
        if isinstance(value, int):
            # Create a pseudo-member for undefined values using int.__new__
            # This never goes in _members_ so it is not a "real" member
            # and is not returned by iteration or .all()
            pseudo_member = int.__new__(cls, value)

            # I chose to use _{value} instead of None because _name_ is supposed
            # to be a string and I don't want to break code that expects it to
            # be there. One of the benefits of this approach is that Stately
            # enums are children of the built-in IntEnum so they will hopefully
            # work naturally in places.
            #
            # we don't allow a number for an enum value in a stately schema so
            # there is no risk of a collision. We prefix with _ just to be sure.
            pseudo_member._name_ = f"_{value}"
            pseudo_member._value_ = value
            return pseudo_member
        # if the value is not an int, we pass through to the default handler
        # which will raise the appropriate error
        return super()._missing_(value)

    def is_known(self) -> bool:
        """
        Check if the current StatelyEnum instance is a known enum member from
        the set. This will be false for any values that are not defined in the
        class definition.
        """
        return not self._name_.startswith("_")

    @classmethod
    def all(cls: type[Self]) -> list[Self]:
        """Return a list of all valid enum instances."""
        return list(cls)

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        # For valid enum members, use the name
        if self.is_known():
            return self._name_
        # For invalid values, show as unknown
        return f"UnknownEnumValue_({int(self.value)})"

    @classmethod
    def from_string(cls: type[Self], name: str) -> Self:
        """Create an enum instance from its string name."""
        try:
            return cls[name]
        except KeyError as e:
            msg = f"{name} is not a valid name for enum {cls.__name__}"
            raise StatelyError(
                message=msg,
                stately_code="InvalidArgument",
                code=Status.INVALID_ARGUMENT,
            ) from e
