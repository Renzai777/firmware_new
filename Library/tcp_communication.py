import sys
import time
import socket
from Utilities.utils import EncryptionUtility


class TcpWrap:
    TrimData = 0

    def tcp_config(self, ip_addr, port):
        print("\n------- Creating socket Connection ------")
        self.re_read_count = 0
        self.sock = socket.create_connection((ip_addr, port))
        self.tcp_timeout(1)
        # self.tcp_read()

    def tcp_read(self):
        data = None
        try:
            data = EncryptionUtility.decrypt(self.sock.recv(1024))
            x = data
            TrimData = data
            if (x[0:3] == b'ACK'):
                TrimData = x[0:3]
            else:
                for i in range(len(x)):
                    if ((x[i]) == 93 and (x[i + 1]) == 125):
                        TrimData = x[:i + 2]
                        sys.stdout.flush()
                    elif ((x[i]) == 34 and (x[i + 1]) == 125):
                        TrimData = x[:i + 2]
                        sys.stdout.flush()
            print("tcp_readabc: ", TrimData)
            return TrimData
        except Exception as e:

            print("Error raised in tcp read:", e)

    def tcp_write(self, data):
        try:

            data = bytes(data.encode())
            TARGET_MSG_PREFIX = b'Havells: '
            dataTx = bytearray(len(data) + len(TARGET_MSG_PREFIX))
            for i in range(len(TARGET_MSG_PREFIX)):
                dataTx[i] = TARGET_MSG_PREFIX[i]
            for i in range(len(data)):
                dataTx[len(TARGET_MSG_PREFIX) + i] = data[i]
            print("dataTx : ", dataTx, type(dataTx))
            tx_data = EncryptionUtility.encrypt(bytes(dataTx))
            self.sock.sendall(tx_data)
        except Exception as e:
            print("error in tcp_write: ", e)
        return

    def tcp_ask(self, data, delay):
        print(data, delay)
        try:
            rx_data = None
            print("tcp_tx: {}".format(data))
            self.tcp_write(data)
            time.sleep(delay)
            try:
                # first read of data
                response = self.tcp_read()
                if (response != None):
                    rx_data = bytes.decode(response)
                    print("rx_data 1 : ", rx_data)
            except Exception as e:
                print("error in tcp read 1rd time: ", e)

            try:
                # 2nd read if ack is received first
                response = self.tcp_read()
                if (response != None):
                    rx_data = bytes.decode(response)
                    print("rx_data 2 : ", rx_data)
            except Exception as e:
                print("error in tcp read 2rd time: ", e)

            # 3rd read of data
            try:
                response = self.tcp_read()
                if (response != None):
                    rx_data = bytes.decode(response)
                    print("\nrx_data 3 : ", rx_data)
            except Exception as e:
                print("error in tcp read 3rd time: ", e)

        except Exception as e:
            rx_data = bytes.decode(self.tcp_read())
            print("rx_data 1 : ", rx_data)

            print("error in tcp_ask: ", e)

        return data, rx_data


    def tcp_communication(self,tx_data,delay=0.01):
        try:
            print("\n tcp_communication")
            self.tcp_config("192.168.0.108",8888)
            tx_data, rx_tcp_response = self.tcp_ask(tx_data,delay)
            print("rx_tcp_response is: ", rx_tcp_response)
            if(rx_tcp_response == "ACK" or rx_tcp_response == None or rx_tcp_response ==""):
                print("\n ****** Reconnecting because of issues ")
                self.tcp_close()
                self.tcp_config("192.168.0.108",8888)
                rx_tcp_response = self.re_connect_device()

                # print("\nrx_tcp_response is : {}\n".format(rx_tcp_response))
        except Exception as e:
            print("Error raised in tcp communication is:",e)
            rx_tcp_response=None
        # self.tcp_close()
        return rx_tcp_response

    def re_connect_device(self):
        response = self.tcp_read()
        if (response != None):
            rx_data = bytes.decode(response)
        print("in re_connect_device - rx_data 1 : ", rx_data)
        return rx_data

    def tcp_timeout(self, timeout):
        self.sock.settimeout(int(timeout))

    def tcp_close(self):
        print("\n------- Closing socket Connection ------")
        self.sock.close()
