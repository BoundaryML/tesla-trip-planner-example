###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401
# flake8: noqa: E501,F401
# pylint: disable=unused-import,line-too-long
# fmt: off
import baml_py
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Dict, Generic, List, Literal, Optional, TypeVar, Union, TypeAlias


T = TypeVar('T')
CheckName = TypeVar('CheckName', bound=str)

class Check(BaseModel):
    name: str
    expression: str
    status: str

class Checked(BaseModel, Generic[T,CheckName]):
    value: T
    checks: Dict[CheckName, Check]

def get_checks(checks: Dict[CheckName, Check]) -> List[Check]:
    return list(checks.values())

def all_succeeded(checks: Dict[CheckName, Check]) -> bool:
    return all(check.status == "succeeded" for check in get_checks(checks))



class CityState(BaseModel):
    city: str
    state: str

class Resume(BaseModel):
    name: str
    email: str
    experience: List[str]
    skills: List[str]

class Stop(BaseModel):
    type: Union[Literal["charging"], Literal["overnight"]]
    location: Union["CityState", "ZipCode"]
    reason: str

class Trip(BaseModel):
    name: str
    start: Union["CityState", "ZipCode"]
    end: Union["CityState", "ZipCode"]
    type: Union[Literal["business"], Literal["personal"]]
    stops: List["Stop"]

class ZipCode(BaseModel):
    zip_code: str
