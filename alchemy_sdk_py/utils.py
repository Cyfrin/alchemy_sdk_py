from typing import Union

ETH_NULL_VALUE: str = "0x"


def is_hash(string: str) -> bool:
    """
    params:
        string: String to check
    returns:
        True if string is a hash, False otherwise
    """
    if not type(string) == str:
        return False
    if not string.startswith("0x"):
        return False
    if not len(string) == 66:
        return False
    return True


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


def bytes32_to_text(bytes_to_convert: str) -> str:
    """
    params:
        string: String to convert
    returns:
        String converted to text
    """
    if not isinstance(bytes_to_convert, str):
        raise TypeError("string must be a string")
    bytes_object = bytes.fromhex(bytes_to_convert[2:])  # Strip the "0x" prefix
    null_byte_index = bytes_object.index(b"\x00")  # Find the null byte
    bytes_object = bytes_object[:null_byte_index]  # Strip the null byte
    decoded_string = bytes_object.decode()  # Decode the bytes
    return decoded_string


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
