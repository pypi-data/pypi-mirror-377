import re

start = (
    r":A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D"
    r"\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF"
    r"\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF"
)
name = start + r"-.0-9\u00B7\u0300-\u036F\u203F-\u2040"

valid_id_pattern = re.compile(f"^[{start}][{name}]*$")


class EPUBId(str):
    """A unique identifier for a resource within an EPUB file.
    Use this class to reference epub resources throughout the library
    using it's manifest id rather than its complete filename.
    """

    def is_valid(self) -> bool:
        """Check if the identifier is valid according to the XML specification.

        Returns:
            bool: True if the identifier is valid, False otherwise.
        """
        return bool(valid_id_pattern.match(self))
