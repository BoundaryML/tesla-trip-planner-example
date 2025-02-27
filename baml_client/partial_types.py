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
from typing import Dict, List, Optional, Union, Literal

from . import types
from .types import Checked, Check

###############################################################################
#
#  These types are used for streaming, for when an instance of a type
#  is still being built up and any of its fields is not yet fully available.
#
###############################################################################


class CityState(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None

class Resume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    experience: List[Optional[str]]
    skills: List[Optional[str]]

class Stop(BaseModel):
    type: Optional[Union[Literal["charging"], Literal["overnight"]]] = None
    location: Optional[Union["CityState", "ZipCode"]] = None
    reason: Optional[str] = None

class Trip(BaseModel):
    name: Optional[str] = None
    start: Optional[Union["CityState", "ZipCode"]] = None
    end: Optional[Union["CityState", "ZipCode"]] = None
    type: Optional[Union[Literal["business"], Literal["personal"]]] = None
    stops: List["Stop"]

class ZipCode(BaseModel):
    zip_code: Optional[str] = None
