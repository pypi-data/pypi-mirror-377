"""
Functions for reading date partitioned files from the azure datalake.

All functions will authenticate using Azure Default Credentials. If you are
are working locally the easiest way to set this up is to raise a ticket for
Azure CLI to be installed and set up on your machine. For more complex cases
like authenticating on a remote application, see Azure's own
[docs](https://learn.microsoft.com/en-us/dotnet/api/azure.identity.defaultazurecredential)
"""

from datetime import datetime, timedelta
from typing import Callable
from concurrent import futures

import fsspec
import pandas as pd


def latest(
    path: str,
    as_of: datetime | None = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Read parquet files between dates into a pandas dataframe.

    `as_of` argument supports introducing a ceiling (i.e finding the latest
    file no more recent than 2023-04-01)

    Additional keyword arguments will be passed down to pandas'
    `read_parquet`.

    Note, unless other keyword arguments are passed down, a pyarrow dtype_backend will
    be used by default.
    """
    to_read = _latest_partition_folder(path, as_of or datetime(3000, 1, 1))
    account_name, path = path.split("/", 1)
    fs = fsspec.filesystem(
        "abfs",
        account_name=account_name,
        anon=False,
        use_listing_cache=False,
    )
    fs.clear_instance_cache()
    files = fs.ls(to_read)
    dataframe: pd.DataFrame = _dataframe_from_files(
        files,
        storage_options={
            "account_name": account_name,
            "anon": False,
            "use_listings_cache": False,
        },
        **kwargs,
    )
    return dataframe


def for_date(
    path: str,
    target_date: datetime,
    raise_error_if_missing: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """
    Read parquet files for a given date into a pandas dataframe.

    Any additional kwargs are parsed into pandas' *read_parquet*

    Note, unless other keyword arguments are passed down, a pyarrow dtype_backend will
    be used by default.
    """
    account_name, path = path.split("/", 1)
    fs = fsspec.filesystem(
        "abfs",
        account_name=account_name,
        anon=False,
        use_listing_cache=False,
    )
    fs.clear_instance_cache()
    try:
        files = fs.ls(
            f"{path}/{target_date.strftime('%Y/%m/%d')}",
        )
    except FileNotFoundError:  # pragma: no cover
        files = []
    if len(files) == 0:  # pragma: no cover
        assert not raise_error_if_missing, f"No data in given dates for {path}"
        return pd.DataFrame()
    dataframe = _dataframe_from_files(
        files,
        storage_options={
            "account_name": account_name,
            "anon": False,
            "use_listings_cache": False,
        },
        **kwargs,
    )
    return dataframe


def between_dates(
    path: str,
    from_date: datetime,
    to_date: datetime,
    raise_error_if_missing: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """
    Read parquet files between dates into a pandas dataframe, note that date range will
    be inclusive on both sides (for instance from 2024-03-01 to 2024-03-03 will include
    3 days of data).

    Any additional keyword arguments are passed into pandas `read_parquet`.

    Note, unless other keyword arguments are passed down, a pyarrow dtype_backend will
    be used by default.
    """
    date_range = [
        from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)
    ]
    return for_dates(
        path,
        date_range,
        raise_error_if_missing=raise_error_if_missing,
        **kwargs,
    )


def for_dates(
    path: str,
    dates: list[datetime],
    raise_error_if_missing: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """
    Read parquet files between dates into a pandas dataframe.

    Any additional keyword arguments are passed into pandas `read_parquet`.

    Note, unless other keyword arguments are passed down, a pyarrow dtype_backend will
    be used by default.
    """
    account_name, path = path.split("/", 1)
    paths = [f"{path}/{i.strftime('%Y/%m/%d')}" for i in dates]
    fs = fsspec.filesystem(
        "abfs",
        account_name=account_name,
        anon=False,
        use_listings_cache=False,
    )
    fs.clear_instance_cache()
    files: list[str] = []
    for i_path in paths:
        try:
            files += fs.ls(i_path)
        except FileNotFoundError:  # pragma: no cover
            pass
    if len(files) == 0:  # pragma: no cover
        assert not raise_error_if_missing, f"No data in given dates for {path}"
        return pd.DataFrame()
    dataframe: pd.DataFrame = _dataframe_from_files(
        files,
        storage_options={
            "account_name": account_name,
            "anon": False,
            "use_listings_cache": False,
        },
        **kwargs,
    )
    if raise_error_if_missing:  # pragma: no cover
        assert len(dataframe) != 0, f"No data in given dates for {path}"
    return dataframe


def _latest_partition_folder(
    path: str,
    as_of: datetime,
) -> str:
    """
    Find the latest partition folder within the datalake.

    `as_of` argument supports introducing a ceiling (i.e finding the latest
    file no more recent than 2023-04-01)

    Expect path to be of form:

    account_name/container/datalake/schema/table
    """
    account_name, container_path = path.split("/", 1)
    filesystem = fsspec.filesystem(
        "abfs",
        account_name=account_name,
        anon=False,
        use_listing_cache=False,
    )
    years = [
        i
        for i in filesystem.ls(container_path)
        if i[-4:].isnumeric() and int(i[-4:]) <= as_of.year
    ]
    assert len(years) != 0, "No matching files within given bounds"
    try:
        latest_year = max(years, key=lambda x: int(x[-4:]))
        months = filesystem.ls(latest_year)
        if filter_needed := int(latest_year[-4:]) == as_of.year:
            months = [i for i in months if int(i[-2:]) <= as_of.month]
        assert len(months) != 0, "No matching months for year"
        latest_month = max(months, key=lambda x: int(x[-2:]))
        days = filesystem.ls(latest_month)
        if filter_needed and int(latest_month[-2:]) == as_of.month:  # pragma: no cover
            days = [i for i in days if int(i[-2:]) <= as_of.day]
        assert len(days) != 0, "No matching days"
        return max(days, key=lambda x: int(x[-2:]))
    except AssertionError:
        # recursive case, we'll pull back the date to the end of the preceding
        # month, and try to match again
        new_date = as_of.replace(day=1) - timedelta(1)
        return _latest_partition_folder(path, new_date)


def _all_files_in_path(
    path: str,
    fs: fsspec.AbstractFileSystem,
    filetype: str = "",
) -> list[str]:
    """
    Return all files in a given path. If you pass this function a folder,
    it will patch recursively against parquet files within that folder. You can
    also give this function a glob string - if you do, it *won't* alter the glob
    in order to guarantee only filetype files (so if using a glob string, you should
    pass a glob string that already filters for parquet files such as 'folder/*.parquet'
    """
    path = path.split("://", 1)[-1]
    is_glob = "*" in path
    path = path if is_glob else path + f"/**/*{filetype}"
    fs.clear_instance_cache()
    return fs.glob(path)


def _dataframe_from_files(
    paths: list[str],
    storage_options: dict,
    input_operation: Callable = pd.read_parquet,
    **kwargs,
) -> pd.DataFrame:
    """
    Read all files in path into a single dataframe, will support concurrent reading for
    performance. Additional keyword arguments passed into input operation which will be
    pd.read_parquet by default, but can be another pandas read operation such as
    pd.read_csv if needed.

    Note, unless other keyword arguments are passed down, a pyarrow dtype_backend will
    be used by default.
    """
    kwargs = kwargs or {"dtype_backend": "pyarrow"}
    paths = [i if i.startswith("abfs://") else f"abfs://{i}" for i in paths]
    with futures.ThreadPoolExecutor(max_workers=15) as executor:
        jobs = [
            executor.submit(
                input_operation,
                i,
                storage_options=storage_options,
                **kwargs,
            )
            for i in paths
        ]
        return pd.concat(i.result() for i in futures.as_completed(jobs))
