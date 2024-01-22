import os
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from azure.core.exceptions import ResourceExistsError
import tkinter as tk
from tkinter import messagebox, filedialog
import re
import fnmatch

# Global container options
container_Modes = {
    "Dev": "dev",
    "Operational": "operational",
    "Test_External": "test_external",
    "Test_Internal": "test_internal"
}
# Global Shop options
'''Stores = {
    "Falcomilano": "Falcomilano",
    "FashionDemo": "FashionDemo",
    "Lobby": "Lobby",
    "Mersivx": "Mersivx",
    "Mxshopify": "Mxshopify",
    "NintendoIL": "NintendoIL",
    "SuperMarketDemo": "SuperMarketDemo",
    "AllShops": "AllShops"
}'''
# available upload types
Content_Type = {
    "app + streaming": "app + streaming",
    "app (all but streaming assets)": "app (all but streaming assets)",
    "streaming only": "streaming only",
    "config only": "config only"
}

storage_connection_strings={}
container_id = '$web'

def saveUserSelections(container_name,flag ,store_names , contentType):
    store_names_str = ', '.join(store_names)

    selections = '\ncontainer_name: '+container_name + ';\nStoreName: ' + store_names_str  +';\ncontentType: '+contentType
    print('user selections:' + selections)

def upload_single_file(blob_service_client, file_path, blob_name):
    """
    Upload a single file to the Azure Blob Storage.
    """
    content_type = 'text/html'
    content_settings = ContentSettings(content_type=content_type, content_encoding='')
    blob_obj = blob_service_client.get_blob_client(container=container_id, blob=blob_name)
    with open(file_path, 'rb') as file_data:
        #blob_obj.upload_blob(file_data, overwrite=True)
        blob_obj.upload_blob(file_data, overwrite=True, content_settings=content_settings)

def get_cache_control_value(file_name, cache_control):
    for pattern in cache_control.keys():
        if fnmatch.fnmatch(file_name, pattern):
            return cache_control[pattern]
    return None

def uploadFiles(container_name,flag ,selected_stores , contentType):

    #check if all stores was selected
    IsAllStoreSelected = 'AllShops' in selected_stores
    print("IsAllStoreSelected " + str(IsAllStoreSelected))

    #save user selections to log file
    saveUserSelections(container_name,flag ,selected_stores , contentType)

    #connect to the container
    connection_string = storage_connection_strings[container_name.lower()]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

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

            if (contentType == 'app (all but streaming assets)' and ('StreamingAssets'.lower() in folder_path.lower())):
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
                if(contentType == 'app (all but streaming assets)' or contentType == 'app + streaming') and file_name.lower() in "index.html":
                    print("skip index file")
                    index_folder_path = folder_path
                    index_file_path = os.path.join(folder_path, file_name)
                elif (not ('Stores'.lower() in folder_path.lower()) ) or IsAllStoreSelected or ( any(store.lower() in folder_path.lower() for store in selected_stores) ):
                    store_names_str = ', '.join(selected_stores)
                    print("### store.lower() " + store_names_str +" ,folderpath "+folder_path.lower())

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

                            content_settings = ContentSettings(content_type=content_type, content_encoding=content_encoding,cache_control=cache_control_value)
                            blob_obj.upload_blob(file_data, overwrite=True,content_settings=content_settings)
                            ##blob_obj.upload_blob()
                            ##blob_obj.upload_blob(file_data)

                    except ResourceExistsError as e:
                        print('Blob (file object) {0} already exists.'.format(file_name))
                        continue
                    except Exception as e:
                        raise Exception(e)

    if(uploadIndex):
        real_index_path = os.path.join(folder_path, "index.html")
        if os.path.exists(index_file_path):  # Check if the real index.html file exists
            upload_single_file(blob_service_client, index_file_path, "index.html")
    ###
    ### Pop up will jump when done uploading
    ###

    messagebox.showinfo("info", "done uploading")

def create_gui():
    window = tk.Tk()
    window.title("Azure Storage Container Management")
    window.geometry("600x300")  # Increased the height to accommodate the dropdown

    # Dropdown menu options
    options = list(container_Modes.keys())
    #store_options = list(Stores.keys())
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
        if content_type != "app (all but streaming assets)" and not selected_stores:
            messagebox.showwarning("Warning", "No stores selected. Please select at least one store.")
            return
        # Proceed with uploading files if stores are selected
        uploadFiles(clicked.get(), False, selected_stores, content_type)

        # get the user selection stores
    def get_selected_stores():
        return [key for key, var in store_vars.items() if var.get()]

    upload_button = tk.Button(window, text="upload", command=upload_button_command)
    upload_button.grid(row=2, column=1, padx=10, pady=10)

    # Call update_shop_selection initially to set initial state of checkboxes
    update_shop_selection()

    window.mainloop()



def read_storage_connection_string_from_file():
    current_dir = os.getcwd()
    filename = "storage_connection.txt"
    file_path = os.path.join(current_dir, filename)

    with open(file_path, "r") as file:
        file_contents = file.read()

    connection_strings = {}
    for line in file_contents.splitlines():
        match = re.match(r'(\w+)_storage_connection_string\s*=\s*\'(.+?)\'', line)
        if match:
            name, connection_string = match.groups()
            connection_strings[name] = connection_string

    return connection_strings

def change_global_var(streamingAsset_flag):
    streamingAsset_flag = True
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

def read_stores_from_file():
    current_dir = os.getcwd()
    filename = "stores_config.txt"
    file_path = os.path.join(current_dir, filename)
    stores = {}

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split('=')
                stores[key] = value

    return stores

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


if __name__ == "__main__":

    storage_connection_strings = read_storage_connection_string_from_file()
    # print(storage_connection_strings)
    Stores = read_stores_from_file()
    # print(Stores)
    cache_control = read_cache_control_config()
    #print(cache_control)

    #blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)


    create_gui()


