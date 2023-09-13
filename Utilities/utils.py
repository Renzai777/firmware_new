from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from cryptography.fernet import Fernet as F
import logging
import colorlog
import json
import os
import subprocess
import time
from zeroconf import ServiceBrowser, Zeroconf
import base64
import ast





class Config:
    def __init__(self, environment="PROD"):
        config_file_path = FileManager.find_file("common_config.json")  # Use the correct file name
        config_data = FileManager.manage_file(config_file_path, "r")
        if config_data is None:
            raise ValueError(f"Failed to read config file: {config_file_path}")

        # Store the configuration data as class attributes
        self.PRODUCT_LIST = config_data[environment]["PRODUCT_LIST"]
        self.MQTT_SETTINGS = config_data[environment]["MQTT_SETTINGS"]
        self.IOT_HUB_SETTINGS = config_data[environment]["IOT_HUB_SETTINGS"]
        self.BLOB_STORAGE_SETTINGS = config_data[environment]["BLOB_STORAGE_SETTINGS"]
        # Add other settings here based on your needs
        self.USER_LOGIN_CREDENTIALS = config_data[environment]["USER_LOGIN_CREDENTIALS"]
        self.WIFI_SETTINGS = config_data[environment]["WIFI_SETTINGS"]
        self.MISCELLANEOUS = config_data[environment]["MISCELLANEOUS"]
        self.URL = config_data[environment]["URL"]
        self.KEYCID1 = config_data[environment]["KEYS"]["keycid1"].encode()
        self.KEYCID2 = config_data[environment]["KEYS"]["keycid2"].encode()
        self.CID = config_data[environment]["KEYS"]["cid"].encode()
        self.CSRT = config_data[environment]["KEYS"]["csrt"].encode()
        self.KEYSRT1 = config_data[environment]["KEYS"]["keysrt1"].encode()
        self.KEYSRT2 = config_data[environment]["KEYS"]["keysrt2"].encode()
        self.KEYAPIM1 = config_data[environment]["KEYS"]["keyapim1"].encode()
        self.KEYAPIM2 = config_data[environment]["KEYS"]["keyapim2"].encode()
        self.APIMKEY = config_data[environment]["KEYS"]["apimkey"].encode()
        self.PROD_SAPIM = config_data[environment]["KEYS"]["prod_sapim"].encode()
        self.SMART_CONFIG_AES_KEY = config_data[environment]["KEYS"]["smart_config_aes_key"].encode()
        self.SMART_CONFIG_AES256_IV = config_data[environment]["KEYS"]["smart_config_aes256_iv"].encode()
        self.AES_KEY = config_data[environment]["KEYS"]["aes_key"].encode()
        self.TARGET_MSG_PREFIX = config_data[environment]["KEYS"]["target_msg_prefix"].encode()




        # Read data from api_endpoints_config.json
        api_endpoints_file_path = FileManager.find_file("api_endpoints_config.json")
        api_endpoints_data = FileManager.manage_file(api_endpoints_file_path, "r")
        if api_endpoints_data is None:
            raise ValueError(f"Failed to read API endpoints config file: {api_endpoints_file_path}")

        # Store each API endpoint as a class attribute for the specified environment
        for request_type, request_apis in api_endpoints_data.items():
            for api in request_apis:
                api_name = next(iter(api))
                setattr(self, api_name, api[api_name][environment])



class EncryptionUtility:

    @staticmethod
    def decrypt(data):
        config = Config()  # Create a temporary Config instance
        cipher = AES.new(F(config.AES_KEY).decrypt(F(config.AES_KEY).decrypt(config.SMART_CONFIG_AES_KEY)),AES.MODE_CBC,F(config.AES_KEY).decrypt(F(config.AES_KEY).decrypt(config.SMART_CONFIG_AES256_IV)))
        try:
            decrypted_data = unpad(cipher.decrypt(data), AES.block_size)
        except ValueError:
            decrypted_data = cipher.decrypt(data)
        return decrypted_data

    @staticmethod
    def encrypt(data):
        config = Config()  # Create a temporary Config instance
        key = config.AES_KEY
        aes_key = F(key).decrypt(F(key).decrypt(config.SMART_CONFIG_AES_KEY))
        aes_iv = F(key).decrypt(F(key).decrypt(config.SMART_CONFIG_AES256_IV))

        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))

        return encrypted_data




class ColoredLogger(logging.Logger):
    COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    def __init__(self, name, level=logging.DEBUG):
        super().__init__(name, level)
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)


class FileManager:
    @staticmethod
    def manage_file(filename, permissions, content=None):
        file_content = None

        if "r" in permissions:
            try:
                with open(filename, 'r') as file:
                    file_content = json.load(file)
            except FileNotFoundError:
                print(f"File '{filename}' not found.")
            except IOError:
                print(f"Error reading file '{filename}'.")

        if "w" in permissions:
            try:
                with open(filename, 'w') as file:
                    json.dump(content, file, indent=4)
            except IOError:
                print(f"Error writing to file '{filename}'.")

        if "a" in permissions:
            try:
                with open(filename, 'a') as file:
                    json.dump(content, file, indent=4)
            except IOError:
                print(f"Error appending to file '{filename}'.")

        return file_content

    @staticmethod
    def find_file(filename):
        current_dir = os.getcwd()

        depth = 0
        while True:
            for root, dirs, files in os.walk(current_dir):
                if filename in files:
                    file_location = os.path.join(root, filename)
                    print(f"File '{filename}' found at: {file_location}")
                    return file_location

            parent_dir = os.path.dirname(current_dir)
            if current_dir == parent_dir:
                break

            current_dir = parent_dir
            depth += 1

        print(f"File '{filename}' not found in the current directory and its subdirectories.")
        return None

    @classmethod
    def update_common_data(cls, response):
        connected_devices = [device for device in response['data'][0]['devices'] if device['status'] == 'Connected']
        device_info = {device['productCode']: device['deviceId'] for device in connected_devices}
        file_path = FileManager.find_file("common_data.json")
        common_data = cls.manage_file(file_path, 'r')
        common_data['DEVICE_IDS'] = device_info
        cls.manage_file(file_path, 'w', content=common_data)
        return device_info



class WifiConnectionManager:

    @staticmethod
    def connection():
        config = Config()
        hostname =config.URL
        max_retries = 3
        retry_delay = 5

        for retry in range(max_retries + 1):
            try:

                result = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, timeout=10)

                if result.returncode == 0:
                    print(result.stdout)
                    print("Connection to", hostname, "is successful!")

                    break
                else:
                    print("Attempt", retry + 1, ":", hostname, "is unreachable. Retrying...")
                    print(result.stderr)
                    time.sleep(retry_delay)

            except subprocess.TimeoutExpired:
                print("Attempt", retry + 1, ": Timed out while pinging", hostname, ". Retrying...")
                time.sleep(retry_delay)

        else:
            print("Failed to establish a connection with", hostname, "after", max_retries, "attempts.")





class MDNSServiceDiscovery:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.listener = MDNSListener()
        self.browser = ServiceBrowser(self.zeroconf, "_hvls._tcp.local.", self.listener)

    def perform_discovery(self, duration=15):
        try:
            time.sleep(duration)
        finally:
            self.zeroconf.close()

class MDNSListener:
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % name)

    def add_service(self, zeroconf, type, name):
        print("Service %s added" % name)
        info = zeroconf.get_service_info(type, name)
        if info:
            decoded_properties = self.decode_and_dump_properties(info)
            print("\n")
            print(decoded_properties)
            print("\n")

            self.update_common_data(decoded_properties)

    def decode_and_dump_properties(self, info):
        decoded_properties = {}

        addresses = '.'.join(str(byte) for byte in info.addresses[0])
        decoded_properties['addresses'] = addresses

        for key, value in info.properties.items():
            if value is not None:
                decoded_value = base64.b64decode(value).decode('utf-8')
                decoded_properties[key.decode('utf-8')] = decoded_value

        return decoded_properties

    def update_common_data(self, decoded_properties):
        mdns_key = f"{decoded_properties['ProductCode']}_{decoded_properties['addresses']}"

        filename = 'common_data.json'
        permissions = "r+"
        with open(filename, permissions) as file:
            common_data = json.load(file)
            if 'MDNS_DETAILS' not in common_data or mdns_key not in common_data['MDNS_DETAILS']:
                common_data.setdefault('MDNS_DETAILS', {})[mdns_key] = decoded_properties
                file.seek(0)
                json.dump(common_data, file, indent=4)
                file.truncate()




class CommonMethod:

    @staticmethod
    def compare_telemetry(recvdata, origdata, key, subkey=None):
        result_count_pass = 0
        result_count_fail = 0
        print("RecvData: ", recvdata, "\n and OrigData", origdata, "\n")
        recv_data_state = {}
        try:
            if recvdata != "{\"None\":0}" and recvdata != {"None": 0} and recvdata != None:
                print("Type {} type {}".format(type(recvdata), type(origdata)))
                receive_data = ast.literal_eval(str(recvdata))
                test_data = ast.literal_eval(str(origdata))
                # print("type: {}".format(type(receive_data)))
                recv_data_state.update({key: receive_data[key]})
                # rssi = receive_data["H010C"]
                # print("\n --- rx_new dict is {} --RSSI: -".format(recv_data_state))
                result = 1
                if subkey == None:
                    if receive_data[key] == test_data[key]:
                        result = 0
                        result_count_pass = result_count_pass + 1
                        print(
                            "\n Comparing, Key - {}:{}\n TxData {}, -- Pass :), No. of Pass = {}, No. of Fail = {}\n".format(
                                key, receive_data[key], origdata, result_count_pass, result_count_fail))
                else:
                    if receive_data[key][subkey] == test_data[key][subkey]:
                        result = 0
                        result_count_pass = result_count_pass + 1
                        print(
                            "\n Comparing, Key - {}: {}\n TxData {}, -- Pass :), No. of Pass = {}, No. of Fail = {}\n".format(
                                key, receive_data[key], origdata, result_count_pass, result_count_fail))
                if (result == 1):
                    result_count_fail = result_count_fail + 1
                    print(
                        "\nFail :( ,\n Comparing, Key - {}: {}\n TxData {},No. of Pass = {}, No. of Fail = {}\n".format(
                            key, receive_data[key], origdata, result_count_pass, result_count_fail))
                return result, recv_data_state
            else:
                print("received data is None")
                result_count_fail = result_count_fail + 1
                print("\nFail :( ,No. of Pass = {}, No. of Fail = {}\n".format(result_count_pass,
                                                                               result_count_fail))
                return 1, "None", "None"
        except Exception as e:
            print("error in compare_telemetry method : ".format(e))







# if __name__ == "__main__":
#     service_discovery = MDNSServiceDiscovery()
#     try:
#         service_discovery.perform_discovery()
#     except KeyboardInterrupt:
#         pass





# config = Config()
# print(config.URL)
# print(config.TARGET_MSG_PREFIX, type(config.TARGET_MSG_PREFIX))
# WifiConnectionManager.connection()
# encryption_utility = EncryptionUtility()
# print(encryption_utility.config.URL)
# print(encryption_utility.config.AES_KEY, type(encryption_utility.config.AES_KEY))


