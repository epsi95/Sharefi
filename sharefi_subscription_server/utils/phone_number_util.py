from typing import Any, Union

import phonenumbers
from phonenumbers import PhoneNumber


def is_valid_number(number):
    try:
        phoneNumber = phonenumbers.parse(number, "IN")
        if phonenumbers.is_possible_number(phoneNumber):
            return [True, phoneNumber.national_number]
        else:
            return [False, -1]

    except Exception as e:
        print(e)
        return [False, -1]


if __name__ == "__main__":
    example_1 = "+91 6578155674"
    print(is_valid_number(example_1))

    example_2 = "qwertyuiop"
    print(is_valid_number(example_2))

    example_3 = "01234"
    print(is_valid_number(example_3))

    example_4 = ";9754877125"
    print(is_valid_number(example_4))

    example_4 = None
    print(is_valid_number(example_4))
