"""
Flexitricity data module is a set of utility functions for loading data, and
optionally, also for interactive with data sources via SQL.

For distribution reasons `flex_data` is open source, but it's unlikely to be of
actual value outside the organisation.

To get up and running with `flex_data` you can pip install the package with:

```bash
pip install "flex-data-sdk"
```

And import with:

```python
from flex.data import datalake, warehouse, trading_db
```

For authentication to work, you'll need some additional set up too:

- Azure credentials on your machine, this can be done through the software portal

- An MSSQL driver installed (17 or 18) in order to access the Azure SQL database.

(You don't need a postgres driver, since `flex_data` uses precompiled binaries
from the `pyscopg2-binary` library).

`flex.data` is organised into four modules:
- datalake (functions for loading data from the datalake)
- warehouse (functions for loading data from the SQL warehouse)
- trading_db (functions for loading data from the trading database)
"""

from flex.data._version import __version__  # noqa
