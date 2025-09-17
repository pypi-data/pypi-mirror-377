"""
Known Kix API endpoints
"""

from enum import Enum


class FridaEndpoint(Enum):
    """
    Known Kix API endpoints. These addresses may change as long as the new address has not less capabilites than the previous one.
    """
    DEV = "https://frida-roles.fraunhofer.de/api"
    PROD = "https://frida-roles.fraunhofer.de/api"

    def __str__(self) -> str:
        return self.value
