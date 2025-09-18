def check_extension(filename: str, expected_extension: str) -> bool:
    """Check if the filename ends with the expected extension"""
    if not filename:
        return False
    ext_len = len(expected_extension)
    return filename[-ext_len:] == expected_extension
