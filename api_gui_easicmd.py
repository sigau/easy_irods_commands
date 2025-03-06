#!/usr/bin/env python3
# -*- coding: utf-8 -*

##########################################################################################################################################################################################################################################################################################
####  contact info 
##########################################################################################################################################################################################################################################################################################
# Author: Gautier Debaecker
# Date: October 2024
# Copyright (c) 2024 by Gautier Debaecker
# Special thanks to Beyoncé for the inspiration
# GitHub: https://github.com/sigau
# License: MIT License 

##########################################################################################################################################################################################################################################################################################
####  calling library
##########################################################################################################################################################################################################################################################################################

import tkinter as tk
from tkinter import ttk
from tkinter import *
import os, sys
from tkinter.messagebox import *
from tkinter.filedialog import *
import api_easicmd as easicmd
from api_easicmd import *
import ttkwidgets
from ttkwidgets.autocomplete import AutocompleteEntry
import customtkinter


################################################################################################################################################################################################################################################################################
### GUI called function's definition (function that will be "called" by the user)
################################################################################################################################################################################################################################################################################


def GUIPUSH():
    INIT_PUSH()


def GUIPULL():
    INIT_PULL()


def GUIIMKDIR():
    INIT_IMKDIR()


def GUIIRM():
    INIT_IRM()


def GUIADDMETA():
    INIT_ADD_META()


################################################################################################################################################################################################################################################################################
### GUI  tools function's definition (function that will only be use by other functions to avoid redundancy )
################################################################################################################################################################################################################################################################################


def listbox_filter(event):
    sstr = search_str.get()
    gui_list_of_icollection.delete(0, END)
    # If filter removed show all data
    if sstr == "":
        fill_listbox(easicmd.list_of_icollection)
        return

    filtered_data = list()
    for item in easicmd.list_of_icollection:
        if item.find(sstr) >= 0:
            filtered_data.append(item)

    fill_listbox(filtered_data)


def fill_listbox(ld):
    for item in ld:
        gui_list_of_icollection.insert(END, item)


def GUI_TYPE_OBJECT(otype):
    global type_object
    if otype == "file":
        type_object = "-d"
    else:
        type_object = "-C"
    return type_object


def GUI_GET_LOCAL_OBJECT(otype):
    global local_object
    if otype == "file":
        local_object = askopenfilename()
    else:
        local_object = askdirectory(
            title="Which folder (verify the path in selection before validate)"
        )
    return local_object


def WHERE_IN_LOCAL():
    global local_path
    local_path = askdirectory(title="Where do you want to download it")


def GET_IRODS_PATH():
    global irods_path
    if "gui_list_of_icollection" in globals():
        irods_path = gui_list_of_icollection.get(gui_list_of_icollection.curselection())
    else:
        # Get the selected item from the treeview
        selected_item = gui_tree_of_icollection.focus()

        if not selected_item:
            print("No folder selected")
            return

        # Initialize an empty list to hold the folder names
        path_elements = []

        # Traverse the tree upwards from the selected item to the root
        while selected_item:
            # Get the folder name of the current node
            folder_name = gui_tree_of_icollection.item(selected_item, "text")
            path_elements.insert(
                0, folder_name
            )  # Insert at the beginning (reverse order)
            # Move to the parent of the current node
            selected_item = gui_tree_of_icollection.parent(selected_item)

        # Join the path elements to form the full path
        irods_path = "/" + "/".join(path_elements)

        # Print the full path
        print(irods_path)


def GET_IRODS_FILE_PATH():
    global irods_path_file
    irods_path_file = (
        f"{irods_path}/{gui_list_of_ifile.get(gui_list_of_ifile.curselection())}"
    )


def PROGRESS_BAR(command):
    global pb
    win_pb = customtkinter.CTkToplevel()
    pb = ttk.Progressbar(win_pb, orient="horizontal", mode="indeterminate", length=280)
    pb.pack(padx=10, pady=20)
    pb.start()
    command
    pb.stop()


################################################################################################################################################################################################################################################################################
### TREE RELATED FUNCTION
################################################################################################################################################################################################################################################################################


# Get the next level of folders based on the current path
def get_next_level_folders(current_path, folder_list):
    next_level = set()
    current_path = current_path.rstrip("/") + "/"  # Ensure trailing slash for matching

    for folder in folder_list:
        if folder.startswith(current_path):
            relative_path = folder[len(current_path) :]
            first_level_folder = relative_path.split("/")[
                0
            ]  # Get the immediate subfolder
            next_level.add(current_path + first_level_folder)

    return sorted(next_level)


# Populate Treeview with folders and track nodes
def populate_treeview(treeview, parent_node, folder_list):
    for folder in folder_list:
        folder_name = folder.rstrip("/").split("/")[-1]  # Only show the folder name
        node_id = treeview.insert(parent_node, "end", text=folder_name, values=[folder])
        # Track all nodes for searching later
        all_nodes[folder] = node_id
        # Add a dummy item to allow expansion (+ symbol in tree)
        treeview.insert(node_id, "end", text="Loading...", values=["dummy"])


# Function to load subfolders dynamically when a folder is expanded
def on_treeview_open(event):
    treeview = event.widget
    selected_item = treeview.focus()
    folder_path = treeview.item(selected_item, "values")[0]  # Get the full folder path

    # Check if it's a dummy node, if so, load the actual content
    children = treeview.get_children(selected_item)
    if len(children) == 1 and treeview.item(children[0], "values")[0] == "dummy":
        # Remove the dummy item
        treeview.delete(children[0])

        # Fetch the next level of subfolders
        subfolders = get_next_level_folders(folder_path, easicmd.list_of_icollection)

        # Populate the tree with the actual subfolders
        populate_treeview(treeview, selected_item, subfolders)


# Function to filter the Treeview based on search input
def treeview_filter(event):
    search_term = search_str.get().lower()

    # Show/hide nodes based on whether they match the search term
    for folder, node_id in all_nodes.items():
        item_text = folder.lower()
        if search_term in item_text:
            # Make sure the node and its parents are visible
            expand_tree_to_node(gui_tree_of_icollection, node_id)
        else:
            # Hide the node if it doesn't match the search term
            gui_tree_of_icollection.detach(node_id)


# Helper function to expand all parent nodes and make a node visible
def expand_tree_to_node(treeview, node):
    parent = treeview.parent(node)
    if parent:
        # If the parent has a dummy node, remove it and load its children
        if (
            len(treeview.get_children(parent)) == 1
            and treeview.item(treeview.get_children(parent)[0], "values")[0] == "dummy"
        ):
            on_treeview_open_parent(treeview, parent)
        treeview.item(parent, open=True)  # Expand the parent
        expand_tree_to_node(treeview, parent)  # Recursively expand all ancestors
    treeview.reattach(node, "", "end")  # Reattach the node itself


# Function to load children when opening parent for search
def on_treeview_open_parent(treeview, parent_node):
    folder_path = treeview.item(parent_node, "values")[0]
    subfolders = get_next_level_folders(folder_path, easicmd.list_of_icollection)
    populate_treeview(treeview, parent_node, subfolders)


################################################################################################################################################################################################################################################################################
### PUSH
################################################################################################################################################################################################################################################################################


def to_irods_and_beyond():
    GET_IRODS_PATH()
    showinfo(
        title="Transfer's Begining",
        message="Click to run the transfer\nAnother pop-up will show when finish",
    )
    with iRODSSession(**easicmd.irods_config) as session:
        if type_object == "-d":
            session.data_objects.put(local_object, irods_path, num_threads=nb_threads)
        else:
            easicmd.copy_folder_to_irods(
                local_object,
                local_object,
                irods_path,
                session,
                easicmd.list_of_icollection,
            )

    showinfo(
        title="All Your Bytes Are Belong To Us",
        message="End of Transfer : The data should be on irods now",
    )


def WHERE_TO_IRODS():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    win_where.title("WHERE TO SEND DATA")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [
            win_where.after(100, win_where.destroy),
            to_irods_and_beyond(),
        ],
    ).pack(side="bottom")


def INIT_PUSH():

    win = customtkinter.CTkToplevel()
    win.title("warning")
    # Get screen width and height
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2
    win.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win, text=message).pack()
    customtkinter.CTkButton(
        win,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win.destroy(),
            GUI_GET_LOCAL_OBJECT("file"),
            WHERE_TO_IRODS(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win.destroy(),
            GUI_GET_LOCAL_OBJECT("folder"),
            WHERE_TO_IRODS(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
# PULL
################################################################################################################################################################################################################################################################################


def DOWNLOAD(itype):
    showinfo(
        title="Transfer's Begining",
        message="Click to run the transfer\nAnother pop-up will show when finish",
    )
    with iRODSSession(**easicmd.irods_config) as session:
        if itype == "-C":
            easicmd.copy_irod_to_folder(
                session,
                irods_path.replace("//", "/"),
                local_path.replace("//", "/"),
                recursive=True,
            )
        else:
            session.data_objects.get(
                irods_path_file.replace("//", "/"), local_path.replace("//", "/")
            )
    showinfo(title="End of Transfer", message="The data should be on your local now")


def GET_IRODS_FILE():
    global gui_list_of_ifile
    win_where = customtkinter.CTkToplevel()
    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile = Listbox(win_where)
    for i in easicmd.ifile:
        gui_list_of_ifile.insert(easicmd.ifile.index(i) + 1, i)
    gui_list_of_ifile.pack(fill="both", expand="yes")
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [
            GET_IRODS_FILE_PATH(),
            win_where.destroy(),
            WHERE_IN_LOCAL(),
            DOWNLOAD("-f"),
        ],
    ).pack(side="bottom")


def PULL_FROM_IRODS(itype):
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()

    if itype == "-C":
        win_where.title("WHICH FOLDER")
    else:
        win_where.title("FIRST SELECT THE FOLDER")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    if itype == "-C":
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [
                GET_IRODS_PATH(),
                win_where.destroy(),
                WHERE_IN_LOCAL(),
                DOWNLOAD("-C"),
            ],
        ).pack(side="bottom")
    else:
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [GET_IRODS_PATH(), win_where.destroy(), GET_IRODS_FILE()],
        ).pack(side="bottom")


def INIT_PULL():
    win_pull = customtkinter.CTkToplevel()
    win_pull.title("warning pull")

    # Get screen width and height
    screen_width = win_pull.winfo_screenwidth()
    screen_height = win_pull.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_pull.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_pull, text=message).pack()
    customtkinter.CTkButton(
        win_pull,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_pull.destroy(),
            PULL_FROM_IRODS("-f"),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_pull,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_pull.destroy(),
            PULL_FROM_IRODS("-C"),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
###imkdir
################################################################################################################################################################################################################################################################################


def CMD_IMKDIR():
    easicmd.IMKDIR(f"{irods_path}/{new_folder}")


def GET_NAME():
    global new_folder
    new_folder = entree.get()
    if " " in new_folder:
        showinfo(message="I HAVE REPLACE SPACE WITH UNDERSCORE !!!")
        new_folder = new_folder.replace(" ", "_")
    CMD_IMKDIR()


def GIVE_NAME():
    global entree
    win_name = customtkinter.CTkToplevel()
    customtkinter.CTkLabel(
        win_name, text="name of the new folder :\n NO SPACE ONLY '_' "
    ).pack()
    entree = customtkinter.CTkEntry(win_name, width=250)
    entree.pack(padx=5, pady=5, side=LEFT)
    entree.focus_force()
    btnAffiche = customtkinter.CTkButton(
        win_name, text="create", command=lambda: [GET_NAME(), win_name.destroy()]
    ).pack(padx=5, pady=5)


def INIT_IMKDIR():

    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    win_where.title("WHERE DO YOU WANT TO CREATE YOUR FOLDER")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_PATH(), win_where.destroy(), GIVE_NAME()],
    ).pack(side="bottom")


################################################################################################################################################################################################################################################################################
###irm
################################################################################################################################################################################################################################################################################


def DESTROY():
    if type_object == "-C":
        easicmd.IRM("-C", irods_path)
    else:
        easicmd.IRM("-d", irods_path_file)
    showinfo(message="DATA HAS BEEN DESTROYED")


def GET_IRM_FILE_NAME():
    global gui_list_of_ifile
    win_where = customtkinter.CTkToplevel()

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile = Listbox(win_where)
    for i in easicmd.ifile:
        gui_list_of_ifile.insert(easicmd.ifile.index(i) + 1, i)
    gui_list_of_ifile.pack(fill="both", expand="yes")
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_FILE_PATH(), win_where.destroy(), DESTROY()],
    ).pack(side="bottom")


def IRM_GET_FOLDER():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else:
        win_where.title("FIRST CHOOSE THE FOLDER ")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    if type_object == "-C":
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [GET_IRODS_PATH(), win_where.destroy(), DESTROY()],
        ).pack(side="bottom")
    else:
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [
                GET_IRODS_PATH(),
                win_where.destroy(),
                GET_IRM_FILE_NAME(),
            ],
        ).pack(side="bottom")


def INIT_IRM():
    win_pull = customtkinter.CTkToplevel()
    win_pull.title("warning IRM")

    # Get screen width and height
    screen_width = win_pull.winfo_screenwidth()
    screen_height = win_pull.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_pull.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_pull, text=message).pack()
    customtkinter.CTkButton(
        win_pull,
        text="FILE",
        command=lambda: [GUI_TYPE_OBJECT("file"), win_pull.destroy(), IRM_GET_FOLDER()],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_pull,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_pull.destroy(),
            IRM_GET_FOLDER(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
##ADD_META
################################################################################################################################################################################################################################################################################def CLEAR_TEXT():


def CLEAR_TEXT():
    attribut.delete(0, END)
    value.delete(0, END)
    units.delete(0, END)


def ADD_META_CMD():
    with iRODSSession(**easicmd.irods_config) as session:
        if type_object == "-C":
            obj = session.collections.get(irods_path)
            obj.metadata.add(attribut.get(), value.get(), units.get())

        else:
            obj = session.data_objects.get(irods_path_file)
            obj.metadata.add(attribut.get(), value.get(), units.get())

    ##updating the autocompletion dictionary
    change = False
    if attribut.get() not in easicmd.dico_attribute:
        easicmd.dico_attribute[attribut.get()] = set()
        easicmd.dico_attribute[attribut.get()].add(value.get())
        change = True

    else:
        if value.get() not in easicmd.dico_attribute[attribut.get()]:
            easicmd.dico_attribute[attribut.get()].add(value.get())
            change = True

    if change == True:
        file_name = os.path.expanduser(pickle_meta_dictionary_path)
        with open(file_name, "wb") as f:
            pickle.dump(easicmd.dico_attribute, f)
        print(f"Dictionary have been update in {file_name}")


def GIVE_META():
    global attribut
    global value
    global units
    easicmd.read_attributes_dictionnary()
    list_value = []
    list_attr = []
    for i in easicmd.dico_attribute.values():
        for (
            j
        ) in (
            i
        ):  ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for attr in easicmd.dico_attribute.keys():
        list_attr.append(attr)
    list_attr.sort(key=str.lower)
    list_value.sort(key=str.lower)
    win_name_addmeta = customtkinter.CTkToplevel()
    win_name_addmeta.title("ADD METADATA (* is mandatory)")
    customtkinter.CTkLabel(win_name_addmeta, text="attribut* : ").grid(row=0)
    customtkinter.CTkLabel(win_name_addmeta, text="value* : ").grid(row=1)
    customtkinter.CTkLabel(win_name_addmeta, text="units : ").grid(row=2)
    attribut = AutocompleteEntry(win_name_addmeta, width=20, completevalues=list_attr)
    attribut.grid(row=0, column=1)
    value = AutocompleteEntry(win_name_addmeta, width=20, completevalues=list_value)
    value.grid(row=1, column=1)
    empty_list = []
    units = AutocompleteEntry(win_name_addmeta, width=20, completevalues=empty_list)
    units.grid(row=2, column=1)
    validate_button = customtkinter.CTkButton(
        win_name_addmeta,
        text="validate",
        command=lambda: [
            ADD_META_CMD(),
            CLEAR_TEXT(),
            win_name_addmeta.destroy(),
            GIVE_META(),
        ],
    )
    validate_button.grid(row=0, column=2)
    exit_button = customtkinter.CTkButton(
        win_name_addmeta, text="exit", command=lambda: [win_name_addmeta.destroy()]
    )
    exit_button.grid(row=3, column=2)


def GET_ADDMETA_FILE_NAME():
    global gui_list_of_ifile
    win_where = customtkinter.CTkToplevel()

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile = Listbox(win_where)
    for i in easicmd.ifile:
        gui_list_of_ifile.insert(easicmd.ifile.index(i) + 1, i)
    gui_list_of_ifile.pack(fill="both", expand="yes")
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_FILE_PATH(), win_where.destroy(), GIVE_META()],
    ).pack(side="bottom")


def ADDMETA_GET_IRODS_PATH():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else:
        win_where.title("FIRST CHOOSE THE FOLDER ")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)
    if type_object == "-C":
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [GET_IRODS_PATH(), win_where.destroy(), GIVE_META()],
        ).pack(side="bottom")
    else:
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [
                GET_IRODS_PATH(),
                win_where.destroy(),
                GET_ADDMETA_FILE_NAME(),
            ],
        ).pack(side="bottom")


def INIT_ADD_META():
    win_addmeta = customtkinter.CTkToplevel()
    win_addmeta.title("warning ADD METADATA")

    # Get screen width and height
    screen_width = win_addmeta.winfo_screenwidth()
    screen_height = win_addmeta.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_addmeta.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_addmeta, text=message).pack()
    customtkinter.CTkButton(
        win_addmeta,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_addmeta.destroy(),
            ADDMETA_GET_IRODS_PATH(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_addmeta,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_addmeta.destroy(),
            ADDMETA_GET_IRODS_PATH(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
### rm_meta
################################################################################################################################################################################################################################################################################


def RM_META_CMD():
    att = str(attribut.get())
    val = str(value.get())
    with iRODSSession(**easicmd.irods_config) as session:
        if type_object == "-C":
            obj = session.collections.get(irods_path)
        else:
            obj = session.data_objects.get(irods_path_file)

        metadata = obj.metadata.items()
        if att == "*":
            for avu in obj.metadata.items():
                obj.metadata.remove(avu)
        else:
            obj.metadata.remove(att, val, units.get())


def GET_RM_ATTR():
    global attribut
    global value
    global units
    easicmd.read_attributes_dictionnary()
    list_value = []
    list_attr = []
    for i in easicmd.dico_attribute.values():
        for (
            j
        ) in (
            i
        ):  ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for attr in easicmd.dico_attribute.keys():
        list_attr.append(attr)
    list_attr.sort(key=str.lower)
    list_value.sort(key=str.lower)
    win_name_addmeta = customtkinter.CTkToplevel()
    win_name_addmeta.title("REMOVE METADATA (* for all)")
    customtkinter.CTkLabel(win_name_addmeta, text="attribut : ").grid(row=0)
    customtkinter.CTkLabel(win_name_addmeta, text="value : ").grid(row=1)
    attribut = AutocompleteEntry(win_name_addmeta, width=20, completevalues=list_attr)
    attribut.grid(row=0, column=1)
    value = AutocompleteEntry(win_name_addmeta, width=20, completevalues=list_value)
    value.grid(row=1, column=1)
    units = customtkinter.CTkEntry(win_name_addmeta, width=20)
    validate_button = customtkinter.CTkButton(
        win_name_addmeta, text="validate", command=lambda: [RM_META_CMD(), CLEAR_TEXT()]
    )
    validate_button.grid(row=0, column=2)
    exit_button = customtkinter.CTkButton(
        win_name_addmeta, text="exit", command=lambda: [win_name_addmeta.destroy()]
    )
    exit_button.grid(row=3, column=2)


def GET_RMMETA_FILE_NAME():
    global gui_list_of_ifile
    win_where = customtkinter.CTkToplevel()
    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile = Listbox(win_where)
    for i in easicmd.ifile:
        gui_list_of_ifile.insert(easicmd.ifile.index(i) + 1, i)
    gui_list_of_ifile.pack(fill="both", expand="yes")
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_FILE_PATH(), win_where.destroy(), GET_RM_ATTR()],
    ).pack(side="bottom")


def RMMETA_GET_IRODS_PATH():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else:
        win_where.title("FIRST CHOOSE THE FOLDER ")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    if type_object == "-C":
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [GET_IRODS_PATH(), win_where.destroy(), GET_RM_ATTR()],
        ).pack(side="bottom")
    else:
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [
                GET_IRODS_PATH(),
                win_where.destroy(),
                GET_RMMETA_FILE_NAME(),
            ],
        ).pack(side="bottom")


def INIT_RM_META():
    win_rmmeta = customtkinter.CTkToplevel()
    win_rmmeta.title("warning ADD METADATA")

    # Get screen width and height
    screen_width = win_rmmeta.winfo_screenwidth()
    screen_height = win_rmmeta.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_rmmeta.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data you want to remove metadata from is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_rmmeta, text=message).pack()
    customtkinter.CTkButton(
        win_rmmeta,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_rmmeta.destroy(),
            RMMETA_GET_IRODS_PATH(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_rmmeta,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_rmmeta.destroy(),
            RMMETA_GET_IRODS_PATH(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
##SHOW META
################################################################################################################################################################################################################################################################################


def PRINT_META(meta_result):
    win_meta = customtkinter.CTkToplevel()
    t = Text(win_meta, height=50, width=104)
    customtkinter.CTkLabel(win_meta, text="Your metadata :").pack()
    t.insert(tk.END, meta_result)
    t.pack()
    button_close = customtkinter.CTkButton(
        win_meta, text="close", command=win_meta.destroy
    )
    button_close.pack(side=BOTTOM)


def GUI_SHOW_META():
    if type_object == "-C":
        meta_result = easicmd.SHOW_META(irods_path)
    else:
        meta_result = easicmd.SHOW_META(irods_path_file)
    PRINT_META(meta_result)


def GET_SHOW_META_FILE_NAME():
    global gui_list_of_ifile
    win_where = customtkinter.CTkToplevel()

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile = Listbox(win_where)
    for i in easicmd.ifile:
        gui_list_of_ifile.insert(easicmd.ifile.index(i) + 1, i)
    gui_list_of_ifile.pack(fill="both", expand="yes")
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_FILE_PATH(), win_where.destroy(), GUI_SHOW_META()],
    ).pack(side="bottom")


def SHOWMETA_GET_IRODS_PATH():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else:
        win_where.title("FIRST CHOOSE THE FOLDER ")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    if type_object == "-C":
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [GET_IRODS_PATH(), win_where.destroy(), GUI_SHOW_META()],
        ).pack(side="bottom")
    else:
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [
                GET_IRODS_PATH(),
                win_where.destroy(),
                GET_SHOW_META_FILE_NAME(),
            ],
        ).pack(side="bottom")


def INIT_SHOW_META():
    win_showmeta = customtkinter.CTkToplevel()
    win_showmeta.title("warning ADD METADATA")

    # Get screen width and height
    screen_width = win_showmeta.winfo_screenwidth()
    screen_height = win_showmeta.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_showmeta.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data you want to show metadata is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_showmeta, text=message).pack()
    customtkinter.CTkButton(
        win_showmeta,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_showmeta.destroy(),
            SHOWMETA_GET_IRODS_PATH(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_showmeta,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_showmeta.destroy(),
            SHOWMETA_GET_IRODS_PATH(),
        ],
    ).pack(side=RIGHT)


####################
##search by meta (not working yet)
####################


def CLEAR_SEARCH_TEXT():
    attribut.delete(0, END)
    value.delete(0, END)
    liaison.delete(0, END)
    operator.delete(0, END)


def SEARCH_GET_CMD():
    global attribut
    global value
    global liaison
    global operator
    global search_meta_cmd

    search_meta_cmd = f"imeta{win_exe} qu {type_object}"
    list_operation = ["=", "like", "'>'", "'<'"]
    list_liaison = ["", "and", "or"]

    easicmd.read_attributes_dictionnary()
    list_value = []
    list_attr = []

    for i in easicmd.dico_attribute.values():
        for (
            j
        ) in (
            i
        ):  ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for attr in easicmd.dico_attribute.keys():
        list_attr.append(attr)
    list_attr.sort(key=str.lower)
    list_value.sort(key=str.lower)

    win_searchcmd = customtkinter.CTkToplevel()
    win_searchcmd.title("SEARCH FOR (* is mandatory)")
    customtkinter.CTkLabel(win_searchcmd, text="attribut* : ").grid(row=0)
    customtkinter.CTkLabel(win_searchcmd, text="operator* (=, like, >, <,) : ").grid(
        row=1
    )
    customtkinter.CTkLabel(win_searchcmd, text="value* : ").grid(row=2)
    customtkinter.CTkLabel(win_searchcmd, text="liaison (and/or): ").grid(row=3)

    attribut = AutocompleteEntry(win_searchcmd, width=20, completevalues=list_attr)
    attribut.grid(row=0, column=1)
    operator = AutocompleteEntry(win_searchcmd, width=20, completevalues=list_operation)
    operator.grid(row=1, column=1)
    value = AutocompleteEntry(win_searchcmd, width=20, completevalues=list_value)
    value.grid(row=2, column=1)
    liaison = AutocompleteEntry(win_searchcmd, width=20, completevalues=list_liaison)
    liaison.grid(row=3, column=1)

    add_button = customtkinter.CTkButton(
        win_searchcmd,
        text="add",
        command=lambda: [BUILD_SEARCH_CMD(), CLEAR_SEARCH_TEXT()],
    )
    add_button.grid(row=0, column=2)
    validate_button = customtkinter.CTkButton(
        win_searchcmd,
        text="validate",
        command=lambda: [EXEC_SEARCH_CMD(), win_searchcmd.destroy()],
    )
    validate_button.grid(row=1, column=2)
    exit_button = customtkinter.CTkButton(
        win_searchcmd, text="exit", command=lambda: [win_searchcmd.destroy()]
    )
    exit_button.grid(row=3, column=2)


def EXEC_SEARCH_CMD():
    global searched_data
    search_meta_cmd_final = f"{search_meta_cmd} {attribut.get()} {operator.get()} {value.get()} {liaison.get()}"
    try:
        searched_data = subprocess.check_output(
            search_meta_cmd_final, shell=True, text=True
        )
    except CalledProcessError:
        searched_data = (
            f"NO DATA ASSOCIATED WITH THE REQUEST \n\n{search_meta_cmd_final}"
        )
    PRINT_SEARCH()


def PRINT_SEARCH():
    win_meta = customtkinter.CTkToplevel()
    t = Text(win_meta, height=25, width=52)
    customtkinter.CTkLabel(win_meta, text="Your searched data are :").pack()
    t.insert(tk.END, searched_data)
    t.pack()
    button_close = customtkinter.CTkButton(
        win_meta, text="close", command=win_meta.destroy
    )
    button_close.pack(side=BOTTOM)


def BUILD_SEARCH_CMD():
    global search_meta_cmd
    new_cmd = f"{search_meta_cmd} {attribut.get()} {operator.get()} {value.get()} {liaison.get()}"
    search_meta_cmd = new_cmd


def INIT_SEARCH_META():
    win_searchmeta = customtkinter.CTkToplevel()
    win_searchmeta.title("warning SEARCH BY METADATA")

    # Get screen width and height
    screen_width = win_searchmeta.winfo_screenwidth()
    screen_height = win_searchmeta.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_searchmeta.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data you're looking for is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_searchmeta, text=message).pack()
    customtkinter.CTkButton(
        win_searchmeta,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_searchmeta.destroy(),
            SEARCH_GET_CMD(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_searchmeta,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_searchmeta.destroy(),
            SEARCH_GET_CMD(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
# SEARCH BY NAME
################################################################################################################################################################################################################################################################################
def SEARCH_FILE_NAME():
    global name
    win_namesearch = customtkinter.CTkToplevel()
    win_namesearch.title("warning SEARCH BY NAME")
    customtkinter.CTkLabel(win_namesearch, text="your query (you can use *): ").pack()
    name = customtkinter.CTkEntry(win_namesearch, width=250)
    name.pack(padx=5, pady=5, side=LEFT)
    Btt_search = customtkinter.CTkButton(
        win_namesearch,
        text="search",
        command=lambda: [FILE_NAME_CMD(), win_namesearch.destroy()],
    )
    Btt_search.pack(side=BOTTOM)


def FILE_NAME_CMD():
    search = name.get()
    search = str(search).replace("*", "%")
    toprint = easicmd.SEARCH_BY_NAME(search, "-f")
    PRINT_NAME(toprint)


def PRINT_NAME(toprint):
    win_printname = customtkinter.CTkToplevel()
    t = Text(win_printname, height=50, width=150)
    customtkinter.CTkLabel(win_printname, text="Your searched data are :").pack()
    t.insert(tk.END, toprint)
    t.pack()
    button_close = customtkinter.CTkButton(
        win_printname, text="close", command=win_printname.destroy
    )
    button_close.pack(side=BOTTOM)


def FOLDER_NAME_CMD():
    search = name.get()
    search = str(search).replace("*", "%")
    toprint = easicmd.SEARCH_BY_NAME(search, "-C")
    PRINT_NAME(toprint)


def SEARCH_FOLDER_NAME():
    global name
    win_namesearch = customtkinter.CTkToplevel()
    win_namesearch.title("warning SEARCH BY NAME")
    customtkinter.CTkLabel(win_namesearch, text="your query (you can use *): ").pack()
    name = customtkinter.CTkEntry(win_namesearch, width=250)
    name.pack(padx=5, pady=5, side=LEFT)
    Btt_search = customtkinter.CTkButton(
        win_namesearch,
        text="search",
        command=lambda: [FOLDER_NAME_CMD(), win_namesearch.destroy()],
    )
    Btt_search.pack(side=BOTTOM)


def INIT_SEARCH_NAME():
    win_searchname = customtkinter.CTkToplevel()
    win_searchname.title("warning SEARCH BY NAME")

    # Get screen width and height
    screen_width = win_searchname.winfo_screenwidth()
    screen_height = win_searchname.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_searchname.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data you're searching is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_searchname, text=message).pack()
    customtkinter.CTkButton(
        win_searchname,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_searchname.destroy(),
            SEARCH_FILE_NAME(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_searchname,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_searchname.destroy(),
            SEARCH_FOLDER_NAME(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
##idush
################################################################################################################################################################################################################################################################################
def GUI_IDUSH():
    global result_size

    result_size = easicmd.IDUSH(irods_path)
    PRINT_IDUST()


def PRINT_IDUST():
    win_meta = customtkinter.CTkToplevel()
    win_meta.title("iRODS iDUSH")
    # Get screen width and height
    screen_width = win_meta.winfo_screenwidth()
    screen_height = win_meta.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 200) // 2
    y_position = (screen_height - 100) // 2

    win_meta.geometry(f"200x100+{x_position}+{y_position}")

    t = Text(win_meta, height=25, width=52)
    customtkinter.CTkLabel(
        win_meta, text=f"Your folder's size is :\n\n{result_size}"
    ).pack()
    button_close = customtkinter.CTkButton(
        win_meta, text="close", command=win_meta.destroy
    )
    button_close.pack(side=BOTTOM)


def INIT_IDUST():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    win_where.title("WHICH FOLDER ?")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_PATH(), win_where.destroy(), GUI_IDUSH()],
    ).pack(side="bottom")


################################################################################################################################################################################################################################################################################
###ICHMOD
################################################################################################################################################################################################################################################################################
def CLEAN_ICHMOD():
    TO.delete(0, END)
    right.delete(0, END)


def ICHMOD_CMD():
    r = right.get()
    if r == "remove/null":
        r = "null"
    t = TO.get()

    with iRODSSession(**easicmd.irods_config) as session:
        if type_object == "-C":
            path = irods_path
            session.acls.set(iRODSAccess(r, irods_path, t), recursive=True)
        else:
            session.acls.set(iRODSAccess(r, irods_path_file, t), recursive=False)
            path = irods_path_file

    showinfo(message=f"You just give {r} access for {path} to {t}")


def ICHMOD_BUILD_CMD(type):
    global TO
    global right
    list_right = ["read", "write", "own", "remove/null"]
    if type == "group":
        easicmd.get_group()
        list_to_show = easicmd.list_group
    else:
        easicmd.get_user()
        list_to_show = easicmd.list_user

    win_cmdichmod = customtkinter.CTkToplevel()
    win_cmdichmod.title("warning ICHMOD")

    customtkinter.CTkLabel(win_cmdichmod, text="give : ").grid(row=0)
    customtkinter.CTkLabel(win_cmdichmod, text="to : ").grid(row=1)
    right = AutocompleteEntry(win_cmdichmod, width=20, completevalues=list_right)
    right.grid(column=1, row=0)
    TO = AutocompleteEntry(win_cmdichmod, width=20, completevalues=list_to_show)
    TO.grid(column=1, row=1)

    BTT_cmd = customtkinter.CTkButton(
        win_cmdichmod, text="select", command=lambda: [ICHMOD_CMD(), CLEAN_ICHMOD()]
    )
    BTT_cmd.grid(column=2, row=0)
    BTT_exit = customtkinter.CTkButton(
        win_cmdichmod, text="exit", command=lambda: [win_cmdichmod.destroy()]
    )
    BTT_exit.grid(column=2, row=2)


def USER_OR_GROUP():
    win_ichmod = customtkinter.CTkToplevel()
    win_ichmod.title("warning ICHMOD")

    # Get screen width and height
    screen_width = win_ichmod.winfo_screenwidth()
    screen_height = win_ichmod.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_ichmod.geometry(f"500x200+{x_position}+{y_position}")

    message = "Share your data with a GROUP or a USER ?"
    customtkinter.CTkLabel(win_ichmod, text=message).pack()
    customtkinter.CTkButton(
        win_ichmod,
        text="USER",
        command=lambda: [
            ICHMOD_BUILD_CMD("user"),
            win_ichmod.destroy(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_ichmod,
        text="GROUP",
        command=lambda: [ICHMOD_BUILD_CMD("group"), win_ichmod.destroy()],
    ).pack(side=RIGHT)


def GET_ICHMOD_FILE_NAME():
    global gui_list_of_ifile
    win_where = customtkinter.CTkToplevel()

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile = Listbox(win_where)
    for i in easicmd.ifile:
        gui_list_of_ifile.insert(easicmd.ifile.index(i) + 1, i)
    gui_list_of_ifile.pack(fill="both", expand="yes")
    select_button = customtkinter.CTkButton(
        win_where,
        text="select",
        command=lambda: [GET_IRODS_FILE_PATH(), win_where.destroy(), USER_OR_GROUP()],
    ).pack(side="bottom")


def ICHMOD_IRODS_PATH():
    easicmd.get_irods_collection()
    global gui_tree_of_icollection, all_nodes
    win_where = customtkinter.CTkToplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else:
        win_where.title("FIRST CHOOSE THE FOLDER ")

    # Get screen width and height
    screen_width = win_where.winfo_screenwidth()
    screen_height = win_where.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 1080) // 2
    y_position = (screen_height - 500) // 2

    win_where.geometry(f"1080x500+{x_position}+{y_position}")

    # Create a Treeview widget
    gui_tree_of_icollection = ttk.Treeview(win_where)
    gui_tree_of_icollection.pack(fill="both", expand="yes")

    # Keep track of all nodes (for search functionality)
    all_nodes = {}

    # Populate the Treeview with the root level (top-level folders)
    root_folders = get_next_level_folders("/", easicmd.list_of_icollection)
    populate_treeview(gui_tree_of_icollection, "", root_folders)

    global search_str
    label_search = customtkinter.CTkLabel(
        win_where, text="Add text to filter the list, then press enter"
    )
    label_search.pack(side=BOTTOM)

    search_str = StringVar()
    search = customtkinter.CTkEntry(win_where, textvariable=search_str, width=300)
    search.pack(padx=5, pady=5, side=BOTTOM)
    search.bind("<Return>", treeview_filter)

    # Bind tree item expansion to dynamically load subfolders
    gui_tree_of_icollection.bind("<<TreeviewOpen>>", on_treeview_open)

    if type_object == "-C":
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [GET_IRODS_PATH(), win_where.destroy(), USER_OR_GROUP()],
        ).pack(side="bottom")
    else:
        select_button = customtkinter.CTkButton(
            win_where,
            text="select",
            command=lambda: [
                GET_IRODS_PATH(),
                win_where.destroy(),
                GET_ICHMOD_FILE_NAME(),
            ],
        ).pack(side="bottom")


def INIT_ICHMOD():
    win_ichmod = customtkinter.CTkToplevel()
    win_ichmod.title("warning ICHMOD")

    # Get screen width and height
    screen_width = win_ichmod.winfo_screenwidth()
    screen_height = win_ichmod.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_ichmod.geometry(f"500x200+{x_position}+{y_position}")

    message = "The data you want to share is a FILE or a FOLDER ?"
    customtkinter.CTkLabel(win_ichmod, text=message).pack()
    customtkinter.CTkButton(
        win_ichmod,
        text="FILE",
        command=lambda: [
            GUI_TYPE_OBJECT("file"),
            win_ichmod.destroy(),
            ICHMOD_IRODS_PATH(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_ichmod,
        text="FOLDER",
        command=lambda: [
            GUI_TYPE_OBJECT("folder"),
            win_ichmod.destroy(),
            ICHMOD_IRODS_PATH(),
        ],
    ).pack(side=RIGHT)


################################################################################################################################################################################################################################################################################
## EDICTIONARY
################################################################################################################################################################################################################################################################################
def UPDATE_DICT():
    file_name = os.path.expanduser(pickle_meta_dictionary_path)
    with open(file_name, "wb") as f:
        pickle.dump(easicmd.dico_attribute, f)
    print(f"Dictionary have been update in {file_name}")


def EDIT_ADD_GETVALUE():
    new_value = value.get()
    value.delete(0, END)
    if new_value not in easicmd.dico_attribute[new_attr]:
        easicmd.dico_attribute[new_attr].append(new_value)
        UPDATE_DICT()


def EDIT_ADD():
    global new_attr
    new_attr = attribut.get()
    attribut.delete(0, END)
    if new_attr not in easicmd.dico_attribute:
        easicmd.dico_attribute[new_attr] = []

    global value
    win_add = customtkinter.CTkToplevel()
    win_add.title(f"Add value to {new_attr} :")

    customtkinter.CTkLabel(win_add, text="value : ").grid(row=0)
    value = customtkinter.CTkEntry(win_add, width=20)
    value.grid(row=0, column=1)

    add_button = customtkinter.CTkButton(
        win_add, text="ADD", command=lambda: [EDIT_ADD_GETVALUE()]
    )
    add_button.grid(row=0, column=2)

    exit_button = customtkinter.CTkButton(
        win_add, text="exit", command=lambda: [win_add.destroy()]
    )
    exit_button.grid(row=2, column=2)


def EDIT_RM_VALUE():
    old_value = value.get()
    value.delete(0, END)
    if old_value in easicmd.dico_attribute[new_attr]:
        easicmd.dico_attribute[new_attr].remove(old_value)
        UPDATE_DICT()


def EDIT_EDIT():
    global new_attr
    new_attr = attribut.get()
    attribut.delete(0, END)

    global value
    win_add = customtkinter.CTkToplevel()
    win_add.title(f"EDITING value form {new_attr} :")

    customtkinter.CTkLabel(win_add, text="value : ").grid(row=0)
    value = AutocompleteEntry(
        win_add, width=20, completevalues=easicmd.dico_attribute[new_attr]
    )
    value.grid(row=0, column=1)

    add_button = customtkinter.CTkButton(
        win_add, text="ADD", command=lambda: [EDIT_ADD_GETVALUE()]
    )
    add_button.grid(row=0, column=2)

    rm_button = customtkinter.CTkButton(
        win_add, text="remove", command=lambda: [EDIT_RM_VALUE()]
    )
    rm_button.grid(row=1, column=2)

    exit_button = customtkinter.CTkButton(
        win_add, text="exit", command=lambda: [win_add.destroy()]
    )
    exit_button.grid(row=2, column=2)


def EDIT_RM_ATTR():
    new_attr = attribut.get()
    attribut.delete(0, END)
    if new_attr in easicmd.dico_attribute:
        easicmd.dico_attribute.pop(new_attr)
        UPDATE_DICT()


def INIT_EDIT():
    easicmd.read_attributes_dictionnary()
    global attribut

    win_edit = customtkinter.CTkToplevel()
    win_edit.title("warning editionary")

    customtkinter.CTkLabel(win_edit, text="attribut* : ").grid(row=0)
    attribut = AutocompleteEntry(
        win_edit, width=20, completevalues=easicmd.dico_attribute.keys()
    )
    attribut.grid(row=0, column=1)

    add_button = customtkinter.CTkButton(
        win_edit, text="create", command=lambda: [EDIT_ADD()]
    )
    add_button.grid(row=1, column=0)

    edit_button = customtkinter.CTkButton(
        win_edit, text="edit existing", command=lambda: [EDIT_EDIT()]
    )
    edit_button.grid(row=1, column=1)

    rm_button = customtkinter.CTkButton(
        win_edit, text="erase ", command=lambda: [EDIT_RM_ATTR()]
    )
    rm_button.grid(row=1, column=2)

    exit_button = customtkinter.CTkButton(
        win_edit, text="exit", command=lambda: [win_edit.destroy()]
    )
    exit_button.grid(row=0, column=2)


################################################################################################################################################################################################################################################################################
## ADD PATH
################################################################################################################################################################################################################################################################################
def CLEAN_PATH():
    path.delete(0, END)


def ADD_PATH():
    new_path = path.get()
    new_path_file = os.path.expanduser(pickle_additional_path_path)
    if os.path.isfile(new_path_file):
        with open(new_path_file, "rb") as f:
            list_new_path = pickle.load(f)
    else:
        list_new_path = []
    if new_path not in list_new_path:
        list_new_path.append(new_path)
    with open(new_path_file, "wb") as f:
        pickle.dump(list_new_path, f)
    print("irods list of path updated")
    easicmd.update_irods_collection2("add", new_path)


def RM_PATH():
    to_remove = path.get()
    new_path_file = os.path.expanduser(pickle_additional_path_path)
    if os.path.isfile(new_path_file):
        with open(new_path_file, "rb") as f:
            list_new_path = pickle.load(f)
        list_new_path.remove(to_remove)
        with open(new_path_file, "wb") as f:
            pickle.dump(list_new_path, f)
        print("irods list of path updated")
        easicmd.update_irods_collection2("remove", to_remove)


def INIT_ADD_PATH():
    global path
    easicmd.get_additional_path()
    win_path = customtkinter.CTkToplevel()
    win_path.title("warning add path")
    customtkinter.CTkLabel(win_path, text="IRODS PATH : ").grid(row=0)
    path = AutocompleteEntry(
        win_path, width=20, completevalues=easicmd.list_additional_path
    )
    path.grid(row=0, column=1)

    edit_button = customtkinter.CTkButton(
        win_path, text="remove", command=lambda: [RM_PATH(), CLEAN_PATH()]
    )
    edit_button.grid(row=1, column=0)

    add_button = customtkinter.CTkButton(
        win_path, text="add", command=lambda: [ADD_PATH(), CLEAN_PATH()]
    )
    add_button.grid(row=1, column=1)

    exit_button = customtkinter.CTkButton(
        win_path, text="exit", command=lambda: [win_path.destroy()]
    )
    exit_button.grid(row=1, column=2)


def INIT_UPD_PATH():
    easicmd.initialise_irods_collection()
    showwarning(
        title="Updating local pickle irods collection",
        message=f"It's done\nthanks for waiting",
    )


################################################################################################################################################################################################################################################################################
## HELP
################################################################################################################################################################################################################################################################################


def help_gui():
    win_help = customtkinter.CTkToplevel()
    win_help.title("help")

    # Get screen width and height
    screen_width = win_help.winfo_screenwidth()
    screen_height = win_help.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_help.geometry(f"500x200+{x_position}+{y_position}")
    message = "For any help go see the README on :"
    customtkinter.CTkLabel(win_help, text=message).pack()
    t = Text(win_help, height=5, width=50)
    t.insert(tk.END, "https://github.com/sigau/easy_irods_commands")
    t.pack()
    customtkinter.CTkButton(
        win_help, text="exit", command=lambda: [win_help.destroy()]
    ).pack(side=BOTTOM)


################################################################################################################################################################################################################################################################################
## CHANGE THEME
################################################################################################################################################################################################################################################################################


def theme_gui():
    win_theme = customtkinter.CTkToplevel()
    win_theme.title("Theme")

    # Get screen width and height
    screen_width = win_theme.winfo_screenwidth()
    screen_height = win_theme.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_theme.geometry(f"500x200+{x_position}+{y_position}")

    message = "Choose the theme you want to use :"
    customtkinter.CTkLabel(win_theme, text=message).pack()

    def radiobutton_event():
        radio_var.get()

    def dark_theme():
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        # print("dark theme selected")

    def light_theme():
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")
        # print("light theme selected")

    def system_theme():
        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("blue")
        # print("default theme selected")

    radio_var = tk.IntVar(value=0)

    radiobutton_1 = customtkinter.CTkRadioButton(
        win_theme, text="DARK", command=dark_theme, variable=radio_var, value=1
    )
    radiobutton_2 = customtkinter.CTkRadioButton(
        win_theme, text="LIGHT", command=light_theme, variable=radio_var, value=2
    )
    radiobutton_3 = customtkinter.CTkRadioButton(
        win_theme, text="SYSTEM", command=system_theme, variable=radio_var, value=3
    )

    # quit_bouton=customtkinter.CTkButton(win_theme, text="quit", command=win_theme.quit).pack(anchor = "center", side=BOTTOM)

    radiobutton_1.pack(padx=20, pady=10)
    radiobutton_2.pack(padx=20, pady=10)
    radiobutton_3.pack(padx=20, pady=10)

################################################################################################################################################################################################################################################################################
## switch user 
################################################################################################################################################################################################################################################################################

def switch_add_user():
    win_switchadd = customtkinter.CTkToplevel()
    win_switchadd.title("warning switch/add user")

    # Get screen width and height
    screen_width = win_switchadd.winfo_screenwidth()
    screen_height = win_switchadd.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_switchadd.geometry(f"500x200+{x_position}+{y_position}")

    message = "Do you want to add or switch user"
    customtkinter.CTkLabel(win_switchadd, text=message).pack()
    customtkinter.CTkButton(
        win_switchadd,
        text="ADD NEW USER",
        command=lambda: [create_user_gui(),
            win_switchadd.destroy(),
        ],
    ).pack(side=LEFT)
    customtkinter.CTkButton(
        win_switchadd,
        text="SWITCH USER",
        command=lambda: [switch_user_gui(), win_switchadd.destroy()],
    ).pack(side=RIGHT)

def create_user_gui():

    create_and_wait_for_config()

    create_and_wait_for_password()

    save_dict = os.path.expanduser(pickle_meta_dictionary_path)

    easicmd.initialise_irods_collection()

    easicmd.irods_collection()

    easicmd.building_attributes_dictionnary()

    easicmd.git_add_file()
    showwarning(
                title="creating new user",
                message=f"It's done\nthanks for waiting",
            )


def switch_user_gui():
    gitrepo=Repo(config_folder)
    repo = gitrepo
    win_theme = customtkinter.CTkToplevel()
    win_theme.title("Switch user")

    # Get screen width and height
    screen_width = win_theme.winfo_screenwidth()
    screen_height = win_theme.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    win_theme.geometry(f"500x200+{x_position}+{y_position}")

    message = "Switch to :"
    customtkinter.CTkLabel(win_theme, text=message).pack()

    list_branch = []
    for branch in repo.heads:
        list_branch.append(branch.name)

    # Add a combobox for branch selection
    selected_branch = StringVar(value=list_branch[0] if list_branch else "No branches available")
    combobox = customtkinter.CTkComboBox(win_theme, values=list_branch, variable=selected_branch)
    combobox.pack(pady=10)

    # Add a button to confirm the selection
    def on_confirm():
        chosen_branch = selected_branch.get()
        print(f"Selected branch: {chosen_branch}")
        easicmd.git_add_file()
        repo.git.checkout(chosen_branch)
        win_theme.destroy()

    confirm_button = customtkinter.CTkButton(win_theme, text="Confirm", command=on_confirm)
    confirm_button.pack(pady=10)
    


################################################################################################################################################################################################################################################################################
## FILL IRODS CONFIG FILE
################################################################################################################################################################################################################################################################################
def config_gui():
    global host_gui
    global port_gui
    global username_gui
    global zone_gui

    win_config = customtkinter.CTkToplevel()
    win_config.title("Config iRODS")

    # Get screen width and height
    screen_width = win_config.winfo_screenwidth()
    screen_height = win_config.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 300) // 2

    # Set the window geometry to position it in the center
    win_config.geometry(f"500x300+{x_position}+{y_position}")

    customtkinter.CTkLabel(win_config, text="        ").grid(row=0, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=1, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=3, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=5, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=7, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=2, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=4, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=6, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=7, column=0)
    customtkinter.CTkLabel(win_config, text="        ").grid(row=8, column=0)

    customtkinter.CTkLabel(win_config, text="host :  ").grid(row=1, column=1)
    customtkinter.CTkLabel(win_config, text="port :  ").grid(row=3, column=1)
    customtkinter.CTkLabel(win_config, text="username :  ").grid(row=5, column=1)
    customtkinter.CTkLabel(win_config, text="zone :  ").grid(row=7, column=1)

    host_gui = customtkinter.CTkEntry(win_config, width=150)
    host_gui.grid(row=1, column=2)
    port_gui = customtkinter.CTkEntry(win_config, width=150)
    port_gui.grid(row=3, column=2)
    username_gui = customtkinter.CTkEntry(win_config, width=150)
    username_gui.grid(row=5, column=2)
    zone_gui = customtkinter.CTkEntry(win_config, width=150)
    zone_gui.grid(row=7, column=2)

    validate_button = customtkinter.CTkButton(
        win_config,
        text="validate",
        command=lambda: [CREATE_IRODS_INFO_GUI(), win_config.destroy()],
    )
    validate_button.grid(row=9, column=4)
    return win_config


def CREATE_IRODS_INFO_GUI():
    irods_config_gui = {
        "host": host_gui.get(),
        "port": port_gui.get(),
        "user": username_gui.get(),
        "zone": zone_gui.get(),
    }
    with open(irods_info_files, "w") as f:
        json.dump(irods_config_gui, f)

    easicmd.git_newbranch(f"{username_gui.get()}_{zone_gui.get()}_{port_gui.get()}")


def create_and_wait_for_config():
    win_config = config_gui()
    win_config.wait_window()


################################################################################################################################################################################################################################################################################
## PASSWORD
################################################################################################################################################################################################################################################################################
def pswd_gui():
    global save_password_var

    win_pswd = customtkinter.CTkToplevel()
    win_pswd.title("iRODS Password")
    message = "Type your password.\nIf you choose to save it, it will be encrypted and stored \nfor later use without the need to retype it."

    # Get screen width and height
    screen_width = win_pswd.winfo_screenwidth()
    screen_height = win_pswd.winfo_screenheight()

    # Calculate the position to center the window
    x_position = (screen_width - 500) // 2
    y_position = (screen_height - 200) // 2

    # Set the window geometry to position it in the center
    win_pswd.geometry(f"500x200+{x_position}+{y_position}")

    customtkinter.CTkLabel(win_pswd, text="        ").grid(row=0, column=0)
    customtkinter.CTkLabel(win_pswd, text=message).grid(row=1, column=2)
    customtkinter.CTkLabel(win_pswd, text="        ").grid(row=2, column=0)

    save_password_var = customtkinter.StringVar(value="on")

    password_gui = customtkinter.CTkEntry(
        win_pswd, width=250
    )  ## add show='*' to mask password
    password_gui.grid(row=3, column=2)

    checkbox = customtkinter.CTkCheckBox(
        win_pswd,
        text="save",
        command=checkbox_event,
        variable=save_password_var,
        onvalue="on",
        offvalue="off",
    )
    checkbox.grid(row=5, column=0)

    validate_button = customtkinter.CTkButton(
        win_pswd,
        text="validate",
        command=lambda: [
            PASSWORD_REGISTER_GUI(save_password_var.get(), password_gui.get()),
            win_pswd.destroy(),
        ],
    )
    validate_button.grid(row=6, column=2)
    return win_pswd


def checkbox_event():
    save_password_var.get()


def PASSWORD_REGISTER_GUI(value, pswd):
    ## we want to save the password
    if value == "on":
        save_pswd(pswd)
        easicmd.get_irods_info()
    else:
        easicmd.get_irods_info()
        easicmd.irods_config["password"] = pswd


def create_and_wait_for_password():
    win_pswd = pswd_gui()
    win_pswd.wait_window()


################################################################################################################################################################################################################################################################################
### creation of the main window (putting the form)
################################################################################################################################################################################################################################################################################


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        master.update_idletasks()  # Permet la mise à jour de la fenêtre

        # Calcul de la taille de la fenêtre sans la barre de titre et les bordures
        width = master.winfo_width() + (
            master.winfo_screenwidth() - master.winfo_reqwidth()
        )
        height = master.winfo_height() + (
            master.winfo_screenheight() - master.winfo_reqheight()
        )
        self._geom = f"{width}x{height}+0+0"

        master.geometry(self._geom)
        master.bind("<Escape>", self.toggle_geom)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        self.master.geometry(self._geom)
        self._geom = geom


class Test(Text):  ###allow control c/v/x in tkinter
    def __init__(self, master, **kw):
        Text.__init__(self, master, **kw)
        self.bind("<Control-c>", self.copy)
        self.bind("<Control-x>", self.cut)
        self.bind("<Control-v>", self.paste)

    def copy(self, event=None):
        self.clipboard_clear()
        text = self.get("sel.first", "sel.last")
        self.clipboard_append(text)

    def cut(self, event):
        self.copy()
        self.delete("sel.first", "sel.last")

    def paste(self, event):
        text = self.selection_get(selection="CLIPBOARD")
        self.insert("insert", text)



try:
    
    ##########################################################################################################################################################################################################################################################################################
    #### number of threads to used
    ##########################################################################################################################################################################################################################################################################################
    nb_threads = os.cpu_count() - 1
    if nb_threads == 0:
        nb_threads = 1

    root = customtkinter.CTk()
    app = FullScreenApp(root)
    root.title("easicmd : easy irods commands graphical edition")

    ##################################################################################################
    ### Work with data (push, pull, imkdir, irm)
    ##################################################################################################
    data = customtkinter.CTkFrame(root)
    data.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    customtkinter.CTkLabel(
        data,
        text="Here you can work with your data like send it to irods, recover it from irods, create ifolders or delete data on irods",
        font=("", 15),
    ).grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    ## PUSH DATA TO IRODS
    push_frame = customtkinter.CTkFrame(data, width=200, height=150)
    push_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    push_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        push_frame, text="Send local data to irods", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        push_frame, text="PUSH", command=GUIPUSH
    ).grid(row=1, column=0, pady=10, sticky="n")


   ## PULL DATA TO IRODS
    pull_frame = customtkinter.CTkFrame(data, width=200, height=150)
    pull_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    pull_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        pull_frame, text="Get data from irods to a local folder", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        pull_frame, text="PULL", command=GUIPULL
    ).grid(row=1, column=0, pady=10, sticky="n")

    ## CREATE A DIRECTORY IN IRODS
    imkdir_frame = customtkinter.CTkFrame(data, width=200, height=150)
    imkdir_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
    imkdir_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        imkdir_frame, text="Create a ifolder in irods", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        imkdir_frame, text="IMKDIR", command=GUIIMKDIR
    ).grid(row=1, column=0, pady=10, sticky="n")

    ## REMOVE DATA FROM IRODS
    irm_frame = customtkinter.CTkFrame(data, width=200, height=150)
    irm_frame.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
    irm_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        irm_frame, text="Remove data from irods", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        irm_frame, text="IRM", command=GUIIRM
    ).grid(row=1, column=0, pady=10, sticky="n")


    ##################################################################################################
    ### Work with metadata (add_meta, rm_meta, show_meta)
    ##################################################################################################
    metadata = customtkinter.CTkFrame(root)
    metadata.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    customtkinter.CTkLabel(
        metadata,
        text="Here you can work with metadata associated with your data on irods.",
        font=("", 15),
    ).grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    ## ADD METADATA
    addmeta_frame = customtkinter.CTkFrame(metadata, width=200, height=150)
    addmeta_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    addmeta_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        addmeta_frame, text="Add metadata to data already on irods", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(addmeta_frame, text="Add Meta", command=INIT_ADD_META).grid(row=1, column=0, pady=10, sticky="n")

    ## REMOVE METADATA
    rmmeta_frame = customtkinter.CTkFrame(metadata, width=200, height=150)
    rmmeta_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    rmmeta_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        rmmeta_frame, text="Remove metadata from data on irods", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(rmmeta_frame, text="Remove Meta", command=INIT_RM_META).grid(row=1, column=0, pady=10, sticky="n")

    ## SHOW METADATA
    showmeta_frame = customtkinter.CTkFrame(metadata, width=200, height=150)
    showmeta_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
    showmeta_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        showmeta_frame, text="Show metadata associated with data", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(showmeta_frame, text="Show Meta", command=INIT_SHOW_META).grid(row=1, column=0, pady=10, sticky="n")

    ## EDIT METADATA DICTIONARY
    edit_frame = customtkinter.CTkFrame(metadata, width=200, height=150)
    edit_frame.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
    edit_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        edit_frame, text="Edit metadata autocompletion dictionary", font=("", 15)
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(edit_frame, text="Edit Meta", command=INIT_EDIT).grid(row=1, column=0, pady=10, sticky="n")

    ##################################################################################################
    ### Configuration des lignes et colonnes principales pour permettre une adaptation
    ##################################################################################################
    root.grid_rowconfigure((0, 1), weight=1)
    root.grid_columnconfigure(0, weight=1)

    data.grid_rowconfigure(1, weight=1)
    data.grid_columnconfigure((0, 1, 2, 3), weight=1)

    metadata.grid_rowconfigure(1, weight=1)
    metadata.grid_columnconfigure((0, 1, 2, 3), weight=1)


    ##################################################################################################
    ### Get info on data (search_by_meta, search_by_name, idush, ichmod)
    ##################################################################################################
    infodata = customtkinter.CTkFrame(root)
    infodata.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    customtkinter.CTkLabel(
        infodata,
        text="Here you can search for data present on irods from their name or associated metadata, get the size that a folder occupies, or manage user permissions.",
        font=("", 15),
    ).grid(row=0, column=0, columnspan=5, padx=10, pady=10)

    ## SEARCH BY METADATA
    searchmeta_frame = customtkinter.CTkFrame(infodata, width=200, height=150)
    searchmeta_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    searchmeta_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        searchmeta_frame,
        text="Search data by metadata (SQL-like)",
        font=("", 15),
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        searchmeta_frame, text="Not Working Yet", command=None
    ).grid(row=1, column=0, pady=10, sticky="n")

    ## SEARCH BY NAME
    searchname_frame = customtkinter.CTkFrame(infodata, width=200, height=150)
    searchname_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    searchname_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        searchname_frame,
        text="Search data by name",
        font=("", 15),
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        searchname_frame, text="Search by Name", command=INIT_SEARCH_NAME
    ).grid(row=1, column=0, pady=10, sticky="n")

    ## GET SIZE OF IRODS FOLDER (IDUSH)
    idush_frame = customtkinter.CTkFrame(infodata, width=200, height=150)
    idush_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
    idush_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        idush_frame,
        text="Get folder size on irods (IDUSH)",
        font=("", 15),
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        idush_frame, text="IDUSH", command=INIT_IDUST
    ).grid(row=1, column=0, pady=10, sticky="n")

    # MANAGE USER PERMISSIONS (ICHMOD)
    ichmod_frame = customtkinter.CTkFrame(infodata, width=200, height=150)
    ichmod_frame.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
    ichmod_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        ichmod_frame,
        text="Manage user permissions (ICHMOD)",
        font=("", 15),
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        ichmod_frame, text="ICHMOD", command=INIT_ICHMOD
    ).grid(row=1, column=0, pady=10, sticky="n")

    ## UPDATE IRODS COLLECTION
    updpath_frame = customtkinter.CTkFrame(infodata, width=200, height=150)
    updpath_frame.grid(row=1, column=4, padx=10, pady=10, sticky="nsew")
    updpath_frame.grid_columnconfigure(0, weight=1)
    customtkinter.CTkLabel(
        updpath_frame,
        text="Update the irods collection, e.g.: someone gave you access to a folder that wasn't in your local list, or you worked on IRODS from another computer.",
        font=("", 15),
        wraplength=300,  # Limite la largeur du texte à 300 pixels
    ).grid(row=0, column=0, padx=10, pady=10, sticky="n")
    customtkinter.CTkButton(
        updpath_frame, text="Update", command=INIT_UPD_PATH
    ).grid(row=1, column=0, pady=10, sticky="n")


    ##################################################################################################
    ### Footer Buttons (Help, Theme, User Switch)
    ##################################################################################################
    footer_frame = customtkinter.CTkFrame(root)
    footer_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    # Configure columns to have equal weight for uniform distribution
    footer_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    customtkinter.CTkButton(
        footer_frame, text="Help", command=help_gui
    ).grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    customtkinter.CTkButton(
        footer_frame, text="Theme", command=theme_gui
    ).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    customtkinter.CTkButton(
        footer_frame, text="Switch/Add User", command=switch_add_user
    ).grid(row=0, column=2, padx=10, pady=10, sticky="ew")

    customtkinter.CTkButton(
        footer_frame, text="Quit", command=root.quit
    ).grid(row=0, column=3, padx=10, pady=10, sticky="ew")

    ##################################################################################################
    ### Configuration des lignes et colonnes principales
    ##################################################################################################
    root.grid_rowconfigure((0, 1, 2, 3), weight=1)
    root.grid_columnconfigure(0, weight=1)

    data.grid_rowconfigure(1, weight=1)
    data.grid_columnconfigure((0, 1, 2, 3), weight=1)

    metadata.grid_rowconfigure(1, weight=1)
    metadata.grid_columnconfigure((0, 1, 2, 3), weight=1)

    infodata.grid_rowconfigure(1, weight=1)
    infodata.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)


##########################################################################################################################################################################################################################################################################################
#### First time verification
##########################################################################################################################################################################################################################################################################################
    file_paths = [
        pickle_meta_dictionary_path,
        pickle_irods_path_path,
        pickle_additional_path_path,
        irods_key_path,
        irods_password_path,
        irods_info_files
    ]
    missing_files = [file for file in file_paths if not os.path.exists(file)]
    if missing_files:
        print("missing files")
        ## If no irods config info file create one
        if not os.path.isfile(irods_info_files):
            showwarning(
                title="missing irods config file",
                message=f"We need to configure irods, you will be asked to provide : \nhost\nport\nuser\nzone\nI'm creating it in {irods_info_files}",
            )
            create_and_wait_for_config()

        ## if no irods password
        if not os.path.isfile(irods_password_path):
            create_and_wait_for_password()

        ### IF no metadata dictionary found create it
        save_dict = os.path.expanduser(pickle_meta_dictionary_path)
        if not os.path.isfile(save_dict):
            showwarning(
                title="missing dictionary",
                message=f"You're missing the attribute/values dictionary need for metadata autocompletion \nI'm creating it in {save_dict}\n It can take some time if you have many files\nI'm doing it only the first time you use the program\nPLEASE WAIT FOR THE SECOND POP UP",
            )
            easicmd.building_attributes_dictionnary()
            # print("easicmd.building_attributes_dictionnary()")
            showwarning(
                title="missing dictionary", message=f"It's done\nthanks for waiting"
            )

        ### If no collection pickle create one
        pickles_path = os.path.expanduser(pickle_irods_path_path)
        if not os.path.isfile(pickles_path):
            showwarning(
                title="missing collection file",
                message=f"You're missing the irods collection file need for autocompletion \nI'm creating it in {pickles_path}\n It can take some time if you have many files.\nI'm doing it only the first time you use the program\nPLEASE WAIT FOR THE SECOND POP UP",
            )
            easicmd.get_irods_collection()
            showwarning(
                title="missing collection file", message=f"It's done\nthanks for waiting"
            )

        ### If no irods addin path file create one
        pickles_additionals_path = os.path.expanduser(pickle_additional_path_path)
        if not os.path.isfile(pickles_additionals_path):
            showwarning(
                title="missing irods addin path file",
                message=f"You're missing the irods addin path file need for autocompletion \nI'm creating it in {pickles_additionals_path}.\nI'm doing it only the first time you use the program\nPLEASE WAIT FOR THE SECOND POP UP",
            )
            easicmd.get_irods_addin_path()
            showwarning(
                title="missing irods addin path file",
                message=f"It's done\nthanks for waiting",
            )
        
        git_add_file()

##########################################################################################################################################################################################################################################################################################
#### 
##########################################################################################################################################################################################################################################################################################
    easicmd.get_irods_info()
    root.mainloop()

except TclError:
    print(
        "Oops!! It's seem you try to use the graphical interface on a computer without display if you're connected through SSH try re-connect using ssh -X"
    )
