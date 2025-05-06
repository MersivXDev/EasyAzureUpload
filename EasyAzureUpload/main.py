import os
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceExistsError
import tkinter as tk
from tkinter import messagebox, filedialog
import re
import fnmatch
from datetime import datetime
from azure.core.exceptions import ResourceExistsError, ServiceResponseError
import socket  # Import the socket library


# Global container options
container_Modes = {
    "Dev": "dev",
    "Operational": "operational",
    "Test_External": "test_external",
    "Test_Internal": "test_internal"
}

# available upload types
Content_Type = {
    "app + streaming": "app + streaming",
    "app (all but streaming assets)": "app (all but streaming assets)",
    "streaming only": "streaming only",
    "config only": "config only"
}

storage_connection_strings={}
container_id = '$web'

from azure.storage.blob import BlobClient, BlobServiceClient
from datetime import datetime
import os


def append_to_log_in_blob(blob_service_client, container_name, log_message):
    blob_name = 'log.txt'
    log_file_path = 'log.txt'  # Path to the local log file

    try:
        # Attempt to download the existing log file from the blob
        blob_client = blob_service_client.get_blob_client(container=container_id, blob=blob_name)
        ##blob_obj = blob_service_client.get_blob_client(container=container_id, blob=log.txt)

        with open(log_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
    except Exception as e:
        print(f"No existing log file found or an error occurred: {e}. Creating a new one.")

    # Append the new log message to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_message + "\n")

    # Re-upload the updated log file to the blob
    with open(log_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        print("Log file updated and uploaded successfully.")


def log_upload_event(blob_service_client, container_name, userPrefs, outcome):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    machine_name = socket.gethostname()  # Get the machine name
    if(outcome==True):
        result = "success"
    else:
        result = "failed"

    log_message = f"\n\n\nUpload Time:{timestamp}\nDevice: {machine_name}\nUser prefs: {userPrefs}\nOutcome: {result}"

    # Call the function to append the log message to the blob
    append_to_log_in_blob(blob_service_client, container_name, log_message)


def saveUserSelections(container_name,flag ,store_names , contentType):
    store_names_str = ', '.join(store_names)

    if 'AllShops' in store_names :
        store = 'AllShops'
    elif len(store_names) == 0 :
        store = 'No Store, App changes'
    else:
        store = store_names

    selections = f"\nStoreName:{store}\ncontentType: '{contentType}"

    print('user selections:' + selections)
    return selections

def upload_single_file(blob_service_client, file_path, blob_name):
    """
    Upload a single file to the Azure Blob Storage.
    """
    content_type = 'text/html'
    #content_settings = ContentSettings(content_type=content_type, content_encoding='')
    file_name = os.path.basename(file_path)

    content_settings = ContentSettings(content_type=content_type, content_encoding='',cache_control=get_cache_control_value(file_name,cache_control))

    blob_obj = blob_service_client.get_blob_client(container=container_id, blob=blob_name)

    with open(file_path, 'rb') as file_data:
        #blob_obj.upload_blob(file_data, overwrite=True)
        blob_obj.upload_blob(file_data, overwrite=True, content_settings=content_settings)

def get_cache_control_value(file_name, cache_control):
    ans = ""
    # First, check for an exact match
    if file_name in cache_control:
        ans = cache_control[file_name]

    if ans == "":
        # No exact match found, proceed to check for pattern matches
        for pattern in cache_control.keys():
            if fnmatch.fnmatch(file_name, pattern) :
                ans = cache_control[pattern]

    # If no pattern matches, return None
    if ans=="":
        return None
    else:
        return ans

def uploadFiles(container_name,flag ,selected_stores , contentType, folders_to_ignore):
    #check if all stores was selected
    IsAllStoreSelected = 'AllShops' in selected_stores
    print("IsAllStoreSelected " + str(IsAllStoreSelected))

    #save user selections to log file
    userPrefs = saveUserSelections(container_name,flag ,selected_stores , contentType)

    #connect to the container
    connection_string = storage_connection_strings[container_name.lower()]
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string,
        transport_options={
            'connection_timeout': 300,  # Sets the connection timeout to 90 seconds
            'read_timeout': 300  # Sets the read timeout to 90 seconds
        }
    )

    # choose build folder
    folder_path = filedialog.askdirectory(title="Select build Folder")
    print('folder_path '+folder_path)

    uploadIndex = False
    if (contentType == 'app (all but streaming assets)' or contentType == 'app + streaming'):
        # Upload the dummy index.html file first
        uploadIndex = True
        dummy_index_path = os.path.join("", "index.html")
        upload_single_file(blob_service_client, dummy_index_path, "index.html")
    # build folder
    OG_PARENT_FOLDER = splitall(folder_path)[-1]
    print('OG_PARENT_FOLDER ' + OG_PARENT_FOLDER)


    if OG_PARENT_FOLDER.lower().endswith('build'):
        index_before_build = OG_PARENT_FOLDER.index('Build') - 1
        temptry = splitall(folder_path)[index_before_build - 1]

    for folder_path, subdirectories, files in os.walk(folder_path):

        for file_name  in files:
            folder_path_components = splitall(folder_path)
            if(any(x in folder_path_components for x in folders_to_ignore)):
                print("trying to ignore folders")

            elif (contentType == 'app (all but streaming assets)' and ('Stores'.lower() in folder_path.lower())):
                #skip streaming assets in this case
                print("app (all but streaming assets) - skip streaming assets")
            elif (contentType == 'config only' and not ('Config'.lower() in folder_path.lower())):
                # skip everything which is not config
                print("config only - skip everything which is not config")
            elif (contentType == 'streaming only' and not ('StreamingAssets'.lower() in folder_path.lower())):
                # skip everything which is not streaming
                print("streaming only - skip everything which is not streaming")
            else:

                #if ( (IsAllStoreSelected == False) and ('StreamingAssets'.lower() in folder_path.lower())):
                # if(contentType == 'app (all but streaming assets)' or contentType == 'app + streaming') and file_name.lower() in "index.html":
                #     print("skip index file")
                #
                #     index_folder_path = folder_path
                #     index_file_path = os.path.join(folder_path, file_name)
                if (not ('stores' in folder_path.lower())) or IsAllStoreSelected or (
                        any(store in folder_path_components for store in selected_stores)):
                    store_names_str = ', '.join(selected_stores)
                    print("folderpath " + folder_path.lower())
                #elif (not ('Stores'.lower() in folder_path.lower()) ) or IsAllStoreSelected or ( any(store.lower() in folder_path.lower() for store in selected_stores) ):
                 #   store_names_str = ', '.join(selected_stores)
                  #  print("### store.lower() " + store_names_str +" ,folderpath "+folder_path.lower())
                    # Assuming selected_stores is a list of store names in lowercase



                    try:
                        file_path = os.path.join(folder_path, file_name)
                        #print('file_path ' + file_path)

                        ##new revised code:
                        if OG_PARENT_FOLDER=="Build":
                            file_path2 = file_path.split(temptry, 1)[-1]
                        else:
                            file_path2 = file_path.split(OG_PARENT_FOLDER, 1)[-1]
                        #print(' before file_path2 ' + file_path2)
                        file_path2 = re.sub(r'^[^a-zA-Z0-9]+', '', file_path2)
                        #print(' after file_path2 ' + file_path2)

                        print(file_path2)
                        blob_obj = blob_service_client.get_blob_client(container=container_id, blob=file_path2)

                        with open(file_path, mode='rb') as file_data:

                            content_encoding = ''

                            # cache control handling
                            cache_control_value = get_cache_control_value(file_name, cache_control)

                            #Handling for gzip
                            if file_name.lower().endswith('.wasm.gz'):
                                content_type = 'application/wasm'
                                content_encoding = 'gzip'
                            elif file_name.lower().endswith('.data.gz') or file_name.lower().endswith('.js.gz'):
                                content_type = 'application/gzip'
                                content_encoding = 'gzip'
                            # Handling for brotli
                            elif file_name.lower().endswith('.wasm.br'):
                                content_type = 'application/wasm'
                                content_encoding = 'br'
                            elif file_name.lower().endswith('.data.br') or file_name.lower().endswith('.js.br'):
                                content_type = 'application/octet-stream'
                                content_encoding = 'br'
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
                            elif file_name.lower().endswith('.svg'):
                                content_type = 'image/svg+xml'
                            else:
                                print("this file is diff :" + file_name)
                                content_type = 'application/octet-stream'

                            content_settings = ContentSettings(content_type=content_type, content_encoding=content_encoding,cache_control=cache_control_value)
                            blob_obj.upload_blob(file_data, overwrite=True,content_settings=content_settings)

                    except ResourceExistsError as e:
                        print('Blob (file object) {0} already exists.'.format(file_name))
                        continue
                    except Exception as e:
                        log_upload_event(blob_service_client, container_name, userPrefs, False)
                        print('Exception: ' ,e)
                        #raise Exception(e)

    # if(uploadIndex):
    #     real_index_path = os.path.join(folder_path, "index.html")
    #     if os.path.exists(index_file_path):  # Check if the real index.html file exists
    #         upload_single_file(blob_service_client, index_file_path, "index.html")


    #create the log file
    log_upload_event(blob_service_client, container_name, userPrefs, True)


    ###
    ### Pop up will jump when done uploading
    ###
    print("\n" + "=" * 40)
    print("\n" + "=" * 40)
    print("\n" + "=" * 40)
    print(" 🚀 UPLOAD COMPLETE 🚀 ")
    print("=" * 40 + "\n")
    print("\n" + "=" * 40)
    print("\n" + "=" * 40)
    messagebox.showinfo("info", "done uploading")

def create_gui():
    window = tk.Tk()
    window.title("Azure Storage Container Management")
    window.geometry("800x600")  # Increased the height to accommodate the dropdown

    # Dropdown menu options
    options = list(storage_connection_strings.keys())
    Content_options = list(Content_Type.keys())

    # Function to update shop selection based on content type
    def update_shop_selection(*args):
        content_type = clicked3.get()
        is_disabled = content_type == "app (all but streaming assets)"
        for store_key in store_vars:
            chk = checkboxes[store_key]  # Get the checkbox widget directly from the dictionary
            chk.configure(state="disabled" if is_disabled else "normal")
            if is_disabled:
                store_vars[store_key].set(False)

    # Container selection
    container_label = tk.Label(window, text="Select container:")
    container_label.grid(row=0, column=0, padx=10, pady=10)

    clicked = tk.StringVar()
    clicked.set(options[0])
    drop = tk.OptionMenu(window, clicked, *options)
    drop.grid(row=0, column=1, padx=10, pady=10)

    container_label2 = tk.Label(window, text="Select shop(s):")
    container_label2.grid(row=0, column=2, padx=10, pady=10)

    store_vars = {}
    checkboxes = {}  # Dictionary to store the checkbox widgets


    # Folders to Ignore selection
    folder_ignore_vars = {}
    folder_ignore_checkboxes = {}  # Dictionary to store the checkbox widgets for folders to ignore

    container_label_folders = tk.Label(window, text="Folders to Ignore:")
    container_label_folders.grid(row=0, column=4, padx=10, pady=10)

    for i, folder_name in enumerate(foldersIgnore.keys()):
        folder_ignore_vars[folder_name] = tk.BooleanVar()
        chk = tk.Checkbutton(window, text=folder_name, var=folder_ignore_vars[folder_name])
        chk.grid(row=i, column=5, sticky="w")
        folder_ignore_checkboxes[folder_name] = chk

    def handle_all_stores_toggle():
        is_all_stores_selected = store_vars["AllShops"].get()
        for store_key in store_vars:
            if store_key != "AllShops":
                store_vars[store_key].set(is_all_stores_selected)

    for i, (store_key, store_name) in enumerate(Stores.items()):
        store_vars[store_key] = tk.BooleanVar()
        chk = tk.Checkbutton(window, text=store_name, var=store_vars[store_key])
        chk.grid(row=i, column=3, sticky="w")
        checkboxes[store_key] = chk  # Store the checkbox widget

        if store_key == "AllShops":
            # Bind the special handler to the "All Stores" checkbox
            store_vars[store_key].trace("w", lambda *args: handle_all_stores_toggle())

    container_label3 = tk.Label(window, text="Select content upload:")
    container_label3.grid(row=1, column=0, padx=10, pady=10)

    clicked3 = tk.StringVar()
    clicked3.set(Content_options[0])
    clicked3.trace("w", update_shop_selection)  # Binding the update function
    drop3 = tk.OptionMenu(window, clicked3, *Content_options)
    drop3.grid(row=1, column=1, padx=10, pady=10)

    container_label4 = tk.Label(window, text="Start Uploading")
    container_label4.grid(row=2, column=0, padx=10, pady=10)

    def upload_button_command():
        content_type = clicked3.get()
        selected_stores = get_selected_stores()
        selected_folders_to_ignore = [folder for folder, var in folder_ignore_vars.items() if var.get()]

        if content_type != "app (all but streaming assets)" and not selected_stores:
            messagebox.showwarning("Warning", "No stores selected. Please select at least one store.")
            return
        # Proceed with uploading files if stores are selected
        uploadFiles(clicked.get(), False, selected_stores, content_type, selected_folders_to_ignore)

        # get the user selection stores
    def get_selected_stores():
        return [key for key, var in store_vars.items() if var.get()]

    upload_button = tk.Button(window, text="upload", command=upload_button_command)
    upload_button.grid(row=2, column=1, padx=10, pady=10)

    # Call update_shop_selection initially to set initial state of checkboxes
    update_shop_selection()

    window.mainloop()


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts



def read_cache_control_config():
    current_dir = os.getcwd()
    filename = "cache_control_config.txt"
    file_path = os.path.join(current_dir, filename)
    cache_control = {}

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('=', 1)  # Split at the first '='
                if len(parts) == 2:
                    key, value = parts
                    cache_control[key.strip()] = value.strip()

    return cache_control

def read_combined_config():
    current_dir = os.getcwd()
    filename = "config.txt"
    file_path = os.path.join(current_dir, filename)

    # Initializing dictionaries to hold the configuration
    config = {
        "StorageConnections": {},
        "CacheControlConfig": {},
        "StoresConfig": {},
        "FoldersToIgnore": {},
    }

    current_section = None

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            # Check for section headers
            if re.match(r'\[.+\]', line):
                current_section = line.strip('[]')
            # Check for key-value pairs
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                config[current_section][key.strip()] = value.strip().strip('\'"')

    return config

if __name__ == "__main__":
    '''
    #storage_connection_strings = read_storage_connection_string_from_file()
    storage_connection_strings = read_storage_connection_string_from_file2()
    # print(storage_connection_strings)
    Stores = read_stores_from_file()
    # print(Stores)
    cache_control = read_cache_control_config()
    '''
    config = read_combined_config()
    storage_connection_strings = config["StorageConnections"]
    cache_control = config["CacheControlConfig"]
    Stores = config["StoresConfig"]
    foldersIgnore = config["FoldersToIgnore"]
    #print(cache_control)

    #blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)


    create_gui()


