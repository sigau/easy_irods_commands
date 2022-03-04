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
        type_object="-f"
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
    print(local_object)


def to_irods_and_beyond():
    irods_path=gui_list_of_icollection.get(gui_list_of_icollection.curselection())
    if type_object == "-f":
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
    #print(easicmd.list_of_icollection)
    gui_list_of_icollection= Listbox(win_where)
    for i in easicmd.list_of_icollection:
        gui_list_of_icollection.insert(easicmd.list_of_icollection.index(i)+1,i)
    gui_list_of_icollection.pack(fill="both",expand="yes")
    select_button= Button(win_where,text="select",command=lambda:[to_irods_and_beyond(),win_where.destroy()]).pack(side='bottom')

def INIT_PUSH():

    win = Toplevel()
    win.title('warning')
    win.geometry('250x200')
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
    win_pull.geometry('250x200')
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
    win_pull.geometry('250x200')
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
    win_addmeta.geometry('250x200')
    message = "The data is a FILE or a FOLDER ?"
    Label(win_addmeta, text=message).pack()
    Button(win_addmeta, text='FILE', command=lambda:[GUI_TYPE_OBJECT("file"),win_addmeta.destroy(),ADDMETA_GET_IRODS_PATH()]).pack(side=LEFT)
    Button(win_addmeta, text='FOLDER', command=lambda:[GUI_TYPE_OBJECT("folder"),win_addmeta.destroy(),ADDMETA_GET_IRODS_PATH()]).pack(side=RIGHT)

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

root = tk.Tk()
app=FullScreenApp(root)
root.title("easicmd : easy irods commands graphical edition")

##################################################################################################
### Work with data (push,pull,imkdir,irm)
##################################################################################################
data = LabelFrame(root, text="Work with DATA", padx=30, pady=30)
data.pack(fill="both", expand="yes")
Label(data, text="A l'intérieure de la frame DATA").pack()

##PUSH DATA TO IRODS
push_frame= LabelFrame(data, text="PUSH",padx=30, pady=30, relief=RAISED)
push_frame.pack(fill="both", expand="yes", side=LEFT)
Label(push_frame, text="A l'intérieure de la frame PUSH").pack()
push_bouton=Button(push_frame, text="PUSH", command=GUIPUSH).pack(side=BOTTOM)

## PULL DATA TO IRODS
pull_frame= LabelFrame(data, text="PULL",padx=30, pady=30, relief=RAISED)
pull_frame.pack(fill="both", expand="yes", side=LEFT)
Label(pull_frame, text="A l'intérieure de la frame PULL").pack()
pull_bouton=Button(pull_frame, text="PULL", command=GUIPULL).pack(side=BOTTOM)

## CREATE A DIRECTORY IN IRODS
imkdir_frame= LabelFrame(data, text="IMKDIR",padx=30, pady=30, relief=RAISED)
imkdir_frame.pack(fill="both", expand="yes", side=LEFT)
Label(imkdir_frame, text="A l'intérieure de la frame IMKDIR").pack()
imkdir_bouton=Button(imkdir_frame, text="IMKDIR", command=GUIIMKDIR).pack(side=BOTTOM)

## REMOVE A DATA FROM IRODS
irm_frame= LabelFrame(data, text="IRM",padx=30, pady=30, relief=RAISED)
irm_frame.pack(fill="both", expand="yes", side=LEFT)
Label(irm_frame, text="A l'intérieure de la frame IRM").pack()
irm_bouton=Button(irm_frame, text="IRM", command=GUIIRM).pack(side=BOTTOM)

##################################################################################################
### Work with metadata (add_meta,rm_meta,show_meta)
##################################################################################################
metadata = LabelFrame(root, text="Work with METADATA", padx=30, pady=30)
metadata.pack(fill="both", expand="yes")
Label(metadata, text="A l'intérieure de la frame METADATA").pack()

## ADD METADATA TO DATA ALREADY ON IRODS
addmeta_frame= LabelFrame(metadata, text="add metadata",padx=30, pady=30, relief=RAISED)
addmeta_frame.pack(fill="both", expand="yes", side=LEFT)
Label(addmeta_frame, text="A l'intérieure de la frame addmeta").pack()
addmeta_bouton=Button(addmeta_frame, text="addmeta", command=INIT_ADD_META).pack(side=BOTTOM)

## REMOVE METADATA TO DATA ALREADY ON IRODS
rmmeta_frame= LabelFrame(metadata, text="remove metadata",padx=30, pady=30, relief=RAISED)
rmmeta_frame.pack(fill="both", expand="yes", side=LEFT)
Label(rmmeta_frame, text="A l'intérieure de la frame rmmeta").pack()
rmmeta_bouton=Button(rmmeta_frame, text="remove meta", command=GUITEST).pack(side=BOTTOM)

## SHOW METADATA ASSOCIATE WITH A DATA
showmeta_frame= LabelFrame(metadata, text="show metadata",padx=30, pady=30, relief=RAISED)
showmeta_frame.pack(fill="both", expand="yes", side=LEFT)
Label(showmeta_frame, text="A l'intérieure de la frame showmeta").pack()
showmeta_bouton=Button(showmeta_frame, text="show meta", command=GUITEST).pack(side=BOTTOM)

##################################################################################################
### Get info on data (serach_by_meta,search_by_name,idush,ichmod)
##################################################################################################
infodata = LabelFrame(root, text="INFO on data", padx=30, pady=30)
infodata.pack(fill="both", expand="yes")
Label(infodata, text="A l'intérieure de la frame INFODATA").pack()

## SEARCH A DATA BY USING METADATA
searchmeta_frame=LabelFrame(infodata, text="searchmeta",padx=30, pady=30, relief=RAISED)
searchmeta_frame.pack(fill="both", expand="yes", side=LEFT)
Label(searchmeta_frame, text="A l'intérieure de la frame searchmeta").pack()
searchmeta_bouton=Button(searchmeta_frame, text="search_by_meta", command=GUITEST).pack(side=BOTTOM)

## SEARCH A DATA BY IT'S NAME
searchname_frame=LabelFrame(infodata, text="searchname",padx=30, pady=30, relief=RAISED)
searchname_frame.pack(fill="both", expand="yes", side=LEFT)
Label(searchname_frame, text="A l'intérieure de la frame searchname").pack()
searchname_bouton=Button(searchname_frame, text="search_by_name", command=GUITEST).pack(side=BOTTOM)

## GET THE SIZE OF A IFOLDER
idush_frame=LabelFrame(infodata, text="idush",padx=30, pady=30, relief=RAISED)
idush_frame.pack(fill="both", expand="yes", side=LEFT)
Label(idush_frame, text="A l'intérieure de la frame idush").pack()
idush_bouton=Button(idush_frame, text="search_by_name", command=GUITEST).pack(side=BOTTOM)

## GIVE ACCES TO THE DATA TO OTHER USER 
ichmod_frame=LabelFrame(infodata, text="ichmod",padx=30, pady=30, relief=RAISED)
ichmod_frame.pack(fill="both", expand="yes", side=LEFT)
Label(ichmod_frame, text="A l'intérieure de la frame ichmod").pack()
ichmod_bouton=Button(ichmod_frame, text="search_by_name", command=GUITEST).pack(side=BOTTOM)

## EXIT
quit_bouton=Button(root, text="quit", command=root.quit).pack(side=BOTTOM)

save_dict=os.path.expanduser("~/.irods_metadata_local_save.pkl")
if not os.path.isfile(save_dict) :
    showwarning(title="missing dictionary",message=f"You're missing the attribute/values dictionary need for metadata autocompletion \nI'm creating it in {save_dict}\n It can take some time if you have many files")
    easicmd.building_attributes_dictionnary()
    #print("easicmd.building_attributes_dictionnary()")
    showwarning(title="missing dictionary",message=f"It's done\nthanks for the wait")



root.mainloop()
