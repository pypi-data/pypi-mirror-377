import time
import requests
import json

from requests.auth import HTTPDigestAuth

from .calendar import Calendar


class api:
    """
    A class that provides an interface to interact with Axis cameras using the VAPIX API.

    Attributes:
    -----------
    host : str
        IP address or domain name of the camera.
    user : str
        Username for the camera's API authentication.
    password : str
        Password for the camera's API authentication.
    base_url : str
        Base URL for accessing the VAPIX API endpoints.
    session : requests.Session
        Session object for handling HTTP requests with authentication.
    doorcontrol : DoorControl
        Instance for controlling Door Controller.
    """

    def __init__(self, user, password, timeout=5):
        """
        Initializes the VapixAPI with host, user, and password credentials.

        Parameters:
        -----------
        host : str
            IP address or domain name of the camera.
        user : str
            Username for the camera's API authentication.
        password : str
            Password for the camera's API authentication.
        timeout : int, optional
            Timeout for HTTP requests (default is 5 seconds).
        """
        self.user = user
        self.password = password
        self.base_url = "https://api.planningcenteronline.com"
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.user, self.password)
        self.session.timeout = timeout

        self.calendar = Calendar(self)

    def _send_request(self, endpoint, method="GET", params=None):
        """
        Send a request to a specific VAPIX API endpoint

        Parameters:
        -----------
        endpoint : str
            The endpoint to which the request is sent.
        method : str, optional
            HTTP request method (default is "GET").
        params : dict, optional
            Parameters to be included in the request.

        Returns:
        --------
        str
            Response text from the request.

        Raises:
        -------
        requests.RequestException
            If the request encounters an error.
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(
                    url, params=params, auth=(self.user, self.password)
                )
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.HTTPError:
            raise Exception(response.text)
        except requests.RequestException as e:
            raise e


if __name__ == "__main__":
    import time
    import os
    import dotenv

    dotenv.load_dotenv()
    api = api(
        os.environ.get("host"), os.environ.get("user"), os.environ.get("password")
    )

    api.session.close()
