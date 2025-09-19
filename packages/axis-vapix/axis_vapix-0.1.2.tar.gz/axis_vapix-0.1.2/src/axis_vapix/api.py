import time
import requests
import json

from requests.auth import HTTPDigestAuth

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

    def __init__(self, host, user, password, timeout=5):
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
        self.host = host
        self.user = user
        self.password = password
        self.base_url = 'http://' + self.host + '/axis-cgi'
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.user, self.password)
        self.session.timeout = timeout

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
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, json=params)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.HTTPError:
            raise Exception(response.text)
        except requests.RequestException as e:
            raise e
