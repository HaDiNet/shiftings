class AlphaNumericConverter:
    regex = r'[0-9A-Za-z]+'

    def to_python(self, value: str) -> str:
        return value

    def to_url(self, value: str) -> str:
        return value
