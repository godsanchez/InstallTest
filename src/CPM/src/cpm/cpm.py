import typer
from typing_extensions import Annotated


def cpm(
    install: Annotated[bool, typer.Option(help="Install a CRC package.")] = False,
    update: Annotated[bool, typer.Option(help="Update a CRC package, or all installed software.")] = False,
    download: Annotated[bool, typer.Option(help="Download a CRC package (without installing).")] = False,
    list: Annotated[bool, typer.Option(help="List installed/downloaded CRC packages.")] = False,
):
    if install:
        print("Installing a CRC package...")
    if update:
        print("Updating a CRC package...")
    if download:
        print("Downloading a CRC package...")
    if list:
        print("Listing installed/downloaded CRC packages...")