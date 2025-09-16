import requests

from ..domain import BaseDomain

class APIRequest(BaseDomain):
    """
    Reusable request sender that builds the URL dynamically.
    """

    def send_api_request(
            self,
            messaging_product:str,
            delivery_type: str,
            message_type: str,
            template_type: str,
            account_sid: str,
            auth_token: str,
            payload: dict
    ):
        try:
            url = f"{self.BASE_URL}/{messaging_product}/{delivery_type}/"

            if message_type:
                url += f"{message_type}/"
            if template_type:
                url += f"{template_type}/"

            response = requests.post(
                url,
                headers={
                    'X-Account-SID': account_sid,
                    'X-Auth-Token': auth_token,
                },
                json=payload,
                timeout=5
            )
            try:
                resp_data = response.json()
            except ValueError:
                resp_data = {"message": response.text}

            return {
                "status_code": response.status_code,
                "response": resp_data or {}
            }

        # --- Specific exception handling ---
        except requests.exceptions.Timeout:
            return {
                "status_code": 504,
                "response": {"error": "Request timed out"}
            }

        except requests.exceptions.ConnectionError:
            return {
                "status_code": 503,
                "response": {"error": "Failed to connect to API gateway"}
            }

        except requests.exceptions.HTTPError as e:
            return {
                "status_code": 502,
                "response": {"error": f"HTTP error occurred: {str(e)}"}
            }

        except requests.exceptions.RequestException as e:
            # Any other requests-related error
            return {
                "status_code": 500,
                "response": {"error": f"Request failed: {str(e)}"}
            }

        # --- Final catch-all (non-requests errors, e.g. coding mistakes) ---
        except Exception as e:
            return {
                "status_code": 500,
                "response": {"error": f"Unexpected error: {str(e)}"}
            }