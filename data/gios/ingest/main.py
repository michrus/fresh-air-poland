import sys

from gios_api_ingest import GIOSAPIIngest


def main() -> int:
    ingest = GIOSAPIIngest()
    ingest.ingest()
    return 0


if __name__ == '__main__':
    sys.exit(main())