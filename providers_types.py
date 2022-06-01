from typing import TypedDict, List, Tuple

class Provider(TypedDict):
    """typing of an individual provider"""
    id: int
    first_name: str
    last_name: str
    sex: str
    birth_date: str
    rating: float
    primary_skills: List[str]
    secondary_skills: List[str]
    company: str
    active: bool
    country: str
    language: str

class Filter_Options(TypedDict, total=False):
    """Typing to be used with Provider_list.filter() for what traits to filter by"""
    id: Tuple[str, int]
    first_name: str
    last_name: str
    sex: str
    birth_date: Tuple[str, str]
    rating: Tuple[str, float]
    primary_skills: List[str]
    secondary_skills: List[str]
    company: str
    active: bool
    country: str
    language: str