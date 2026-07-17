"""Module defining DBConnectionParameters dataclass."""

from dataclasses import dataclass


@dataclass
class DBConnectionParameters:
    """Dataclass for storing database connection parameters."""

    dialect: str
    driver: str
    user: str
    password: str
    address: str
    port: int
    db_name: str
