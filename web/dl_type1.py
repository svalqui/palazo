from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def download_csv1(
    output_file="",
    page_url="",
    fallback_url="",
):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Download the directory page
    response = requests.get(
        page_url,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    csv_url = None

    # Search all links for either a CSV URL or relevant link text
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(" ", strip=True).lower()

        if (
            ".csv" in href.lower()
        ):
            csv_url = urljoin(page_url, href)
            break

    # Fallback URL used by ASX
    if csv_url is None:
        csv_url = fallback_url

    print("Downloading:", csv_url)

    # Download the CSV file
    csv_response = requests.get(
        csv_url,
        headers=headers,
        timeout=30
    )
    csv_response.raise_for_status()

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(csv_response.content)

    return output_path


