from typing import Dict, List

from models.option import Option


def from_list_to_dict_option(options: List[Option]) -> Dict[str, Option]:
    options = {str(i + 1): (options[i]) for i in range(len(options))}
    return options
