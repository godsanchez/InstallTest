import downloadblob


def main():
    downloadblob.download_asset(
        asset_guid=downloadblob.args.package_guid,
        version=downloadblob.args.version,
        download_path=downloadblob.args.download_path,
    )


if __name__ == "__main__":
    main()
