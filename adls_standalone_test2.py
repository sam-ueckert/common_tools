# must install
# pip install azure-storage-file-datalake azure-identity
"""
# These tools provide the ability to interact with files on ADLS

# to import:
from fileclient_adls import AdlsConnection

# Example usage:
   	# get credentials from command line arguments
    tenant_id = sys.argv[1]
	client_id = sys.argv[2]
	client_secret = sys.argv[3]

    # connect to ADLS filesystem "adt-calfit-adls"
    account_url = 'https://adt-calfit-adls@adtedfdatalake.dfs.core.windows.net/'  
	adls_conn = AdlsConnection(tenant_id, client_id, client_secret, account_url)
	
    # this loop would allow you to recursively get or create folders as: /folder/subfolder/2023/03/25 (/folder/subfolder/year/month/day)
    year = time.strftime("%Y")
	month = time.strftime("%m")
	day = time.strftime("%d")
    new_path = ""
	for item in ["folder", "subfolder", year, month, day]:
		new_path = f"{new_path}/{item}"
		print(f"new_path: {new_path}")
		directory_client = adls_conn.create_directory(new_path)
"""
try:
    from azure.identity import ClientSecretCredential
    from azure.storage.filedatalake import (
        DataLakeServiceClient,
        DataLakeServiceClient,
        DataLakeDirectoryClient,
        FileSystemClient,
    )
    from azure.core.paging import ItemPaged
    from azure.core.exceptions import ResourceModifiedError
except:
    print(f"must install azure tools via: 'pip install azure-storage-file-datalake azure-identity'")
import sys, os
import time
import json
import argparse


def to_gzip_file(data_text: str, filename: str) -> None:
    with gzip.open(filename, "wb") as output:
        # We cannot directly write Python objects like strings!
        # We must first convert them into a bytes format using io.BytesIO() and then write it
        with io.TextIOWrapper(output, encoding="utf-8") as encode:
            encode.write(data_text)


class AdlsConnection:
    # this class allows us to use an ADLS filesystem

    def __init__(
        self,
        account_key: str,
        account_url: str,
        file_system_name: str,
        disable_http_logging: bool = False,
    ) -> None:
        """
        Setup connection and authenticate to ADLS
        account_url should look like: 'https://adt-calfit-adls@adtedfdatalake.dfs.core.windows.net/'
        """
        if disable_http_logging:
            import logging

            azure_http_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
            azure_http_logger.setLevel(logging.WARNING)  # this was too talky

        # credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        # self.service_client = DataLakeServiceClient(account_url=account_url, credential=credential)
        self.service_client = DataLakeServiceClient(account_url=account_url, credential=account_key)
        # self.service_client = self.get_service_client_account_key(self, account_name, account_key)
        self.file_system_name = file_system_name
        if self.service_client:
            self.file_system_client = self.service_client.get_file_system_client(file_system=file_system_name)

    # def get_service_client_account_key(self, account_name, account_key) -> DataLakeServiceClient:
    #     account_url = f"https://{account_name}.dfs.core.windows.net"
    #     service_client = DataLakeServiceClient(account_url, credential=account_key)

    #     return service_client

    def get_file_system_client(self, file_system_name: str) -> None:
        """
        Setup connection to ADLS filesystem
        the file_system_name refers to the root of the file system, e.g., 'adt-calfit-adls'
        You don't have to instantiate this unless you did not specify in __init__ as 'file_system_name@hostname'
        """
        self.file_system_name = file_system_name
        if self.service_client:
            self.file_system_client = self.service_client.get_file_system_client(file_system=file_system_name)

    def get_directory(self, directory_path: str) -> DataLakeDirectoryClient:
        """
        returns an object to interact with a specific directory in ADLS filesystem
        """
        directory_client = self.file_system_client.get_directory_client(directory_path)
        return directory_client

    def rename_directory(self, directory_client: DataLakeDirectoryClient, new_dir_name: str) -> None:
        directory_client.rename_directory(new_name=f"{directory_client.file_system_name}/{new_dir_name}")

    def delete_directory(self, directory_client: DataLakeDirectoryClient) -> None:
        directory_client.delete_directory()

    def create_directory(self, directory_path: str) -> DataLakeDirectoryClient:
        """
        Create a directory, this is idempotent:
        1) if directory already exists, do nothing
        2) if directory does not already exist, create the directory

        Returns an object to interact with this specific directory in ADLS filesystem
        """
        directory_client = self.file_system_client.create_directory(directory_path)
        return directory_client

    def create_daily_folders(self, basepath: str) -> DataLakeDirectoryClient:
        directory_client = None
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%d")
        new_path = ""
        for item in [basepath, year, month, day]:
            new_path = f"{new_path}/{item}"
            print(f"new_path: {new_path}")
            directory_client = self.create_directory(new_path)
        return directory_client

    def download_file_from_directory(
        self,
        directory_client: DataLakeDirectoryClient,
        local_path: str,
        local_file_name: str,
        adls_file_name: str,
    ) -> None:
        file_client = directory_client.get_file_client(adls_file_name)

        with open(file=os.path.join(local_path, local_file_name), mode="wb") as local_file:
            download = file_client.download_file()
            local_file.write(download.readall())
            local_file.close()

    def upload_file_to_directory(
        self,
        directory_client: DataLakeDirectoryClient,
        local_path: str,
        file_name: str,
        adls_filename: str | None = None,
        overwrite=True,
    ) -> None:
        """
        Uploads a local file to ADLS, by default this WILL overwrite an existing file of the same name
        (optional) use adls_filename to specify a different filename to create on ADLS
        """
        try:
            if adls_filename:
                remote_filename = adls_filename
            else:
                remote_filename = file_name
            file_client = directory_client.get_file_client(remote_filename)
            with open(file=os.path.join(local_path, file_name), mode="rb") as data:
                file_client.upload_data(data, overwrite=overwrite)
        except ResourceModifiedError as e:
            raise Exception(
                f"Cannot upload file '{adls_file_name}' because it already exists on destination and you set 'overwrite=False'"
            )

    def upload_data_to_directory(
        self,
        directory_client: DataLakeDirectoryClient,
        adls_file_name: str,
        data: str | bytes,
        overwrite=True,
    ) -> None:
        """
        Uploads data to create a new file on ADLS, by default this WILL overwrite an existing file of the same name
        data can be either str or bytes (utf-8 encoding)
        str will be converted to bytes (utf-8 encoding)
        """
        try:
            if type(data) == str:
                data = data.encode("utf-8")
            file_client = directory_client.get_file_client(adls_file_name)
            print(
                f"directory_client.get_directory_properties().name: {directory_client.get_directory_properties().name}"
            )
            file_client.upload_data(data, overwrite=overwrite)
        except ResourceModifiedError as e:
            raise Exception(
                f"Cannot upload file '{adls_file_name}' because it already exists on destination and you set 'overwrite=False'"
            )

    def list_directory_contents(
        self,
        directory: str | DataLakeDirectoryClient,
        recursive: bool = False,
        print_tree=True,
        print_list=False,
    ) -> ItemPaged:
        """
        Lists the contents of a directory

            directory can be either:
                str:  directory_path should look like 'folder' or 'folder/subfolder/subfolder'
                DataLakeDirectoryClient: DataLakeDirectoryClient object

            recursive lists all subdirectories
            print_tree give an easy to read tree view
            print_list gives a flatteneed list of paths


        You can use the returned object as:
            items = list_directory_contents(directory_path)
            for item in items:
                print(item.name)

        """

        def _print_directory_contents(paths: ItemPaged, directory_path: str | None) -> None:
            if directory_path is None:
                return
            else:
                indent = ""
                directory_path = directory_path.strip("/")
                root = f"[{self.file_system_name}]/{directory_path}"
                print_tree_items = [root]
                print_list_items = [root]

                for path in paths:
                    if print_tree:
                        indent = 2 * " " * str(path).count("/")
                        if path.is_directory:
                            print_tree_items.append(f"{indent}/{path.name.split('/')[-1]}")
                        else:
                            print_tree_items.append(f"{indent}{path.name.split('/')[-1]}")
                    if print_list:
                        print_list_items.append(f"{root}/{path.name}")
                if print_tree:
                    print("---------------------------")
                    for item in print_tree_items:
                        print(item)
                if print_list:
                    print("---------------------------")
                    for item in print_list_items:
                        print(item)

        if type(directory) == str:
            directory_path = directory
        elif type(directory) == DataLakeDirectoryClient:
            directory_path = directory.get_directory_properties().name
        else:
            directory_path = None
            raise Exception(f"'{directory}' is not a valid path string or DataLakeDirectoryClient")

        paths = self.file_system_client.get_paths(path=directory_path, recursive=recursive)

        if print_tree or print_list:
            _print_directory_contents(paths, directory_path)

        return paths


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
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-a",
        "--account_url",
        help="ADLS account url, e.g., https://adtedfdatalake.dfs.core.windows.net/",
        required=True,
    )
    arg_parser.add_argument(
        "-f",
        "--file_system_name",
        help="ADLS file system name, e.g., 'adt-calfit-adls'",
        required=True,
    )
    arg_parser.add_argument(
        "-k",
        "--account_key",
        help="Client Secret (password) for accessing ADLS",
        required=True,
    )

    ARGS = arg_parser.parse_args()
    account_key = ARGS.account_key
    account_url = ARGS.account_url
    file_system_name = ARGS.file_system_name

    adls_conn = AdlsConnection(account_key, account_url, file_system_name)
    year = time.strftime("%Y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    timestamp = f"{year}-{month}-{day}"
    test_data = f"test at {timestamp}"

    local_upload_path = "./test/upload"
    local_download_path = "./test/download"
    adls_test_path = "/test/delete_me"
    test_filename = f"test_delete_me_{timestamp}.txt.gz"
    test_upload_filepath = os.path.join(local_upload_path, test_filename)
    test_download_filepath = os.path.join(local_download_path, test_filename)

    print("------------------")
    adls_conn.list_directory_contents(directory=adls_test_path, recursive=True)
    print("------------------")

    new_path = ""
    # create folders in ADLS
    for item in ["test", "delete_me", year, month, day]:
        new_path = f"{new_path}/{item}"
        print(f"new_path: {new_path}")
        directory_client = adls_conn.create_directory(new_path)

    # adls_conn.upload_file_to_directory(directory_client, "./", junk_filename)
    # with open(junk_filename, mode="rb") as bytes_data:
    to_gzip_file(test_data, test_filename)
    with open(test_upload_filepath, mode="rb") as zipped_data:
        adls_conn.upload_data_to_directory(directory_client, test_filename, zipped_data, overwrite=False)
    time.sleep(2)
    adls_conn.download_file_from_directory(directory_client, local_download_path, test_filename, test_filename)

    adls_conn.list_directory_contents(directory=adls_test_path, recursive=True)
    directory_client = adls_conn.get_directory(directory_path=adls_test_path)
    items = adls_conn.list_directory_contents(directory=directory_client, recursive=True, print_list=True)

    with gzip.open(test_download_filepath, "rb") as f:
        file_content = f.read()
        if file_content == test_data:
            print(f"SUCCESS: test data matches")
        else:
            print(f"FAILED: file_content: '{file_content}', does not match test_data: '{test_data}'")

    with open("test_unzip.json", "wb") as json_out:
        json_out.write(file_content)
        json_out.close()
