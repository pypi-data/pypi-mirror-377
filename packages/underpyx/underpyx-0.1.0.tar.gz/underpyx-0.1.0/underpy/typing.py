from typing import Union, List, Dict

JSON = Union[
    str,
    int,
    float,
    bool,
    None,
    Dict[str, "JSON"],
    List["JSON"]
]