import json
import http.client
import time

from cryptography.fernet import Fernet as F
import logging
from Utilities.utils import ColoredLogger, Config
from Utilities.utils import FileManager




class HttpClient:
    def __init__(self, base_url):
        self.connection = http.client.HTTPSConnection(base_url)

    def close_connection(self):
        if self.connection:
            self.connection.close()

# logger = ColoredLogger("my_logger", level=logging.DEBUG)

class ApiClient(HttpClient):
    def __init__(self, config, environment):
        super().__init__(config.URL)
        self.config = config
        self.environment = environment.lower()
        self.logger = ColoredLogger("my_logger", level=logging.DEBUG)
        self.access_token = None
        self.http_client = HttpClient(config.URL)

    def request_api(self, method, url, payload, headers):
        try:
            self.logger.debug("Making API request to URL: %s", url)

            self.http_client.connection.request(method, url, payload, headers)
            response = self.http_client.connection.getresponse()
            self.logger.info("Response Status: %s %s", response.status, response.reason)
            data = response.read()
            parsed_data = json.loads(data)
            self.logger.debug("Parsed Response Data: %s", parsed_data)

            return parsed_data

        except json.JSONDecodeError as e:
            self.logger.error("Failed to decode API response: %s", e)
            return None
        except http.client.HTTPException as e:
            self.logger.error("HTTP Exception: %s", e)
            return None
        except Exception as e:
            self.logger.error("Error occurred: %s", e)
            return None

    def login(self, user, password):
        try:
            print("Inside login")
            if self.environment not in ["qa", "prod"]:
                raise ValueError("Invalid environment. Must be either 'qa' or 'prod'.")

            if self.environment == "qa":
                hostname = self.config.URL
                print(hostname)
                endpoint = "/user/v1/userlogin"
                payload = json.dumps({
                    "userName": user,
                    "clientId": F(self.config.KEYCID1).decrypt(
                        F(self.config.KEYCID2).decrypt(self.config.CID)).decode(),
                    "clientSecret": F(self.config.KEYSRT1).decrypt(
                        F(self.config.KEYSRT2).decrypt(self.config.CSRT)).decode(),
                    "password": password
                })
                headers = {
                    'Ocp-Apim-Subscription-Key': F(self.config.KEYAPIM1).decrypt(
                        F(self.config.KEYAPIM2).decrypt(self.config.APIMKEY)).decode(),
                    'Content-Type': 'application/json'
                }
            else:  # self.environment == "prod"
                hostname = self.config.URL
                print(hostname)

                endpoint = "/user/userlogin"
                print(endpoint)
                payload = json.dumps({
                    "userName": user,
                    "clientId": "7ot562f7js79629pk7jfmcja42",
                    "clientSecret": "1o7jomk2oedm2jc5rfueatsvfl50qa21565r9h1ut6kois74r92l",
                    "password": password
                })
                headers = {
                    'Ocp-Apim-Subscription-Key': "7de853d3061542c590b896fe4bfbe92a",
                    'Content-Type': 'application/json'
                }

            url = hostname + endpoint
            print(url)
            response_data = self.request_api("POST", endpoint, payload, headers)
            print(response_data)

            self.logger.info("Login Request URL: %s", url)
            self.logger.info("Login Request Payload: %s", payload)
            self.logger.info("Login Response Data: %s", response_data)

            if response_data and response_data.get("statusCode") == 200:
                access_token = response_data["data"]["accessToken"]["jwtToken"]
                self.access_token = access_token
                common_data_file_path = FileManager.find_file("common_data.json")
                common_data = FileManager.manage_file(common_data_file_path, "r")
                if common_data is None:
                    raise ValueError(f"Failed to read common_data file: {common_data_file_path}")

                common_data["ACCESS_TOKEN"] = access_token
                FileManager.manage_file(common_data_file_path, "w", common_data)

                return self.access_token
            else:
                self.logger.error("Login Failed: %s", response_data.get("statusCode"))
                return None

        except json.JSONDecodeError as e:
            self.logger.error("Failed to decode API response: %s", e)
            return None
        except http.client.HTTPException as e:
            self.logger.error("HTTP Exception: %s", e)
            return None
        except Exception as e:
            self.logger.error("Error occurred: %s", e)
            return None

        finally:
            self.http_client.close_connection()

    def fetch_devices(self):
        if self.environment == "qa":
            hostname = self.config.URL
            endpoint = "/mobile/fetchDevicesOfUser"
            payload = ""
            headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json'
            }
        else:
            hostname = self.config.URL
            endpoint = "/mobile/fetchDevicesOfUser"
            payload = ""
            headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json'
            }

        url = hostname + endpoint
        print(url)
        response_data = self.request_api("GET", endpoint, payload, headers)
        device_ids = FileManager.update_common_data(response_data)
        print(device_ids)

        return device_ids

    def fetch_device_status(self, device_id):
        hostname = self.config.URL
        endpoint = "/mobile/getCurrentStatusOfDevice?deviceId=" + device_id
        payload = ""
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        url = hostname + endpoint
        response_data = self.request_api("GET", endpoint, payload, headers)
        print(f"Response Data : {response_data}")

        if response_data.get("message") == "success":
            try:
                data = response_data["data"]["telemetry"]["data"]["message"]
                return data
            except KeyError:
                return None
        else:
            return None

    def delete_device_from_user(self, device_id):
        try:
            hostname = self.config.URL
            endpoint = "/mobile/deleteDeviceFromUser?deviceId=" + device_id
            payload = ""
            headers = {
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json'
            }
            url = hostname + endpoint
            print(url)
            response = self.request_api("DELETE", endpoint, payload, headers)
            return response

        except Exception as e:
            print("Exception raised in delete_device_from_user:", e)




    def device_control(self, deviceid, tx_command):
        if not isinstance(tx_command, dict):
            raise ValueError("tx_command must be a dictionary.")

        hostname = self.config.URL
        endpoint = "/mobile/deviceControl"

        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        tx_key, tx_value = next(iter(tx_command.items()))

        payload = json.dumps({
            "deviceId": deviceid,
            tx_key: tx_value
        })

        url = hostname + endpoint
        response_data = self.request_api("PUT", endpoint, payload, headers)

        return response_data
















































