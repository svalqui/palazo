from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def download_csv1(
    output_file="",
    page_url="",
):
    """
    Download CSV file.

    Returns:
        Path: The path of the downloaded file.
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Get the ASX directory page
    response = requests.get(
        page_url,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()

    # Find the CSV link
    soup = BeautifulSoup(response.text, "html.parser")
    csv_url = None

    for link in soup.find_all("a", href=True):
        link_text = link.get_text(" ", strip=True).lower()

        if "all asx listed companies" in link_text:
            csv_url = urljoin(page_url, link["href"])
            break

    if csv_url is None:
        raise RuntimeError(
            "Could not find the download link."
        )

    # Download the CSV
    csv_response = requests.get(
        csv_url,
        headers=headers,
        timeout=30
    )
    csv_response.raise_for_status()

    # Save the file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(csv_response.content)

    return output_path
