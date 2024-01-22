import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceExistsError
import time

import tkinter as tk
from tkinter import messagebox, filedialog
import re



def delete_container():
    # Delete a container
    container_client= blob_service_client.get_container_client(container_id)
    if container_client.exists():
        try:
            # Delete the container (asynchronously)
            container_client.delete_container()

            # Wait for the deletion operation to complete
            while True:
                try:
                    # Attempt to get the container, this will raise an exception if it doesn't exist
                    time.sleep(5)
                    container_client = blob_service_client.create_container(container_id)
                    messagebox.showinfo("info" , "container deleted")
                    break# Wait for 1 second before checking again
                except ResourceExistsError :
                    print('ResourceExistsError')

                    # Container is deleted, exit the loop
                    #break

        except Exception as e:
            # Handle any exceptions that occur during the deletion process
            print("Error occurred during container deletion:", str(e))
    else:
        # The container doesn't exist, so you can skip it
        print("Container doesn't exist. Skipping...")
    # Create a container

    #container_client = blob_service_client.create_container(container_id)
    #print("Container created successfully. ")


    ##container_client = blob_service_client.create_container(container_id)
    # container_client = blob_service_client.get_container_client(container_id)
    ##print(container_client)




    # List containers
    all_containers = blob_service_client.list_containers(include_metadata=True)
    for container in all_containers:
        print(container)

    # Upload a blob to a container
    blob_root_directory = ''
    working_dir = os.getcwd()
    file_directory = os.walk(working_dir + '/dbt')
    folder_path = filedialog.askdirectory(title="Select Folder")
    for folder_path, subdirectories, files in os.walk(folder_path):
    #for folder in file_directory:
        for file_name in files:

            try:
                file_path = os.path.join(folder_path, file_name)
                relative_path = os.path.relpath(file_path, working_dir)
                x = re.sub(r'^\.\.\\\\', '', relative_path)
                # x = relative_path.lstrip('\\')
                blob_path = '{0}/{1}'.format(blob_root_directory, x)

                # print(remove_subdirectory_from_path(blob_path))
                y = blob_path.replace('/..\\', '')
                z = get_substring_after_first_backslash(y);
                print(z)
                blob_obj = blob_service_client.get_blob_client(container=container_id, blob=z)
                with open(file_path, mode='rb') as file_data:

                    content_type = ''
                    content_encoding = ''

                    if file_name.lower().endswith('.wasm.gz'):
                        content_type = 'application/wasm'
                        content_encoding = 'gzip'
                    elif file_name.lower().endswith('.data.gz') or file_name.lower().endswith('.js.gz'):
                        content_type = 'application/gzip'
                        content_encoding = 'gzip'
                    elif file_name.lower().endswith('.json'):
                        content_type = 'application/json'
                    elif file_name.lower().endswith('.js'):
                        content_type = 'text/javascript'
                    elif file_name.lower().endswith('.mp4'):
                        content_type = 'video/mp4'
                    elif file_name.lower().endswith('.webm'):
                        content_type = 'video/webm'
                    elif file_name.lower().endswith('.wasm'):
                        content_type = 'application/wasm'
                    elif file_name.lower().endswith('.mp3'):
                        content_type = 'audio/mpeg'
                    elif file_name.lower().endswith('.png'):
                        content_type = 'image/png'
                    elif file_name.lower().endswith('.jpg'):
                        content_type = 'image/jpeg'
                    elif file_name.lower().endswith('.ico'):
                        content_type = 'image/x-icon'
                    elif file_name.lower().endswith('.html'):
                        content_type = 'text/html'
                    elif file_name.lower().endswith('.css'):
                        content_type = 'text/css'
                    else:
                        print("this file is diff :" + file_name)
                        content_type = 'application/octet-stream'

                    content_settings = ContentSettings(content_type=content_type, content_encoding=content_encoding)
                    blob_obj.upload_blob(file_data, content_settings=content_settings)
                    ##blob_obj.upload_blob()
                    ##blob_obj.upload_blob(file_data)

            except ResourceExistsError as e:
                print('Blob (file object) {0} already exists.'.format(file_name))
                continue
            except Exception as e:
                raise Exception(e)
    messagebox.showinfo("info", "done uploading")
    # List blobs (file objects) in a given container
    blobs = container_client.list_blobs()



def delete_container2():
    all_containers = blob_service_client.list_containers(include_metadata=True)
    for container in all_containers:
        print(container)

    # Upload a blob to a container
    blob_root_directory = ''
    working_dir = os.getcwd()
    file_directory = os.walk(working_dir + '/dbt')
    folder_path = filedialog.askdirectory(title="Select Folder")
    for folder_path, subdirectories, files in os.walk(folder_path):
    #for folder in file_directory:
        #print(folder)
        #folder_path = folder[0]
        #files = folder[2]

        for file_name  in files:
            #print(file)
            if folder_path.lower().endswith('build'):

                try:
                    file_path = os.path.join(folder_path, file_name)
                    relative_path = os.path.relpath(file_path, working_dir)
                    x = re.sub(r'^\.\.\\\\', '', relative_path)
                    #x = relative_path.lstrip('\\')
                    blob_path = '{0}/{1}'.format(blob_root_directory, x)

                    #print(remove_subdirectory_from_path(blob_path))
                    y = blob_path.replace('/..\\', '')
                    z = get_substring_after_first_backslash(y);
                    print (z)
                    blob_obj = blob_service_client.get_blob_client(container=container_id, blob=z)

                    with open(file_path, mode='rb') as file_data:

                        content_type = ''
                        content_encoding = ''

                        if file_name.lower().endswith('.wasm.gz'):
                            content_type = 'application/wasm'
                            content_encoding = 'gzip'
                        elif file_name.lower().endswith('.data.gz') or file_name.lower().endswith('.js.gz'):
                            content_type = 'application/gzip'
                            content_encoding = 'gzip'
                        elif file_name.lower().endswith('.json'):
                            content_type = 'application/json'
                        elif file_name.lower().endswith('.js'):
                            content_type = 'text/javascript'
                        elif file_name.lower().endswith('.mp4'):
                            content_type = 'video/mp4'
                        elif file_name.lower().endswith('.webm'):
                            content_type = 'video/webm'
                        elif file_name.lower().endswith('.wasm'):
                            content_type = 'application/wasm'
                        elif file_name.lower().endswith('.mp3'):
                            content_type = 'audio/mpeg'
                        elif file_name.lower().endswith('.png'):
                            content_type = 'image/png'
                        elif file_name.lower().endswith('.jpg'):
                            content_type = 'image/jpeg'
                        elif file_name.lower().endswith('.ico'):
                            content_type = 'image/x-icon'
                        elif file_name.lower().endswith('.html'):
                            content_type = 'text/html'
                        elif file_name.lower().endswith('.css'):
                            content_type = 'text/css'
                        else:
                            print("this file is diff :" + file_name)
                            content_type = 'application/octet-stream'

                        content_settings = ContentSettings(content_type=content_type, content_encoding=content_encoding)
                        blob_obj.upload_blob(file_data, overwrite=True,content_settings=content_settings)
                        ##blob_obj.upload_blob()
                        ##blob_obj.upload_blob(file_data)

                except ResourceExistsError as e:
                    print('Blob (file object) {0} already exists.'.format(file_name))
                    continue
                except Exception as e:
                    raise Exception(e)

    messagebox.showinfo("info", "done uploading")

def get_substring_after_first_backslash(input_string):
    first_backslash_index = input_string.find('\\')
    if first_backslash_index != -1:
        return input_string[first_backslash_index + 1:]
    else:
        return input_string

input_string = 'webgl3\\Build\\webgl3.framework.js.gz'
substring = get_substring_after_first_backslash(input_string)
print(substring)


# blobs = container_client.list_blobs(name_starts_with='dbt')
# for blob in blobs:
#     print(blob['name'])
#     print(blob['container'])
#     print(blob['snapshot'])
#     print(blob['version_id'])
#     print(blob['is_current_version'])
#     print(blob['blob_type'])
#     print(blob['blob_tier'])
#     print(blob['metadata'])
#     print(blob['creation_time'])
#     print(blob['last_modified'])
#     print(blob['last_accessed_on'])
#     print(blob['size'])
#     print(blob['deleted'])
#     print(blob['deleted_time'])
#     print(blob['tags'])

# Download a blob
##file_object_path = 'dbt/2. Build dbt projects/1. Build your DAG/Exposures dbt Developer Hub.pdf'
#file_downloaded = os.path.join(working_dir, 'Exposures dbt Developer Hub.pdf')

##with open(file_downloaded, mode='wb') as download_file:
##    download_file.write(container_client.download_blob(file_object_path).readall())

# Delete a blob (subfolder in this example)
##blobs = container_client.list_blobs()
##for blob in blobs:
    ##    if blob.name.startswith('dbt/List of commands/'):
    ##    container_client.delete_blob(blob.name)
##    print('Blob {0} deleted'.format(blob.name))
def create_gui():
    window = tk.Tk()
    window.title("Azure Storage Container Management")
    window.geometry("300x150")

    delete_button = tk.Button(window, text="overwrite all", command=delete_container)
    delete_button.pack(pady=20)
    delete_button2 = tk.Button(window, text="overwrite build folder", command=delete_container2)
    delete_button2.pack(pady=20)
    window.mainloop()


def read_storage_connection_string_from_file():
    current_dir = os.getcwd()

    # Specify the name of your file
    filename = "storage_connection.txt"

    # Join the directory and filename to create the complete file path
    file_path = os.path.join(current_dir, filename)

    with open(file_path, "r") as file:
        #storage_connection_string = file.read()
        #lines = file.readlines()
        file_contents = file.read()
    # Print the storage connection string
    pattern = r"storage_connection_string\s*=\s*'(.+?)'"
    match = re.search(pattern, file_contents)
    if match:
        storage_connection_string = match.group(1)
    else:
        storage_connection_string = None
    print(storage_connection_string)

    return storage_connection_string


if __name__ == "__main__":
    storage_connection_string = read_storage_connection_string_from_file()
    print(storage_connection_string)
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

    container_id = '$web'
    create_gui()


