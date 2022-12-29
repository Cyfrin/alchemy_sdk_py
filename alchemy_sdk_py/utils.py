from typing import Union


def is_hex_int(string: str) -> bool:
    """
    params:
        string: String to check
    returns:
        True if string is a hex int, False otherwise
    """
    if not type(string) == str:
        return False
    try:
        int(string, 16)
        return True
    except ValueError:
        return False


class HexIntStringNumber:
    def __init__(self, stringIntNumber: Union[str, int, None]):
        self.hex_string = (
            hex(stringIntNumber) if not is_hex_int(stringIntNumber) else stringIntNumber
        )
        self.int: int = int(self.hex_string, 16)
        self.int_string: str = str(self.int)

    def __str__(self) -> str:
        return self.int_string

    def __eq__(self, other: Union[str, int, any, None]) -> bool:
        if isinstance(other, HexIntStringNumber):
            return self.int == other.int
        else:
            HexIntStringNumber(other).int == self.int

    @property
    def hex(self) -> str:
        return self.hex_string

    @property
    def int_number(self) -> int:
        return self.int

    @property
    def str(self) -> str:
        return self.int_string

    @property
    def hexString(self) -> str:
        return self.hex_string
