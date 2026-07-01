from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "pyqttoolkit"
LICENSE_PATH = ROOT / "LICENSE_SHORT"
EXCLUDED_FILENAMES = {"_version.py"}


def commented_license_text() -> str:
    lines = LICENSE_PATH.read_text().splitlines()
    return "\n".join(f"# {line}" if line else "#" for line in lines)


def main() -> int:
    expected_header = commented_license_text()
    missing_headers = []

    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if path.name in EXCLUDED_FILENAMES:
            continue

        content = path.read_text().replace("\r\n", "\n")
        if not content.startswith(expected_header):
            missing_headers.append(path.relative_to(ROOT))

    if missing_headers:
        print("Missing license header:")
        for path in missing_headers:
            print(path)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
