#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import tkinter as tk
from tkinter import *
import os, sys, re, gzip 
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import easicmd as easicmd
from easicmd import *
import time
import ttkwidgets
from ttkwidgets.autocomplete import AutocompleteEntry
import subprocess



#ssh -X to activate Xwindow
# autocompletion sudo apt-get install python3-pil python3-pil.imagetk
######################################################################################################################################## 
### GUI called function's definition (function that will be "called" by the user)                  
########################################################################################################################################
    
def GUIPUSH() :
    INIT_PUSH()

def GUIPULL() :
    INIT_PULL()

def GUIIMKDIR():
    INIT_IMKDIR()

def GUIIRM():
    INIT_IRM()

def GUIADDMETA():
    INIT_ADD_META()
######################################################################################################################################## 
### GUI  tools function's definition (function that will only be use by other functions to avoid redundancy )                
########################################################################################################################################

def GUITEST():
    print("test")

def GUI_TYPE_OBJECT(otype):
    global type_object
    if otype == "file":
        type_object="-d"
    else :
        type_object="-C"
    return type_object
############
### PULL
###########
def GUI_GET_LOCAL_OBJECT(otype) :
    global local_object
    if otype == "file" :
        local_object=askopenfilename()
    else :
        local_object=askdirectory(title="Which folder (verify the path in selection before validate)")
    return local_object

def to_irods_and_beyond():
    irods_path=gui_list_of_icollection.get(gui_list_of_icollection.curselection())
    if type_object == "-d":
        cmd_push=f"iput -PKVf {local_object} {irods_path}"
    else :
        cmd_push=f"iput -rPKVf {local_object} {irods_path}"
    showinfo(title="Transfer's Begining",message="Click to run the transfer\nAnother pop-up will show when finish")
    subprocess.run(cmd_push.split())
    showinfo(title="End of Transfer",message="The data should be on irods now")

def WHERE_TO_IRODS():
    global gui_list_of_icollection
    win_where = Toplevel()
    win_where.title("WHERE TO SEND DATA")
    win_where.geometry('1080x500')
    easicmd.irods_collection()
    gui_list_of_icollection= Listbox(win_where)
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    select_button= Button(win_where,text="select",command=lambda:[to_irods_and_beyond(),win_where.destroy()]).pack(side='bottom')

def INIT_PUSH():

    win = Toplevel()
    win.title('warning')
    win.geometry('500x200')
    message = "The data is a FILE or a FOLDER ?"
    Label(win, text=message).pack()
    Button(win, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win.destroy(),GUI_GET_LOCAL_OBJECT("file"),WHERE_TO_IRODS()]).pack(side=LEFT)
    Button(win, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win.destroy(),GUI_GET_LOCAL_OBJECT("folder"),WHERE_TO_IRODS()]).pack(side=RIGHT)

#######
#PULL
#######
def DOWNLOAD(itype):
    if itype == "-C" :
        cmd_pull=f"iget -rPKV {irods_path} {local_path}".replace("//", "/")
    else :
        cmd_pull=f"iget -PKV {irods_path_file} {local_path}".replace("//", "/")
    showinfo(title="Transfer's Begining",message="Click to run the transfer\nAnother pop-up will show when finish")
    subprocess.run(cmd_pull.split())
    showinfo(title="End of Transfer",message="The data should be on your local now")

def WHERE_IN_LOCAL():
    global local_path
    local_path=askdirectory(title="where do you want to download it")

def GET_IRODS_PATH():
    global irods_path
    irods_path=gui_list_of_icollection.get(gui_list_of_icollection.curselection())
    #print(irods_path)

def GET_IRODS_FILE_PATH():
    global irods_path_file
    irods_path_file=f"{irods_path}/{gui_list_of_ifile.get(gui_list_of_ifile.curselection())}"
    #print(irods_path_file)

def GET_IRODS_FILE():
    global gui_list_of_ifile
    win_where = Toplevel()
    win_where.geometry('1080x500')
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile=Listbox(win_where)
    for i in easicmd.ifile :
        gui_list_of_ifile.insert(easicmd.ifile.index(i)+1,i)
    gui_list_of_ifile.pack(fill="both",expand="yes")
    select_button=Button(win_where,text="select",command=lambda:[GET_IRODS_FILE_PATH(),win_where.destroy(),WHERE_IN_LOCAL(),DOWNLOAD("-f")]).pack(side='bottom')

def PULL_FROM_IRODS(itype):
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    if itype == "-C" :
        win_where.title("WHICH FOLDER")
    else :
        win_where.title("FIRST SELECT THE FOLDER")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    
    if itype == "-C":
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(), WHERE_IN_LOCAL(),DOWNLOAD("-C") ]).pack(side='bottom')
    else :
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(), GET_IRODS_FILE()]).pack(side='bottom')


def INIT_PULL() :
    win_pull = Toplevel()
    win_pull.title('warning pull')
    win_pull.geometry('500x200')
    message = "The data is a FILE or a FOLDER ?"
    Label(win_pull, text=message).pack()
    Button(win_pull, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_pull.destroy(),PULL_FROM_IRODS("-f")]).pack(side=LEFT)
    Button(win_pull, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_pull.destroy(),PULL_FROM_IRODS("-C")]).pack(side=RIGHT)

############
###imkdir
############

def CMD_IMKDIR():
    cmd_imkdir=f"imkdir -p {irods_path}/{new_folder}"
    subprocess.run(cmd_imkdir.split())

def GET_NAME():
    global new_folder
    new_folder = entree.get()
    if " " in new_folder :
        showinfo(message="I HAVE REPLACE SPACE WITH UNDERSCORE !!!")
        new_folder=new_folder.replace(" ","_")
    CMD_IMKDIR()

def GIVE_NAME():
    global entree
    win_name=Toplevel()
    Label(win_name,text="name of the new folder :\n NO SPACE ONLY '_' ").pack()
    entree = Entry(win_name, width=50)
    entree.pack(padx=5, pady=5, side=LEFT)
    entree.focus_force()
    btnAffiche = Button(win_name,text="create", command=lambda:[GET_NAME(), win_name.destroy()]).pack(padx=5, pady=5)

def INIT_IMKDIR():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    win_where.title("WHERE DO YOU WANT TO CREATE YOUR FOLDER")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GIVE_NAME()]).pack(side='bottom')        

########
###irm
########
def DESTROY():
    if type_object == "-C":
        cmd_irm=f"irm -rf {irods_path}"
    else :
        cmd_irm=f"irm -f {irods_path_file}"
    subprocess.run(cmd_irm.split())
    showinfo(message="DATA HAS BEEN DESTROYED")

def GET_IRM_FILE_NAME():
    global gui_list_of_ifile
    win_where = Toplevel()
    win_where.geometry('1080x500')
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile=Listbox(win_where)
    for i in easicmd.ifile :
        gui_list_of_ifile.insert(easicmd.ifile.index(i)+1,i)
    gui_list_of_ifile.pack(fill="both",expand="yes")
    select_button=Button(win_where,text="select",command=lambda:[GET_IRODS_FILE_PATH(),win_where.destroy(),DESTROY()]).pack(side='bottom')

def IRM_GET_FOLDER():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else :
        win_where.title("FIRST CHOOSE THE FOLDER ?")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    if type_object == "-C":
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),DESTROY()]).pack(side='bottom')
    else :
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GET_IRM_FILE_NAME()]).pack(side='bottom')
    

def INIT_IRM():
    win_pull = Toplevel()
    win_pull.title('warning IRM')
    win_pull.geometry('500x200')
    message = "The data is a FILE or a FOLDER ?"
    Label(win_pull, text=message).pack()
    Button(win_pull, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_pull.destroy(),IRM_GET_FOLDER()]).pack(side=LEFT)
    Button(win_pull, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_pull.destroy(),IRM_GET_FOLDER()]).pack(side=RIGHT)
    
############
##ADD_META
############
def CLEAR_TEXT():
    attribut.delete(0,END)
    value.delete(0,END)
    units.delete(0,END)


def ADD_META_CMD():
    if type_object == "-C":
        cmd_add=f"imeta add {type_object} {irods_path} {attribut.get()} {value.get()} {units.get()}"
    else :
        cmd_add=f"imeta add {type_object} {irods_path_file} {attribut.get()} {value.get()} {units.get()}"
    subprocess.run(cmd_add.split())

    ##updating the autocompletion dictionary
    change=False
    if attribut.get() not in easicmd.dico_attribute:
        easicmd.dico_attribute[attribut.get()]=set()
        easicmd.dico_attribute[attribut.get()].add(value.get())
        change=True

    else:
        if value.get() not in easicmd.dico_attribute[attribut.get()]:
            easicmd.dico_attribute[attribut.get()].add(value.get())
            change=True

    if change == True :
        file_name=os.path.expanduser("~/.irods_metadata_local_save.pkl")
        with open(file_name,"wb") as f :
            pickle.dump(easicmd.dico_attribute, f)
        print(f"Dictionary have been update in {file_name}")

# def GIVE_META():
#     global attribut
#     global value 
#     global units 
#     win_name_addmeta= Toplevel()
#     win_name_addmeta.title("ADD METADATA (* is mandatory)")
#     Label(win_name_addmeta,text="attribut* : ").grid(row=0)
#     Label(win_name_addmeta,text="value* : ").grid(row=1)
#     Label(win_name_addmeta,text="units : ").grid(row=2)
#     attribut = Entry(win_name_addmeta, width=20)
#     attribut.grid(row=0, column=1)
#     value = Entry(win_name_addmeta, width=20)
#     value.grid(row=1, column=1)
#     units = Entry(win_name_addmeta, width=20)
#     units.grid(row=2, column=1)
#     validate_button = Button(win_name_addmeta,text="validate",command=lambda:[ADD_META_CMD(),CLEAR_TEXT()])
#     validate_button.grid(row=0, column=2)
#     exit_button = Button(win_name_addmeta,text="exit",command=lambda:[win_name_addmeta.destroy()])
#     exit_button.grid(row=3, column=2)

def GIVE_META():
    global attribut
    global value 
    global units
    easicmd.read_attributes_dictionnary()
    list_value=[]
    list_attr=[]
    for i in easicmd.dico_attribute.values():
        for j in i : ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for attr in easicmd.dico_attribute.keys(): 
        list_attr.append(attr)
    list_attr.sort(key=str.lower)
    list_value.sort(key=str.lower) 
    win_name_addmeta= Toplevel()
    win_name_addmeta.title("ADD METADATA (* is mandatory)")
    Label(win_name_addmeta,text="attribut* : ").grid(row=0)
    Label(win_name_addmeta,text="value* : ").grid(row=1)
    Label(win_name_addmeta,text="units : ").grid(row=2)
    attribut = AutocompleteEntry(win_name_addmeta, width=20,completevalues=list_attr)
    attribut.grid(row=0, column=1)
    value = AutocompleteEntry(win_name_addmeta, width=20,completevalues=list_value)
    value.grid(row=1, column=1)
    units = Entry(win_name_addmeta, width=20)
    units.grid(row=2, column=1)
    validate_button = Button(win_name_addmeta,text="validate",command=lambda:[ADD_META_CMD(),CLEAR_TEXT(),win_name_addmeta.destroy(),GIVE_META()])
    validate_button.grid(row=0, column=2)
    exit_button = Button(win_name_addmeta,text="exit",command=lambda:[win_name_addmeta.destroy()])
    exit_button.grid(row=3, column=2)

def GET_ADDMETA_FILE_NAME():
    global gui_list_of_ifile
    win_where = Toplevel()
    win_where.geometry('1080x500')
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile=Listbox(win_where)
    for i in easicmd.ifile :
        gui_list_of_ifile.insert(easicmd.ifile.index(i)+1,i)
    gui_list_of_ifile.pack(fill="both",expand="yes")
    select_button=Button(win_where,text="select",command=lambda:[GET_IRODS_FILE_PATH(),win_where.destroy(),GIVE_META()]).pack(side='bottom')
        
def ADDMETA_GET_IRODS_PATH():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else :
        win_where.title("FIRST CHOOSE THE FOLDER ?")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    if type_object == "-C":
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GIVE_META()]).pack(side='bottom')
    else :
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GET_ADDMETA_FILE_NAME()]).pack(side='bottom')    

def INIT_ADD_META():
    win_addmeta = Toplevel()
    win_addmeta.title('warning ADD METADATA')
    win_addmeta.geometry('500x200')
    message = "The data is a FILE or a FOLDER ?"
    Label(win_addmeta, text=message).pack()
    Button(win_addmeta, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_addmeta.destroy(),ADDMETA_GET_IRODS_PATH()]).pack(side=LEFT)
    Button(win_addmeta, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_addmeta.destroy(),ADDMETA_GET_IRODS_PATH()]).pack(side=RIGHT)


############
### rm_meta
############
def RM_META_CMD():
    att=str(attribut.get()).replace("*", "%")
    val=str(value.get()).replace("*", "%")
    if type_object == "-C":
        cmd_rm=f"imeta rmw {type_object} {irods_path} {att} {val} %"
    else :
        cmd_rm=f"imeta rmw {type_object} {irods_path_file} {att} {val} %"
    subprocess.run(cmd_rm.split())

def GET_RM_ATTR():
    global attribut
    global value 
    global units
    easicmd.read_attributes_dictionnary()
    list_value=[]
    list_attr=[]
    for i in easicmd.dico_attribute.values():
        for j in i : ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for attr in easicmd.dico_attribute.keys(): 
        list_attr.append(attr)
    list_attr.sort(key=str.lower)
    list_value.sort(key=str.lower) 
    win_name_addmeta= Toplevel()
    win_name_addmeta.title("REMOVE METADATA (* for all)")
    Label(win_name_addmeta,text="attribut : ").grid(row=0)
    Label(win_name_addmeta,text="value : ").grid(row=1)
    attribut = AutocompleteEntry(win_name_addmeta, width=20,completevalues=list_attr)
    attribut.grid(row=0, column=1)
    value = AutocompleteEntry(win_name_addmeta, width=20,completevalues=list_value)
    value.grid(row=1, column=1)
    units = Entry(win_name_addmeta, width=20)
    validate_button = Button(win_name_addmeta,text="validate",command=lambda:[RM_META_CMD(),CLEAR_TEXT()])
    validate_button.grid(row=0, column=2)
    exit_button = Button(win_name_addmeta,text="exit",command=lambda:[win_name_addmeta.destroy()])
    exit_button.grid(row=3, column=2)  

def GET_RMMETA_FILE_NAME():
    global gui_list_of_ifile
    win_where = Toplevel()
    win_where.geometry('1080x500')
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile=Listbox(win_where)
    for i in easicmd.ifile :
        gui_list_of_ifile.insert(easicmd.ifile.index(i)+1,i)
    gui_list_of_ifile.pack(fill="both",expand="yes")
    select_button=Button(win_where,text="select",command=lambda:[GET_IRODS_FILE_PATH(),win_where.destroy(),GET_RM_ATTR()]).pack(side='bottom')    

def RMMETA_GET_IRODS_PATH():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else :
        win_where.title("FIRST CHOOSE THE FOLDER ?")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    if type_object == "-C":
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GET_RM_ATTR()]).pack(side='bottom')
    else :
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GET_RMMETA_FILE_NAME()]).pack(side='bottom')  

def INIT_RM_META():
    win_rmmeta= Toplevel()
    win_rmmeta.title('warning ADD METADATA')
    win_rmmeta.geometry('500x200')
    message = "The data you want to remove metadata is a FILE or a FOLDER ?"
    Label(win_rmmeta, text=message).pack()
    Button(win_rmmeta, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_rmmeta.destroy(),RMMETA_GET_IRODS_PATH()]).pack(side=LEFT)
    Button(win_rmmeta, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_rmmeta.destroy(),RMMETA_GET_IRODS_PATH()]).pack(side=RIGHT)    

##################
##SHOW META
##################
def PRINT_META():
    win_meta= Toplevel()
    t= Text(win_meta, height = 25, width = 52)
    Label(win_meta,text="Your meta data :").pack()
    t.insert(tk.END, meta_to_show)
    t.pack()
    button_close= Button(win_meta, text="close", command=win_meta.destroy)
    button_close.pack(side=BOTTOM)

def GUI_SHOW_META():
    global meta_to_show
    if type_object == "-C":
        cmd=f"imeta ls {type_object} {irods_path}"
    else :
        cmd=f"imeta ls {type_object} {irods_path_file}"
    meta_to_show=subprocess.check_output(cmd, shell=True,text=True )
    PRINT_META()


def GET_SHOW_META_FILE_NAME():
    global gui_list_of_ifile
    win_where = Toplevel()
    win_where.geometry('1080x500')
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile=Listbox(win_where)
    for i in easicmd.ifile :
        gui_list_of_ifile.insert(easicmd.ifile.index(i)+1,i)
    gui_list_of_ifile.pack(fill="both",expand="yes")
    select_button=Button(win_where,text="select",command=lambda:[GET_IRODS_FILE_PATH(),win_where.destroy(),GUI_SHOW_META()]).pack(side='bottom') 

def SHOWMETA_GET_IRODS_PATH():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else :
        win_where.title("FIRST CHOOSE THE FOLDER ?")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    if type_object == "-C":
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GUI_SHOW_META()]).pack(side='bottom')
    else :
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GET_SHOW_META_FILE_NAME()]).pack(side='bottom')
        
def INIT_SHOW_META():
    win_showmeta= Toplevel()
    win_showmeta.title('warning ADD METADATA')
    win_showmeta.geometry('500x200')
    message = "The data you want to show metadata is a FILE or a FOLDER ?"
    Label(win_showmeta, text=message).pack()
    Button(win_showmeta, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_showmeta.destroy(),SHOWMETA_GET_IRODS_PATH()]).pack(side=LEFT)
    Button(win_showmeta, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_showmeta.destroy(),SHOWMETA_GET_IRODS_PATH()]).pack(side=RIGHT)

####################
##search by meta
####################

def CLEAR_SEARCH_TEXT():
    attribut.delete(0,END)
    value.delete(0,END)
    liaison.delete(0,END)
    operator.delete(0,END)


def SEARCH_GET_CMD():
    global attribut
    global value 
    global liaison
    global operator
    global search_meta_cmd

    search_meta_cmd=f"imeta qu {type_object}"
    list_operation=["=","like","\'>\'","\'<\'"]
    list_liaison=["","and",'or']

    easicmd.read_attributes_dictionnary()
    list_value=[]
    list_attr=[]
    
    for i in easicmd.dico_attribute.values():
        for j in i : ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for attr in easicmd.dico_attribute.keys(): 
        list_attr.append(attr)
    list_attr.sort(key=str.lower)
    list_value.sort(key=str.lower) 
    
    win_searchcmd= Toplevel()
    win_searchcmd.title("SEARCH FOR (* is mandatory)")
    Label(win_searchcmd,text="attribut* : ").grid(row=0)
    Label(win_searchcmd,text="operator* (=, like, >, <,) : ").grid(row=1)
    Label(win_searchcmd,text="value* : ").grid(row=2)
    Label(win_searchcmd,text="liaison (and/or): ").grid(row=3)

    attribut = AutocompleteEntry(win_searchcmd, width=20,completevalues=list_attr)
    attribut.grid(row=0, column=1)
    operator= AutocompleteEntry(win_searchcmd, width=20,completevalues=list_operation)
    operator.grid(row=1, column=1)
    value = AutocompleteEntry(win_searchcmd, width=20,completevalues=list_value)
    value.grid(row=2, column=1)
    liaison=AutocompleteEntry(win_searchcmd, width=20,completevalues=list_liaison)
    liaison.grid(row=3,column=1)
    
    add_button = Button(win_searchcmd,text="add",command=lambda:[BUILD_SEARCH_CMD(),CLEAR_SEARCH_TEXT()])
    add_button.grid(row=0,column=2)
    validate_button = Button(win_searchcmd,text="validate",command=lambda:[EXEC_SEARCH_CMD(),win_searchcmd.destroy()])
    validate_button.grid(row=1, column=2)
    exit_button = Button(win_searchcmd,text="exit",command=lambda:[win_searchcmd.destroy()])
    exit_button.grid(row=3, column=2) 


def EXEC_SEARCH_CMD():
    global searched_data
    search_meta_cmd_final=f"{search_meta_cmd} {attribut.get()} {operator.get()} {value.get()} {liaison.get()}"
    try :
        searched_data=subprocess.check_output(search_meta_cmd_final, shell=True,text=True )
    except CalledProcessError :
        searched_data=f"NO DATA ASSOCIATED WITH THE REQUEST \n\n{search_meta_cmd_final}"
    PRINT_SEARCH()

def PRINT_SEARCH():
    win_meta= Toplevel()
    t= Text(win_meta, height = 25, width = 52)
    Label(win_meta,text="Your searched data are :").pack()
    t.insert(tk.END, searched_data)
    t.pack()
    button_close= Button(win_meta, text="close", command=win_meta.destroy)
    button_close.pack(side=BOTTOM)

def BUILD_SEARCH_CMD():
    global search_meta_cmd
    new_cmd=f"{search_meta_cmd} {attribut.get()} {operator.get()} {value.get()} {liaison.get()}"
    search_meta_cmd = new_cmd


def INIT_SEARCH_META():
    win_searchmeta= Toplevel()
    win_searchmeta.title('warning SEARCH BY METADATA')
    win_searchmeta.geometry('500x200')
    message = "The data you're searching is a FILE or a FOLDER ?"
    Label(win_searchmeta, text=message).pack()
    Button(win_searchmeta, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_searchmeta.destroy(),SEARCH_GET_CMD()]).pack(side=LEFT)
    Button(win_searchmeta, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_searchmeta.destroy(),SEARCH_GET_CMD()]).pack(side=RIGHT)

########################
# SEARCH BY NAME
########################
def SEARCH_FILE_NAME():
    global name
    win_namesearch = Toplevel()
    win_namesearch.title('warning SEARCH BY NAME')
    Label(win_namesearch,text="your query (you can use *): ").pack()
    name=Entry(win_namesearch, width=50)
    name.pack(padx=5, pady=5, side=LEFT)
    Btt_search= Button(win_namesearch,text="search",command=lambda:[FILE_NAME_CMD(),win_namesearch.destroy()])
    Btt_search.pack(side=BOTTOM)

def FILE_NAME_CMD():
    global result
    search=name.get()
    search=str(search).replace("*", "%")
    cmd_search=f"ilocate {search}"
    try :
        result=subprocess.check_output(cmd_search, shell=True,text=True )
    except subprocess.CalledProcessError :
        result=f"NO DATA ASSOCIATED WITH THE REQUEST \n\n{cmd_search}"
    PRINT_NAME()
    
def PRINT_NAME():
    win_printname= Toplevel()
    t= Text(win_printname, height = 50, width = 150)
    Label(win_printname,text="Your searched data are :").pack()
    t.insert(tk.END, result)
    t.pack()
    button_close= Button(win_printname, text="close", command=win_printname.destroy)
    button_close.pack(side=BOTTOM)


def FOLDER_NAME_CMD():
    global result
    result=""
    easicmd.irods_collection()
    search=f"*/*{name.get()}"
    for i in easicmd.list_of_icollection:
        if fnmatch.fnmatch(i, search) :
            result=f"{result}\n{i}"
    PRINT_NAME()

def SEARCH_FOLDER_NAME():
    global name
    win_namesearch = Toplevel()
    win_namesearch.title('warning SEARCH BY NAME')
    Label(win_namesearch,text="your query (you can use *): ").pack()
    name=Entry(win_namesearch, width=50)
    name.pack(padx=5, pady=5, side=LEFT)
    Btt_search= Button(win_namesearch,text="search",command=lambda:[FOLDER_NAME_CMD(),win_namesearch.destroy()])
    Btt_search.pack(side=BOTTOM)


def INIT_SEARCH_NAME():
    win_searchname= Toplevel()
    win_searchname.title('warning SEARCH BY NAME')
    win_searchname.geometry('500x200')
    message = "The data you're searching is a FILE or a FOLDER ?"
    Label(win_searchname, text=message).pack()
    Button(win_searchname, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_searchname.destroy(),SEARCH_FILE_NAME()]).pack(side=LEFT)
    Button(win_searchname, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_searchname.destroy(),SEARCH_FOLDER_NAME()]).pack(side=RIGHT)    

###########
##idush
###########
def GUI_IDUSH():
    global result_size
    cmd_ils=f"ils -rl {irods_path}"
    ils=(subprocess.run(cmd_ils.split(),capture_output=True).stdout).decode("utf-8")
    total_bits=0
    for line in ils.split("\n"):
        if "/" not in line and line !="":
            bits=int(line.split()[3])
            total_bits += bits
    result_size=easicmd.sizeof_fmt(total_bits)
    PRINT_IDUST()

def PRINT_IDUST():
    win_meta= Toplevel()
    t= Text(win_meta, height = 25, width = 52)
    Label(win_meta,text=f"The size of your folder is : {result_size}").pack()
    button_close= Button(win_meta, text="close", command=win_meta.destroy)
    button_close.pack(side=BOTTOM)

def INIT_IDUST():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    win_where.title("WHICH FOLDER ?")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GUI_IDUSH()]).pack(side='bottom')


#############
###ICHMOD
#############
def CLEAN_ICHMOD():
    TO.delete(0,END)
    right.delete(0,END)

def ICHMOD_CMD():
    r=right.get()
    if r == "remove/null" :
        r="null"
    t=TO.get()

    if type_object == "-C":
        cmd_ichmod=f"ichmod -r {r} {t} {irods_path}"
        path=irods_path
    else :
        cmd_ichmod=f"ichmod {r} {t} {irods_path_file}"
        path=irods_path_file
    subprocess.run(cmd_ichmod.split())
    showinfo(message=f"You just give {r} acces for {path} to {t}")

def ICHMOD_BUILD_CMD(type):
    global TO
    global right
    list_right=["read","write","own","remove/null"]
    if type == "group" :
        easicmd.get_group()
        list_to_show=easicmd.list_group
    else :
        easicmd.get_user()
        list_to_show=easicmd.list_user

    win_cmdichmod=Toplevel()
    win_cmdichmod.title("warning ICHMOD")

    Label(win_cmdichmod,text="give : ").grid(row=0)
    Label(win_cmdichmod,text="to : ").grid(row=1)
    right=AutocompleteEntry(win_cmdichmod, width=20,completevalues=list_right)
    right.grid(column=1,row=0)
    TO=AutocompleteEntry(win_cmdichmod, width=20,completevalues=list_to_show)
    TO.grid(column=1,row=1)

    BTT_cmd=Button(win_cmdichmod,text="select",command=lambda:[ICHMOD_CMD(),CLEAN_ICHMOD()])
    BTT_cmd.grid(column=2,row=0)
    BTT_exit=Button(win_cmdichmod,text="exit",command=lambda:[win_cmdichmod.destroy()])
    BTT_exit.grid(column=2,row=2)

def USER_OR_GROUP():
    win_ichmod= Toplevel()
    win_ichmod.title('warning ICHMOD')
    win_ichmod.geometry('500x200')
    message = "Share your data with a GROUP or a USER ?"
    Label(win_ichmod, text=message).pack()
    Button(win_ichmod, text='USER', command=lambda:[ICHMOD_BUILD_CMD("user"),win_ichmod.destroy(),]).pack(side=LEFT)
    Button(win_ichmod, text='GROUP', command=lambda:[ICHMOD_BUILD_CMD("group"),win_ichmod.destroy()]).pack(side=RIGHT)

def GET_ICHMOD_FILE_NAME():
    global gui_list_of_ifile
    win_where = Toplevel()
    win_where.geometry('1080x500')
    win_where.title("SELECT THE FILE")
    easicmd.list_ifile(irods_path)
    gui_list_of_ifile=Listbox(win_where)
    for i in easicmd.ifile :
        gui_list_of_ifile.insert(easicmd.ifile.index(i)+1,i)
    gui_list_of_ifile.pack(fill="both",expand="yes")
    select_button=Button(win_where,text="select",command=lambda:[GET_IRODS_FILE_PATH(),win_where.destroy(),USER_OR_GROUP()]).pack(side='bottom')     

def ICHMOD_IRODS_PATH():
    easicmd.irods_collection()
    global gui_list_of_icollection
    win_where = Toplevel()
    if type_object == "-C":
        win_where.title("WHICH FOLDER ?")
    else :
        win_where.title("FIRST CHOOSE THE FOLDER ?")
    win_where.geometry('1080x500')
    gui_list_of_icollection= Listbox(win_where)    
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    if type_object == "-C":
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),USER_OR_GROUP()]).pack(side='bottom')
    else :
        select_button= Button(win_where,text="select",command=lambda:[GET_IRODS_PATH(),win_where.destroy(),GET_ICHMOD_FILE_NAME()]).pack(side='bottom')

def INIT_ICHMOD():
    win_ichmod= Toplevel()
    win_ichmod.title('warning ICHMOD')
    win_ichmod.geometry('500x200')
    message = "The data you're want to share is a FILE or a FOLDER ?"
    Label(win_ichmod, text=message).pack()
    Button(win_ichmod, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_ichmod.destroy(),ICHMOD_IRODS_PATH()]).pack(side=LEFT)
    Button(win_ichmod, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_ichmod.destroy(),ICHMOD_IRODS_PATH()]).pack(side=RIGHT)


######################################################################################################################################## 
### creation of the main window (putting the form)                  
########################################################################################################################################

class FullScreenApp(object):
    ##This creates a fullscreen window. Pressing Escape resizes the window to '200x200+0+0' by default. If you move or resize the window, Escape toggles between the current geometry and the previous geometry.
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        #print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom        

class Test(Text):  ###allow control c/v/x in tkinter 
    def __init__(self, master, **kw):
        Text.__init__(self, master, **kw)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-v>', self.paste)
        
    def copy(self, event=None):
        self.clipboard_clear()
        text = self.get("sel.first", "sel.last")
        self.clipboard_append(text)
    
    def cut(self, event):
        self.copy()
        self.delete("sel.first", "sel.last")

    def paste(self, event):
        text = self.selection_get(selection='CLIPBOARD')
        self.insert('insert', text)

try :
    root = tk.Tk()
    app=FullScreenApp(root)
    root.title("easicmd : easy irods commands graphical edition")

    ##################################################################################################
    ### Work with data (push,pull,imkdir,irm)
    ##################################################################################################
    data = LabelFrame(root, text="Work with DATA", padx=30, pady=30)
    data.pack(fill="both", expand="yes")
    Label(data, text="Here you can work with your data like send it to irods, recover it from irods, create ifolders or delete data on irods").pack()

    ##PUSH DATA TO IRODS
    push_frame= LabelFrame(data, text="PUSH",padx=30, pady=30, relief=RAISED)
    push_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(push_frame, text="Send local data to irods").pack()
    push_bouton=Button(push_frame, text="PUSH", command=GUIPUSH).pack(side=BOTTOM)

    ## PULL DATA TO IRODS
    pull_frame= LabelFrame(data, text="PULL",padx=30, pady=30, relief=RAISED)
    pull_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(pull_frame, text="Get data from irods to a local folder").pack()
    pull_bouton=Button(pull_frame, text="PULL", command=GUIPULL).pack(side=BOTTOM)

    ## CREATE A DIRECTORY IN IRODS
    imkdir_frame= LabelFrame(data, text="IMKDIR",padx=30, pady=30, relief=RAISED)
    imkdir_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(imkdir_frame, text="Create a ifolder in irods").pack()
    imkdir_bouton=Button(imkdir_frame, text="IMKDIR", command=GUIIMKDIR).pack(side=BOTTOM)

    ## REMOVE A DATA FROM IRODS
    irm_frame= LabelFrame(data, text="IRM",padx=30, pady=30, relief=RAISED)
    irm_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(irm_frame, text="Remove data frome Irods").pack()
    irm_bouton=Button(irm_frame, text="IRM", command=GUIIRM).pack(side=BOTTOM)

    ##################################################################################################
    ### Work with metadata (add_meta,rm_meta,show_meta)
    ##################################################################################################
    metadata = LabelFrame(root, text="Work with METADATA", padx=30, pady=30)
    metadata.pack(fill="both", expand="yes")
    Label(metadata, text="Here you can work with the metadata associated with your data on irods such as add, delete,see metadate or edit the metadata dictionary (soon)").pack()

    ## ADD METADATA TO DATA ALREADY ON IRODS
    addmeta_frame= LabelFrame(metadata, text="add metadata",padx=30, pady=30, relief=RAISED)
    addmeta_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(addmeta_frame, text="Add metadata to a data (file or folder) already present on irods").pack()
    addmeta_bouton=Button(addmeta_frame, text="addmeta", command=INIT_ADD_META).pack(side=BOTTOM)

    ## REMOVE METADATA TO DATA ALREADY ON IRODS
    rmmeta_frame= LabelFrame(metadata, text="remove metadata",padx=30, pady=30, relief=RAISED)
    rmmeta_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(rmmeta_frame, text="Remove metadata to a data (file or folder) already present on irods").pack()
    rmmeta_bouton=Button(rmmeta_frame, text="remove meta", command=INIT_RM_META).pack(side=BOTTOM)

    ## SHOW METADATA ASSOCIATE WITH A DATA
    showmeta_frame= LabelFrame(metadata, text="show metadata",padx=30, pady=30, relief=RAISED)
    showmeta_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(showmeta_frame, text="Show metadata to a data (file or folder) already present on irods").pack()
    showmeta_bouton=Button(showmeta_frame, text="show meta", command=INIT_SHOW_META).pack(side=BOTTOM)

    ##################################################################################################
    ### Get info on data (serach_by_meta,search_by_name,idush,ichmod)
    ##################################################################################################
    infodata = LabelFrame(root, text="INFO on data", padx=30, pady=30)
    infodata.pack(fill="both", expand="yes")
    Label(infodata, text="Here you can search for data present on irods from their name or associated metadata, get the size that a folder occupied on irods or allow to give/remove rights to other users on your data on irods").pack()

    ## SEARCH A DATA BY USING METADATA
    searchmeta_frame=LabelFrame(infodata, text="searchmeta",padx=30, pady=30, relief=RAISED)
    searchmeta_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(searchmeta_frame, text="Search for data from the associated metadata (SQL-like)").pack()
    searchmeta_bouton=Button(searchmeta_frame, text="search_by_meta", command=INIT_SEARCH_META).pack(side=BOTTOM)

    ## SEARCH A DATA BY IT'S NAME
    searchname_frame=LabelFrame(infodata, text="searchname",padx=30, pady=30, relief=RAISED)
    searchname_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(searchname_frame, text="Search for data based on their name").pack()
    searchname_bouton=Button(searchname_frame, text="search_by_name", command=INIT_SEARCH_NAME).pack(side=BOTTOM)

    ## GET THE SIZE OF A IFOLDER
    idush_frame=LabelFrame(infodata, text="idush",padx=30, pady=30, relief=RAISED)
    idush_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(idush_frame, text="Get the size that a folder occupied on irods\n(AN IRODS EQUIVALENT TO du -sh)").pack()
    idush_bouton=Button(idush_frame, text="idush", command=INIT_IDUST).pack(side=BOTTOM)

    ## GIVE ACCES TO THE DATA TO OTHER USER 
    ichmod_frame=LabelFrame(infodata, text="ichmod",padx=30, pady=30, relief=RAISED)
    ichmod_frame.pack(fill="both", expand="yes", side=LEFT)
    Label(ichmod_frame, text="With this command you can give \n(or remove with null) write/read/owner right\n to another iRODS user or group").pack()
    ichmod_bouton=Button(ichmod_frame, text="ichmod", command=INIT_ICHMOD).pack(side=BOTTOM)

    ## EXIT
    quit_bouton=Button(root, text="quit", command=root.quit).pack(side=BOTTOM)

    save_dict=os.path.expanduser("~/.irods_metadata_local_save.pkl")
    if not os.path.isfile(save_dict) :
        showwarning(title="missing dictionary",message=f"You're missing the attribute/values dictionary need for metadata autocompletion \nI'm creating it in {save_dict}\n It can take some time if you have many files")
        easicmd.building_attributes_dictionnary()
        #print("easicmd.building_attributes_dictionnary()")
        showwarning(title="missing dictionary",message=f"It's done\nthanks for the wait")



    root.mainloop()

except TclError:
    print("Oops!! It's seem you try to use the graphical interface on a computer without display if you're connected through SSH try re-connect using ssh -X")