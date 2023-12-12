# just some dev testing for fileclient_adls

from fileclient_adls import AdlsConnection
import sys, os
import json

##Example paths
# /Logs/Redhat_Linux
# /Landing/Redhat_Linux
# /Landing/Redhat_Linux/Lifecycle
# /Landing/Redhat_Linux/CVE
# /Landing/Redhat_Linux/Hosts/2023/09/25/response_redhat_hosts_2023-09-25.json
import time
import gzip
import io


def to_gzip_file(data_text: str, filename: str) -> None:
    with gzip.open(filename, "wb") as output:
        # We cannot directly write Python objects like strings!
        # We must first convert them into a bytes format using io.BytesIO() and then write it
        with io.TextIOWrapper(output, encoding="utf-8") as encode:
            encode.write(data_text)


if __name__ == "__main__":
    tenant_id = sys.argv[1]
    client_id = sys.argv[2]
    client_secret = sys.argv[3]
    # account_url = 'https://adt-calfit-adls@adtedfdatalake.dfs.core.windows.net/'
    account_url = "https://adtedfdatalake.dfs.core.windows.net/"
    file_system_name = "adt-calfit-adls"
    adls_conn = AdlsConnection(
        tenant_id, client_id, client_secret, account_url, file_system_name
    )
    # adls_conn.get_file_system_client(file_system_name)
    year = time.strftime("%Y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    timestamp = f"{year}-{month}-{day}"
    junk_filename = f"test_junk_delete_me_2023-12-11-c.json"
    junk_filename_gzip = f"test_junk_delete_me_2023-12-11-c.gzip"
    print("------------------")
    adls_conn.list_directory_contents(directory="/Logs/delete_me", recursive=True)
    print("------------------")

    new_path = ""
    for item in ["Logs", "delete_me", year, month, day]:
        new_path = f"{new_path}/{item}"
        print(f"new_path: {new_path}")
        directory_client = adls_conn.create_directory(new_path)

    # adls_conn.upload_file_to_directory(directory_client, "./", junk_filename)
    # with open(junk_filename, mode="rb") as bytes_data:
    # 	adls_conn.upload_data_to_directory(directory_client, junk_filename, bytes_data)
    # with open(junk_filename, mode="r") as text_data:
    # 	adls_conn.upload_data_to_directory(directory_client, junk_filename, text_data.read())
    with open(junk_filename, mode="r") as raw_data:
        to_gzip_file(raw_data.read(), junk_filename_gzip)
        raw_data.close()
        with open(junk_filename_gzip, mode="rb") as zipped_data:
            adls_conn.upload_data_to_directory(
                directory_client, junk_filename_gzip, zipped_data, overwrite=False
            )
    time.sleep(2)
    download_filename = f"foo_{junk_filename_gzip}"
    adls_file_name = junk_filename
    adls_conn.download_file_from_directory(
        directory_client, ".", download_filename, junk_filename_gzip
    )
    # with open(download_filename, "r") as open_file:
    # 	bar = json.load(open_file)

    # 	open_file.close()
    # print(json.dumps(bar, indent=4))
    # print(json.dumps(bar))
    # print(bar)
    adls_conn.list_directory_contents(directory="Logs", recursive=True)
    directory_client = adls_conn.get_directory(directory_path="Logs")
    items = adls_conn.list_directory_contents(
        directory=directory_client, recursive=True, print_list=True
    )

    with gzip.open(junk_filename_gzip, "rb") as f:
        file_content = f.read()

    with open("test_unzip.json", "wb") as json_out:
        json_out.write(file_content)
        json_out.close()
