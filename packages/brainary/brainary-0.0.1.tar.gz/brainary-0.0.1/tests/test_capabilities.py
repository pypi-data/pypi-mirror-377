import logging

from brainary.capabilities.registry import CAPABILITIES

logging.basicConfig(level=logging.INFO)

print(CAPABILITIES["critical_thinking"].list_all())