from datetime import datetime, timedelta, timezone
from typing import final

from epublib.util import datetime_to_str


@final
class TestUtil:
    def test_datetime_to_str(self):
        old = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        new = datetime.fromisoformat(datetime_to_str(old))
        assert old.replace(microsecond=0) == new

        old = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
        new = datetime.fromisoformat(datetime_to_str(old))
        assert old.astimezone(timezone.utc).replace(microsecond=0) == new

        dt = datetime.now()
        new = datetime.fromisoformat(datetime_to_str(dt))
        assert dt.astimezone(timezone.utc).replace(microsecond=0) == new

        dt = datetime.now()
        new = datetime.fromisoformat(datetime_to_str(dt))

        assert new.microsecond == 0
