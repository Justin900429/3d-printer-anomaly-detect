import time
import os
import warnings

from dotenv import load_dotenv
import requests

import cv2


class OctoClient:
    def __init__(self, host_name="http://octopi.local", use_cap=True,
                 device=0):
        # Set up API url and secret key
        load_dotenv()
        self.api_key = os.getenv("api_key")
        self.base_url = f"{host_name}/api"

        # Set up camera
        self.use_cap = use_cap
        if self.use_cap:
            self.cam = cv2.VideoCapture(device)
            time.sleep(0.1)
        else:
            self.cam = None

    @property
    def frame(self):
        if not self.check_cam():
            return None
        success, frame = self.cam.read()
        if not success:
            return None
        else:
            return frame

    def close_cam(self):
        if self.cam is not None:
            self.cam.release()
            self.cam = None

    def check_cam(self):
        if self.cam is None:
            warnings.warn("Camera is not activated")
        elif not self.cam.isOpened():
            warnings.warn("Camera is activated but not opened. "
                          "Try disable the MJPG-streamer with `sudo service webcamd stop`."
                          "If still fail to open the camera, check the device.")
        else:
            return True
        return False

    def set_up_cam(self, device="http://octopi.local/webcam/?action=stream"):
        # Release the resource first before restart the camera
        if self.cam is not None:
            self.cam.release()

        self.cam = cv2.VideoCapture(device)
        self.check_cam()

    @staticmethod
    def __send_reqeust(url, data=None, use_post=False, use_file=False):
        try:
            if use_post:
                assert data is not None, "Data should not be `None` for sending post"
                response = requests.post(url, json=data)
                return response
            elif use_file:
                assert data is not None, "Data should not be `None` for sending post"
                response = requests.post(url, files=data)
                return response
            else:
                response = requests.get(url)
                return response.json()
        except requests.exceptions.ConnectionError:
            raise ValueError("Server is not working. Please check the service")

    def get_file_list(self):
        get_file_url = f"{self.base_url}/files?apikey={self.api_key}"
        return self.__send_reqeust(get_file_url)

    def get_specific_temperature(self, target="tool"):
        get_temp_url = f"{self.base_url}/printer/{target}?apikey={self.api_key}"
        return self.__send_reqeust(get_temp_url)

    def get_all_temperature(self):
        get_temp_url = f"{self.base_url}/printer?apikey={self.api_key}"
        return self.__send_reqeust(get_temp_url)

    def check_bed_heated(self):
        get_board_temp = self.get_specific_temperature("bed")
        temp_actual = get_board_temp["bed"]["actual"]
        temp_target = get_board_temp["bed"]["target"]

        return (temp_target != 0.) and (abs(temp_target - temp_actual) > 1)

    def check_tool_heated(self):
        get_tool_temp = self.get_specific_temperature("tool")
        temp_actual = get_tool_temp["tool0"]["actual"]
        temp_target = get_tool_temp["tool0"]["target"]

        return (temp_target != 0.) and (abs(temp_target - temp_actual) > 1)

    def get_job_state(self):
        get_job_state_url = f"{self.base_url}/job?apikey={self.api_key}"
        return self.__send_reqeust(get_job_state_url)

    def get_printed_progress(self):
        """Get the progress of current work. `job_state` is used to track the current state of printer"""
        job_state = self.get_job_state()

        if job_state["state"] in ["Printing", "Pausing", "Paused", "Printing from SD"]:
            completion = job_state["progress"]["completion"]
            print_time_left = job_state["progress"]["printTimeLeft"]

            if self.check_bed_heated():
                job_state["state"] = "board heated"
            elif self.check_tool_heated():
                job_state["state"] = "tool heated"

            return {
                "job_state": job_state["state"],
                "completion": completion,
                "print_time_left": print_time_left
            }
        else:
            return {
                "job_state": "Not printed"
            }

    def get_connect_state(self):
        get_connect_state_url = f"{self.base_url}/connection?apikey={self.api_key}"
        return self.__send_reqeust(get_connect_state_url)

    def is_connected(self):
        connect_state = self.get_connect_state()
        return connect_state["current"]["state"] != "Closed"

    def get_printer_profile(self, user="_default"):
        get_profile_url = f"{self.base_url}/printerprofiles/{user}?apikey={self.api_key}"
        return self.__send_reqeust(get_profile_url)

    def get_user_profile(self):
        get_user_url = f"{self.base_url}/currentuser?apikey={self.api_key}"
        return self.__send_reqeust(get_user_url)

    def get_current_user(self):
        user_profile = self.get_user_profile()

        if "admins" in user_profile["groups"]:
            role = "admins"
        else:
            role = user_profile["groups"][0]

        return {
            "name": user_profile["name"],
            "role": role
        }

    def upload_file(self, filename):
        upload_file_url = f"{self.base_url}/files/local?apikey={self.api_key}"
        res = self.__send_reqeust(
            upload_file_url, data={"file": open(filename, "rb"), "filename": os.path.basename(filename)},
            use_file=True)
        return res

    def print_selected_file(self, filename):
        print_file_url = f"{self.base_url}/files/{filename}?apikey={self.api_key}"
        res = self.__send_reqeust(print_file_url, data={"command": "select", "print": "true"}, use_post=True)
        return res


if __name__ == "__main__":
    octo_client = OctoClient(use_cap=False)
    frame = octo_client.get_current_user()
    print(frame)
