def main_directory(name: str) -> str:
    name = name.title()
    words = name.split()
    return "".join(words)


def source_directory(name: str) -> str:
    name = name.lower()
    words = name.split()
    return "_".join(words)
