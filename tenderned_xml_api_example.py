import logging
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

BASE_URL = "https://www.tenderned.nl/papi/tenderned-rs-tns/v2"


def create_session(username: str, password: str) -> requests.Session:
    """Create a session with the basic auth headers included.

    Args:
        username: username used to authenticate the requests
        password: password used to authenticate the requests

    Returns:
        requests.Session: authenticated session
    """
    session = requests.Session()

    # Add the authentication headers
    session.auth = (username, password)

    return session


def call_tns_xml_api(session: requests.Session, pub_id: int) -> str:
    """Call the TenderNed Notice Service XML API endpoint.

    Args:
        session: session created using `start_session`
        pub_id: id of the publication to retrieve

    Returns:
        str: raw response text
    """
    # Make the API call using the requests library
    url = f"{BASE_URL}/publicaties/{pub_id}/public-xml"
    logging.info(f"Retrieving data from {url}")
    response = session.get(url)

    response.raise_for_status()  # Raise an exception if the status code indicates an error

    return response.text


def parse_response(response_text: str) -> None:
    """Parses the raw response text retrieved from the XML API.

    Args:
        response_text: raw string containing XML
    """
    soup = BeautifulSoup(response_text, features="xml")

    object_contract = soup.find("OBJECT_CONTRACT")
    if not object_contract:
        raise ValueError("XML does not contain object contract")

    contract_title = object_contract.find("TITLE")
    if not contract_title:
        raise ValueError("Contract does not contain a title")

    logging.info(f"Contract title: {contract_title.get_text(strip=True)}")


# Example usage:
def main() -> None:
    """Example to retrieve and parse a single eForms publication.

    Steps:
    1. Retrieve authentication information from .env file
    2. Create a session
    3. Call the API
    4. Parse the response
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

    # Load credentials from .env file
    load_dotenv()
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    if not username or not password:
        logging.error("Please provide a username and password in the .env file.")
        return

    session = create_session(username, password)

    resp = call_tns_xml_api(session, pub_id=300000)

    parse_response(resp)


if __name__ == "__main__":
    main()
