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
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient,
)
from azure.core.paging import ItemPaged
from azure.core.exceptions import ResourceModifiedError
import sys, os
import time


class AdlsConnection:
    # this class allows us to use an ADLS filesystem

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        account_url: str,
        file_system_name: str,
        disable_http_logging: bool = True,
    ) -> None:
        """
        Setup connection and authenticate to ADLS
        account_url should look like: 'https://adt-calfit-adls@adtedfdatalake.dfs.core.windows.net/'
        file_system_name should look like: 'adt-calfit-adls'
        """
        if disable_http_logging:
            import logging

            azure_http_logger = logging.getLogger(
                "azure.core.pipeline.policies.http_logging_policy"
            )
            azure_http_logger.setLevel(logging.WARNING)  # this was too talky

        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.service_client = DataLakeServiceClient(
            account_url=account_url, credential=credential
        )
        self.file_system_name = file_system_name
        if self.service_client:
            self.file_system_client = self.service_client.get_file_system_client(
                file_system=file_system_name
            )

    def get_file_system_client(self, file_system_name: str) -> None:
        """
        Setup connection to ADLS filesystem
        the file_system_name refers to the root of the file system, e.g., 'adt-calfit-adls'
        You don't have to instantiate this unless you did not specify in __init__ as 'file_system_name@hostname'
        """
        self.file_system_name = file_system_name
        if self.service_client:
            self.file_system_client = self.service_client.get_file_system_client(
                file_system=file_system_name
            )

    def get_directory(self, directory_path: str) -> DataLakeDirectoryClient:
        """
        returns an object to interact with a specific directory in ADLS filesystem
        """
        directory_client = self.file_system_client.get_directory_client(directory_path)
        return directory_client

    def rename_directory(
        self, directory_client: DataLakeDirectoryClient, new_dir_name: str
    ) -> None:
        directory_client.rename_directory(
            new_name=f"{directory_client.file_system_name}/{new_dir_name}"
        )

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

        with open(
            file=os.path.join(local_path, local_file_name), mode="wb"
        ) as local_file:
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

        def _print_directory_contents(
            paths: ItemPaged, directory_path: str | None
        ) -> None:
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
                            print_tree_items.append(
                                f"{indent}/{path.name.split('/')[-1]}"
                            )
                        else:
                            print_tree_items.append(
                                f"{indent}{path.name.split('/')[-1]}"
                            )
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
            raise Exception(
                f"'{directory}' is not a valid path string or DataLakeDirectoryClient"
            )

        paths = self.file_system_client.get_paths(
            path=directory_path, recursive=recursive
        )

        if print_tree or print_list:
            _print_directory_contents(paths, directory_path)

        return paths
