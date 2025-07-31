from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union, TypeVar, Type

from flask import Response, jsonify, make_response, abort
from jsonschema import validate
from jsonschema.exceptions import ValidationError

T = TypeVar("T")

"""
Abstract classes for Query and Response formatters / parsers.
"""


@dataclass
class APIResponse(ABC):
    status_code: int = 200
    status: str = "OK"

    def get_response_data(self) -> Union[dict, None]:
        return None

    def make_response(self) -> Response:
        data = self.get_response_data()
        if data is None:
            response_body = ""
        else:
            response_body = jsonify(**data)
        response = make_response(response_body)
        response.status_code = self.status_code
        response.status = f"{self.status_code:03d} {self.status}"
        return response


@dataclass
class APIErrorResponse(APIResponse):
    status_code: int = 400
    status: str = "Client Error"
    error_message: str = None
    error_data: dict = field(default_factory=dict)

    def get_response_data(self) -> Union[dict, None]:
        error_message = self.error_message or self.status
        return {"error message": error_message} | self.error_data


@dataclass
class APIQuery(ABC):
    @classmethod
    def parse(cls: Type[T], payload) -> T:
        try:
            validate(instance=payload, schema=cls.get_json_schema())
            cls.additional_validation(payload)
        except (ValidationError, AssertionError) as e:
            abort(400, str(e))
        return cls.dispatch_data(payload)

    @staticmethod
    @abstractmethod
    def get_json_schema() -> dict:
        pass

    @staticmethod
    def additional_validation(payload):
        pass

    @classmethod
    @abstractmethod
    def dispatch_data(cls: Type[T], payload) -> T:
        pass
