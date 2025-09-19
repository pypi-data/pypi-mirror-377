from typing import final

from epublib.identifier import EPUBId


@final
class TestIdentifier:
    def test_valid_identifiers(self):
        valid_identifiers = [
            "variable",
            "_privateVar",
            "var123",
            "var_name",
            "VarName",
            "varName2",
            "chapter1",
            "café",
            "_начало",
            "章节1",
        ]
        for identifier in valid_identifiers:
            assert EPUBId(identifier).is_valid()

        invalid_identifiers = [
            "123start",
            "-var-name",
            "var name",
            "var$name",
            "",
            " ",
            ".varname",
            "var@name",
            "var#name",
            "var%name",
            "var	name",
        ]
        for identifier in invalid_identifiers:
            assert not EPUBId(identifier).is_valid()
