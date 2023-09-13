from Utilities.utils import FileManager



class LloydAC:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            file_name = FileManager.find_file("lloyd_ac.json")
            uid_json = FileManager.manage_file(file_name, "r")
            cls._data = uid_json["lloyd_ac"]

    @classmethod
    def get_command(cls, command_str):
        if cls._data is None:
            cls._load_data()

        for key, value in cls._data.items():
            if isinstance(value, dict) and command_str in value:
                return value[command_str]
        else:
            raise ValueError(f"Command {command_str} not found!")






