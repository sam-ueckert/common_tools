"""
# Shared file tools module
"""
import json
import gzip
import io
import time
import path
import yaml
# from log_tools import log_exceptions
from .log_tools import log_exceptions

@log_exceptions
def get_yaml_settings(directory, filename):
    with open(f'{directory}/{filename}', 'r') as f:
        return yaml.safe_load(f)

@log_exceptions
def get_shared_settings():
    current_directory = path.Path(__file__).parent.abspath()
    return get_yaml_settings(current_directory, 'shared_settings.yml')

@log_exceptions
def format_elapsed_time(elapsed_seconds:float) -> str:
    hours = 0
    minutes = 0
    seconds = 0
    
    if elapsed_seconds > 3600:
        hours, elapsed_seconds = divmod(elapsed_seconds, 3600)

    if elapsed_seconds > 60:
        minutes, elapsed_seconds = divmod(elapsed_seconds, 60)
    hours = round(hours)
    minutes = round(minutes)
    seconds = round(elapsed_seconds, 2)
    if hours < 10:
        hours = f"0{hours}"
    if minutes < 10:
        minutes = f"0{minutes}"
    if seconds < 10:
        seconds = f"0{seconds}"
        
    return f'{hours}:{minutes}:{seconds}'

def get_timestamp_for_filename(time_obj: time) -> str:
    # standardized timestamp to append to filename
    return f"{time_obj.strftime('%H_%M__%m_%d_%Y')}"

@log_exceptions
def load_json_file(filename: str) -> dict:
	with open(filename, "r") as openfile:
		json_object = json.load(openfile)
		openfile.close()
		return json_object
	
@log_exceptions
def to_json_file(json_data: json, filename: str) -> None:
	if not type(json_data) is str:
		json_data = json.dumps(json_data, indent=4)
	with open(filename, "w") as outfile:
		outfile.write(json_data)
		outfile.close()

@log_exceptions
def to_gzip_file(data_text: str, filename: str) -> None:
	with gzip.open(filename, 'wb') as output:
	# We cannot directly write Python objects like strings!
	# We must first convert them into a bytes format using io.BytesIO() and then write it
		with io.TextIOWrapper(output, encoding='utf-8') as encode:
			encode.write(data_text)

if __name__ == '__main__':
    print("Example tools (you are running this as a script instead of importing)")
    