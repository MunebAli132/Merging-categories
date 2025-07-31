from dataclasses import dataclass, field
from typing import Union, TypeVar, List, Optional, Dict, Type

from category_merger.api_utils import APIQuery, APIResponse

T = TypeVar("T")


@dataclass
class Category:
    id: int
    label: str
    parent_id: Optional[int]
    count: int


# global variable simulating external storage
categories: Dict[int, Category] = {}  # {Id: Category}


@dataclass
class CategoryInsertQuery(APIQuery):
    id: int = None
    label: str = None
    count: int = None
    parent: Optional[int] = None

    @staticmethod
    def get_json_schema() -> dict:
        return {
            "type": "object",
            "properties": {
                "Id": {"type": "integer"},
                "Label": {"type": "string"},
                "Count": {"type": "integer"},
                "Parent": {"type": "integer"},
            },
            "required": ["Id", "Count"],
            "additionalProperties": False,
        }

    @classmethod
    def dispatch_data(cls: Type[T], payload) -> T:
        return cls(
            id=payload["Id"],
            label=payload.get("Label", ""),
            count=payload["Count"],
            parent=payload.get("Parent", None),
        )


@dataclass
class CategoryItemResponse(APIResponse):
    id: int = None
    label: str = None
    count: int = None
    parent: Optional[int] = None
    children: List[int] = field(default_factory=list)
    just_deleted: bool = False

    @classmethod
    def from_category(cls, category: Category):
        return cls(id=category.id, label=category.label, count=category.count, parent=category.parent_id)

    def get_response_data(self) -> Union[dict, None]:
        if self.just_deleted:
            self.status_code = 204
            self.status = "No Content: Deleted."
            return None
        else:
            return {
                "Id": self.id,
                "Label": self.label,
                "Count": self.count,
                "Parent": self.parent,
                "Children": [],
            }


@dataclass
class CategoryListResponse(APIResponse):
    ids: List[int] = None

    def get_response_data(self) -> Union[dict, None]:
        return {"CategoryIds": self.ids}




