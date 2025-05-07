import platform
import zipfile
import requests
from io import BytesIO

from Library.tools import list_files

# Maps Python platform.machine() and platform.system() to Chrome platform labels


def get_platform_label() -> str:
    system = platform.system()
    machine = platform.machine()

    if system == "Linux":
        if machine == "x86_64":
            return "linux64"
        elif machine == "aarch64":
            return "linux-arm64"

    elif system == "Darwin":
        if machine == "x86_64":
            return "mac-x64"
        elif machine == "arm64":
            return "mac-arm64"

    elif system == "Windows":
        return "win32"

    raise RuntimeError(f"Unsupported system: {system} {machine}")


def download_latest_chrome_driver(platform_label, destination_dir="chrome_driver") -> str:
    # Step 1: Get latest stable version
    version_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    response = requests.get(version_url)
    data = response.json()
    version = data["channels"]["Stable"]["version"]
    print(f"Latest stable ChromeDriver version: {version}")

    # Step 2: Find the matching download URL
    downloads = data["channels"]["Stable"]["downloads"]["chromedriver"]
    url = next(
        item["url"] for item in downloads if
        item["platform"] == platform_label
    )

    # Step 3: Download and unzip
    zip_response = requests.get(url)
    with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
        z.extractall(destination_dir)

    files = list_files(directory=destination_dir)
    dir_chrome_driver = f"{destination_dir}/{files[0]}" if files else ""
    return dir_chrome_driver


if __name__ == "__main__":
    # Example usage
    print("Downloading the latest ChromeDriver...")

    # Get the platform label
    platform_label = get_platform_label()
    print(f"Platform label: {platform_label}")

    # Download the latest ChromeDriver
    dir_driver = download_latest_chrome_driver(
        platform_label=platform_label
    )
    print(f"ChromeDriver downloaded and extracted to: {dir_driver}")
