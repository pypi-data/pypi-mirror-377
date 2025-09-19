# Make working with datetimes in Python simpler and more powerful.

Created to be used in a project, this package is published to github for ease of management and installation across different modules.

## Installation

Install from `PyPi`

```bash
pip install cytimes
```

Install from `github`

```bash
pip install git+https://github.com/AresJef/cyTimes.git
```

## Compatibility

Supports Python 3.10 and above.

## Features

`cyTimes` introduces two classes that simplify and enhance working with datetimes:

- `Pydt` (Python datetime.datetime)
- `Pddt` (Pandas DatetimeIndex)

Both provide similar functionalities:

- Direct drop-in replacements (subclasses) for standard Python `datetime` and Pandas `DatetimeIndex`.
- Cython-optimized for high-performance parsing, creation, and manipulation.
- Well-documented methods with type annotations.
- Flexible constructors accepting multiple input formats (strings, datetime objects, timestamps, etc.).
- Rich conversion options (ISO strings, ordinals, timestamps, and more).
- Comprehensive manipulation for precise datetime fields adjustments (years, quarters, months, days, time).
- Direct calendar information insights (e.g., days in month, leap years).
- Extended timezone-related capabilities.
- Supports adding or subtracting deltas, and compute deltas against datetime-like object(s).

## `Pydt` Usage

The `Pydt` class operates similarly to Python’s native `datetime.datetime`, with added methods and improvements.

### Construction

```python
from cytimes import Pydt
import datetime, numpy as np

Pydt(1970, 1, 1, tzinfo="UTC")
>>> 1970-01-01 00:00:00+0000
Pydt.parse("1970 Jan 1 00:00:01 PM")
>>> 1970-01-01 12:00:01
Pydt.now()
>>> 2024-12-06 10:37:25.619593
Pydt.utcnow()
>>> 2024-12-06 09:37:36.743159+0000
Pydt.combine("1970-01-01", "00:00:01")
>>> 1970-01-01 00:00:01
Pydt.fromordinal(1)
>>> 0001-01-01 00:00:00
Pydt.fromseconds(1)
>>> 1970-01-01 00:00:01
Pydt.fromicroseconds(1)
>>> 1970-01-01 00:00:00.000001
Pydt.fromtimestamp(1, datetime.UTC)
>>> 1970-01-01 00:00:01+0000
Pydt.utcfromtimestamp(1)
>>> 1970-01-01 00:00:01+0000
Pydt.fromisoformat("1970-01-01T00:00:01")
>>> 1970-01-01 00:00:01
Pydt.fromisocalendar(1970, 1, 4)
>>> 1970-01-01 00:00:00
Pydt.fromdate(datetime.date(1970, 1, 1))
>>> 1970-01-01 00:00:00
Pydt.fromdatetime(datetime.datetime(1970, 1, 1))
>>> 1970-01-01 00:00:00
Pydt.fromdatetime64(np.datetime64(1, "s"))
>>> 1970-01-01 00:00:01
Pydt.strptime("00:00:01 1970-01-01", "%H:%M:%S %Y-%m-%d")
>>> 1970-01-01 00:00:01
```

### Conversion

```python
from cytimes import Pydt

dt = Pydt(1970, 1, 1, tzinfo="CET")

dt.ctime()
>>>  "Thu Jan  1 00:00:00 1970"
dt.strftime("%Y-%m-%d %H:%M:%S %Z")
>>>  "1970-01-01 00:00:00 CET"
dt.isoformat()
>>>  "1970-01-01T00:00:00+01:00"
dt.timetuple()
>>> (1970, 1, 1, 0, 0, 0, 3, 1, 0)
dt.toordinal()
>>>  719163
dt.seconds()
>>>  0.0
dt.microseconds()
>>>  0
dt.timestamp()
>>>  -3600.0
dt.date()
>>>  1970-01-01
dt.time()
>>>  00:00:00
dt.timetz()
>>>  00:00:00
```

### Manipulation

```python
from cytimes import Pydt

dt = Pydt(1970, 2, 2, 2, 2, 2, 2, "CET")

# . replace
dt.replace(year=2007, microsecond=1, tzinfo="UTC")
>>> 2007-02-02 02:02:02.000001+0000

# . year
dt.to_curr_year(3, 15)
>>> 1970-03-15 02:02:02.000002+0100
dt.to_prev_year("Feb", 30)
>>> 1969-02-28 02:02:02.000002+0100
dt.to_next_year("十二月", 31)
>>> 1971-12-31 02:02:02.000002+0100
dt.to_year(100, "noviembre", 30)
>>> 2070-11-30 02:02:02.000002+0100

# . quarter
dt.to_curr_quarter(3, 15)
>>> 1970-03-15 02:02:02.000002+0100
dt.to_prev_quarter(3, 15)
>>> 1969-12-15 02:02:02.000002+0100
dt.to_next_quarter(3, 15)
>>> 1970-06-15 02:02:02.000002+0100
dt.to_quarter(100, 3, 15)
>>> 1995-03-15 02:02:02.000002+0100

# . month
dt.to_curr_month(15)
>>> 1970-02-15 02:02:02.000002+0100
dt.to_prev_month(15)
>>> 1970-01-15 02:02:02.000002+0100
dt.to_next_month(15)
>>> 1970-03-15 02:02:02.000002+0100
dt.to_month(100, 15)
>>> 1978-06-15 02:02:02.000002+0200

# . weekday
dt.to_monday()
>>> 1970-02-02 02:02:02.000002+0100
dt.to_sunday()
>>> 1970-02-08 02:02:02.000002+0100
dt.to_curr_weekday(4)
>>> 1970-02-06 02:02:02.000002+0100
dt.to_prev_weekday(4)
>>> 1970-01-30 02:02:02.000002+0100
dt.to_next_weekday(4)
>>> 1970-02-13 02:02:02.000002+0100
dt.to_weekday(100, 4)
>>> 1972-01-07 02:02:02.000002+0100

# . day
dt.to_yesterday()
>>> 1970-02-01 02:02:02.000002+0100
dt.to_tomorrow()
>>> 1970-02-03 02:02:02.000002+0100
dt.to_day(100)
>>> 1970-05-13 02:02:02.000002+0100

# . date&time
dt.to_first_of("Y")
>>> 1970-01-01 02:02:02.000002+0100
dt.to_last_of("Q")
>>> 1970-03-31 02:02:02.000002+0100
dt.to_start_of("M")
>>> 1970-02-01 00:00:00+0100
dt.to_end_of("W")
>>> 1970-02-08 23:59:59.999999+0100

# . round / ceil / floor
dt.round("h")
>>> 1970-02-02 02:00:00+0100
dt.ceil("m")
>>> 1970-02-02 02:03:00+0100
dt.floor("s")
>>> 1970-02-02 02:02:02+0100
```

### Calendar Information

```python
from cytimes import Pydt

dt = Pydt(1970, 2, 2, tzinfo="UTC")

# . iso
dt.isocalendar()
>>> {'year': 1970, 'week': 6, 'weekday': 1}
dt.isoyear()
>>> 1970
dt.isoweek()
>>> 6
dt.isoweekday()
>>> 1

# . year
dt.is_leap_year()
>>> False
dt.is_long_year()
>>> True
dt.leap_bt_year(2007)
>>> 9
dt.days_in_year()
>>> 365
dt.days_bf_year()
>>> 719162
dt.days_of_year()
>>> 33
dt.is_year(1970)
>>> True

# . quarter
dt.days_in_quarter()
>>> 90
dt.days_bf_quarter()
>>> 0
dt.days_of_quarter()
>>> 33
dt.is_quarter(1)
>>> True

# . month
dt.days_in_month()
>>> 28
dt.days_bf_month()
>>> 31
dt.days_of_month()
>>> 2
dt.is_month("Feb")
>>> True
dt.month_name("es")
>>> "febrero"

# . weekday
dt.is_weekday("Monday")
>>> True

# . day
dt.is_day(2)
>>> True
dt.day_name("fr")
>>> "lundi"

# . date&time
dt.is_first_of("Y")
>>> False
dt.is_last_of("Q")
>>> False
dt.is_start_of("M")
>>> False
dt.is_end_of("W")
>>> False
```

### Timezone Operation

```python
from cytimes import Pydt

dt = Pydt(1970, 1, 1, tzinfo="UTC")

dt.is_local()
>>> False
dt.is_utc()
>>> True
dt.is_dst()
>>> False
dt.tzname()
>>> "UTC"
dt.utcoffset()
>>> 0:00:00
dt.utcoffset_seconds()
>>> 0
dt.dst()
>>> None
dt.astimezone("CET")
>>> 1970-01-01 01:00:00+0100
dt.tz_localize(None)
>>> 1970-01-01 00:00:00
dt.tz_convert("CET")
>>> 1970-01-01 01:00:00+0100
dt.tz_switch("CET")
>>> 1970-01-01 01:00:00+0100
```

### Arithmetic

```python
from cytimes import Pydt

dt = Pydt(1970, 1, 1, tzinfo="UTC")

dt.add(years=1, weeks=1, microseconds=1)
>>> 1971-01-08 00:00:00.000001+0000
dt.sub(quarters=1, days=1, seconds=1)
>>> 1969-09-29 23:59:59+0000
dt.diff("2007-01-01 01:01:01+01:00", "s")
>>> -1167609662
```

### Comparison

```python
from cytimes import Pydt

dt = Pydt(1970, 1, 1)

dt.is_past()
>>> True
dt.is_future()
>>> False
dt.closest("1970-01-02", "2007-01-01")
>>> 1970-01-02 00:00:00
dt.farthest("1970-01-02", "2007-01-01")
>>> 2007-01-01 00:00:00
```

## `Pddt` Usage

`Pddt` extends similar functionalities to Pandas `DatetimeIndex`, making it behave more like native Python `datetime.datetime`, but for arrays of datetime values. It supports:

- Vectorized parsing, creation, and manipulation.
- Most of the same methods and properties as `Pydt` (see examples above), adapted for datetime-arrays.
- Automatic handling of out-of-range datetimes in nanoseconds by downcasting to microsecond precision `'us'` to avoid overflow.

### Handling Nanosecond Overflow

By default, `DatetimeIndex` uses nanosecond precision `'ns'`, which cannot represent datetimes outside the range 1677-09-21 to 2262-04-11. Pddt automatically downcasts to microseconds `us` when encountering out-of-range datetimes, sacrificing nanosecond precision to allow a broader range support.

```python
from cytimes import Pddt

Pddt(["9999-01-01 00:00:00+00:00", "9999-01-02 00:00:00+00:00"])
>>> Pddt(['9999-01-01 00:00:00+00:00', '9999-01-02 00:00:00+00:00'],
        dtype='datetime64[us, UTC]', freq=None)
```

Downcasting mechanism also automacially applies to all methods that modify the datetimes, resulting values out of the `'ns'` range:

```python
from cytimes import Pddt

pt = Pddt(["1970-01-01 00:00:00+00:00", "1970-01-02 00:00:00+00:00"])
# Pddt(['1970-01-01 00:00:00+00:00', '1970-01-02 00:00:00+00:00'],
#       dtype='datetime64[ns, UTC]', freq=None)
pt.to_year(1000, "Feb", 30)
>>> Pddt(['2970-02-28 00:00:00+00:00', '2970-02-28 00:00:00+00:00'],
        dtype='datetime64[us, UTC]', freq=None)
```

### Acknowledgements

cyTimes is based on several open-source repositories.

- [babel](https://github.com/python-babel/babel)
- [numpy](https://github.com/numpy/numpy)
- [pandas](https://github.com/pandas-dev/pandas)

cyTimes is built on the following open-source repositories:

- [dateutil](https://github.com/dateutil/dateutil)

  Class <'Parser'> and <'Delta'> in this package are the cythonized version of <'dateutil.parser'> and <'dateutil.relativedelta'>. Credit and thanks go to the original authors and contributors of the `dateutil` library.
