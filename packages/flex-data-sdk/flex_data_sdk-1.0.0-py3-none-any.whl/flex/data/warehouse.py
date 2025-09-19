"""
Functions for reading SQL queries from the azure SQL warehouse.

All functions will authenticate using Azure Default Credentials. If you are
are working locally the easiest way to set this up is to raise a ticket for
Azure CLI to be installed and set up on your machine. For more complex cases
like authenticating on a remote application, see Azure's own
[docs](https://learn.microsoft.com/en-us/dotnet/api/azure.identity.defaultazurecredential)
"""

import struct
import pyodbc
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, Connection

import pandas as pd

from azure.identity import DefaultAzureCredential


def azure_connection(server: str, database: str) -> Engine:  # pragma: no cover
    """
    Build an azure connection with Default Credential authentication
    """
    possible_drivers: list = [
        i for i in pyodbc.drivers() if "SQL Server" in i and i != "SQL Server"
    ]
    if len(possible_drivers) == 0:
        msg = (
            "No compatible MSSQL driver could be found on this device.\n"
            "(note that 'SQL Server' itself does not support active directory "
            "connection)\n\n"
            "Consider raising a ticket to have SQL Server 17, 18 or later installed."
        )
        raise RuntimeError(msg)
    driver: str = possible_drivers[0].replace(" ", "+")
    engine: Engine = create_engine(
        f"mssql+pyodbc://@{server}/{database}?driver={driver}"
    )
    credentials = DefaultAzureCredential()

    @event.listens_for(engine, "do_connect")
    def inject_token(dialect, conn_rec, cargs, cparams) -> None:
        del dialect, conn_rec
        cargs[0] = cargs[0].replace(";Trusted_Connection=Yes", "")
        token_bytes = credentials.get_token(
            "https://database.windows.net/.default"
        ).token.encode("UTF-16-LE")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s", len(token_bytes), token_bytes
        )
        cparams["attrs_before"] = {1256: token_struct}

    return engine


def query(
    sql: str,
    server: str | None = None,
    database: str | None = None,
    connection: Engine | Connection | str | None = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Run and return the results of a database query for the Azure SQL Warehouse.

    Additional keyword arguments will be passed down to pandas' `read_sql`.

    Note, unless other keyword arguments are passed down, a pyarrow dtype_backend will
    be used by default.

    Connection is an optional parameter to allow for the use of a
    pre-existing connection so doing batch queries is more efficient.
    Use connection with context handler to ensure connection is closed.
    """
    if not ((server and database) or connection):
        raise ValueError(
            "Either sever and database, "
            "or existing connection must be given to connect to SQL"
        )

    kwargs = kwargs or {"dtype_backend": "pyarrow"}
    return pd.read_sql(
        sql,
        con=connection or azure_connection(str(server), str(database)),
        **kwargs,
    )
