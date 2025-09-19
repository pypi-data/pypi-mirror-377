if __name__ == "__main__":
    from sys import argv
    if argv[1] == "setup":
        from . import setup
        setup()
    if argv[1] in ["package", "pack"]:
        from . import package
        package(as_module=True)