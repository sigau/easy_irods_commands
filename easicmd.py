#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys,os,re, time, csv
import subprocess
import fnmatch
import pkg_resources
#from prompt_toolkit import prompt
#from prompt_toolkit.completion import WordCompleter

## two # (##) mean a commentary and one # (#) mean a option you can change at your own risk 

##########################################################################################################################################################################################################################################################################################
####  install dependancy (bad and temporary methods)
##########################################################################################################################################################################################################################################################################################

required = {"prompt_toolkit"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

##########################################################################################################################################################################################################################################################################################
####  main function
##########################################################################################################################################################################################################################################################################################

def main() :
    if len(sys.argv)>1:
        if sys.argv[1] == "push":
            if len(sys.argv)>2 :
                PUSH(sys.argv[2])
            else:
                print("Give a path to upload to irods")
        
        elif sys.argv[1] == "pull":
            if len(sys.argv)>3 :
                if sys.argv[2] == "-f" or sys.argv[2] == "f":
                    PULL("-f",sys.argv[3])
                elif sys.argv[2] == "-C" or sys.argv[2] == "C":
                    PULL("-C",sys.argv[3])
                else:
                    print("possible option for type is -f or -C" )
            elif len(sys.argv)>2:
                if sys.argv[2] == "-f" or sys.argv[2] == "f":
                    PULL("-f",False)
                elif sys.argv[2] == "C" or sys.argv[2] == "C":
                    PULL("-C",False)
                else:
                    print("possible option for type is -f or -C" )
            else :
                print("you need to give at least the type of data you want to download from irods (-f or -C ) \nyou can also give the path to which you want to download the object")

        elif sys.argv[1] == "add_meta":
            if len(sys.argv)>2 :
                ADD_META(sys.argv[2])
            else :
                ask=input("add metadata to folder (C) or file (f) : ")
                if ask != "f" or ask != "C" :
                    print("possible options are C for a folder or f for a file")
                    sys.exit()
                else:
                    ask="-"+ask
                call_iobject(ask) 
                ADD_META(iobject)

        
        else :
            help()
    else :
        help()
        
    


##########################################################################################################################################################################################################################################################################################
### fonction help 
##########################################################################################################################################################################################################################################################################################

def help():
    print("\nPossible OPTION :\n")
    print("\thelp\t: print this help and leave")
    print("\tpush\t: irsync/iput folder/file (given by a path) from local to irods with auto completion")
    print("\tpull\t: pull [option] [local path]\n\t\t  irsync/iget folder/file from irods to local with auto completion\n\t\t  For a file add option -f\n\t\t  For a folder add option -C\n\n\t\t  path can be full path or '.' for current folder\n\t\t  if no path given, a list of all the folder from root will be proposed (can be very long if you have many)") 
    print("\tadd_meta\t: add_meta or add_meta [irods path]\n\t\t  if you don't give an irods path you'll be ask an option ([f] for file or [C] for a folder) then you will have to chose your object help by autocompletion ")
    
##########################################################################################################################################################################################################################################################################################
#### tools function's definition (function that will only be use by over function to avoid redundancy )
##########################################################################################################################################################################################################################################################################################

def irods_collection():
    ##create a list with all the collection in irods for autocompletion later 
    global icol_completer
    list_of_icollection=[]
    cmd_ils="ils -r" ##list all the collection from your irods root
    ils=(subprocess.run(cmd_ils.split(),capture_output=True).stdout).decode("utf-8") #keep the output of a cmd in a variable
    for i in ils.split("\n"):
        if "  C- " in i :
            list_of_icollection.append(i.replace("  C- ", "")) ##keep only the collection represent by C- in irods
    icol_completer=WordCompleter(list_of_icollection)


def list_ifile(ifolder):
    ##list with all the ifile of a collection in irods for autocompletion later
    global ifile_completer
    ifile=[]
    cmd_ils=f"ils {ifolder}"
    ils=(subprocess.run(cmd_ils.split(), capture_output=True).stdout).decode("utf-8")
    for i in ils.split("\n"):
        if "/" not in i :  ##take everything except for the collection
            ifile.append(i.replace("  ", ""))
    ifile_completer=WordCompleter(ifile)


def local_collection():
    ##create a list of the local folder/subfolder from the current/roots directory for autocompletion later
    ##can take very long time if you have many folder  
    global folder_completer
    cmd="find ~/ -type d -not -path '*/\.*' " ##from roots
    #cmd="find -type d -path '*/\.*' -prune -o -type d " ## from current folder
    lsd=(subprocess.check_output(cmd, shell=True,text=True )).rstrip()
    folder_completer=WordCompleter(lsd.split("\n"))
    

def list_local_file(folder):
    ##create a list of all the files in a local folder for autocompletion later
    ##can take very long time if you have many
    global file_completer
    local_file=[]
    cmd_ls=f"ls -p {folder} | grep -v /"
    lsf=(subprocess.run(cmd_ls.split(), capture_output=True).stdout).decode("utf-8")
    for i in lsf.split("\n"):
        if os.path.isfile(f"{folder}/{i}"):
            local_file.append(i)
    file_completer=WordCompleter(local_file)


def list_sha_irods():
    ##creat a list of all the sha256 registered in the icat
    global list_isha
    list_isha=[]
    cmd_ichecksum="ichksum ." ##get the modified sha for all the files in irods
    ichksum=(subprocess.run(cmd_ichecksum.split(),capture_output=True).stdout).decode("utf-8")
    for i in ichksum.split("\n"):
        if "sha2:" in i :
            isha=i.split("sha2:")[1]
            list_isha.append(isha)


def identify_loc_object(object):
    ##identify is the object is a folder or a file and and associate a itype for irods commands
    global is_file
    if os.path.isfile(object) :
        type_iobject="-d"
        is_file=True
    else:
        type_iobject="-C"
        is_file=False
    return type_iobject


def identify_iobject(iobject):
    ##identify is the object is a collection(folder), object (file) (or user ?) 
    global is_ifile
    cmd_ils=f"ils {iobject}"
    ils=(subprocess.run(cmd_ils.split(),capture_output=True).stdout).decode("utf-8")
    if ":" not in ils:
        type_iobject="-d"
        is_ifile=True
    else :
        type_iobject="-C"
        is_ifile=False
    return type_iobject

def call_iobject(type_iobject):
    global iobject
    irods_collection()
    iobject=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if iobject == "":
        iobject=((subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")).replace("\n", "/")
    if type_iobject == "-f":
        list_ifile(iobject)
        iobject=(iobject+"/"+prompt("irods file (tap tab) :",completer=ifile_completer))
    

def sizeof_fmt(num, suffix="B"):
    ## transform size in bits in humain readable format
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}" 


##########################################################################################################################################################################################################################################################################################
#### called function's definition (function that will be "called" by the user/main )
##########################################################################################################################################################################################################################################################################################
def PUSH(local_object) :
    ##send an object to irods by irsync and add meta data on it 
    ##object can be folder or file given by path
    identify_loc_object(local_object)    
    irods_collection()

    irods_path=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if irods_path=="": 
        irods_path=((subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")).replace("\n", "/")
    if is_file:
        cmd_push=f"irsync -KV {local_object} i:{irods_path}"
    else:
        cmd_push=f"irsync -rKV {local_object} i:{irods_path}"
    subprocess.run(cmd_push.split())
    
    ##add meta 
    ask_add_meta=input("add metadata ?(y/n)")
    if ask_add_meta == "y" or ask_add_meta == "Y" or ask_add_meta == "yes" or ask_add_meta == "YES" or ask_add_meta == "Yes":
        if local_object[-1] == "/": ## if the user just put the files from the folder in a alreday existing
            ADD_META(irods_path) ## collection we add meta to this already existing collection
            sys.exit()
        if "/" in local_object: ##when path (path/to/object) given we keep only the end as in irods  
            local_object=(local_object.split("/"))[-1] ## the new path will be irods_path/object
        new_iobject=(f"{irods_path}/{local_object}").replace("//", "/")
        ADD_META(new_iobject)

def PULL(type_iobject,local_path) :
    ##get back an object from irods and copy it on local folder or on a given path
    call_iobject(type_iobject)
    if not local_path :
        local_collection()
        local_path=prompt("local folder :",completer=folder_completer)
    if type_iobject == "f" :
        cmd_pull=f"iget -PKV {iobject} {local_path}".replace("//", "/")
    else :
        cmd_pull=f"irsync -rKV i:{iobject} {local_path}".replace("//", "/")
    subprocess.run(cmd_pull.split())

    
def ADD_META(iobject):
    ##loop to add meta data to a given object on irods that can be collection(folder), DataObject(file) or user
    attribut="placeholder"
    while attribut !="":
        attribut=input("attribut : " )
        if attribut =="" :
            break
        value=input("value : ")
        unit=input("unit : ") 
        cmd_add_meta=f"imeta add {identify_iobject(iobject)} {iobject} {attribut} {value} {unit}"
        subprocess.run(cmd_add_meta.split())


def IRM_META(iobject):
    ##easy way of removing metadata from a object (remove all, one attribut)
    print()

def IMKDIR():
    ##easy way for creating an irods collection helped with autocompletion if you don't know the exact tree view
    print()

def IRM(type_iobject):
    ##easy way for deleting an object on irods helped with autocompletion. 
    ##can be collection(folder) or Data_Object(file)
    print()

def SHOW_META(type_iobject):
    ##easy way for showing the meta data associate with an irods object helped with autocompletion
    ##can be collection(folder), Data_Object(file) or user
    print()

def SEARCH_BY_META():
    ##Search for an object(s) in irods by query the metadata associate with it/them
    ##The attributes exiting in irods are save in a dictionary as key with the (metadata) values associate with this attribute as (dictionary) values
    ##so the user can't ask for nonexistent attribut/values
    print()

def SYNCHRONISE(local_folder):
    ##synchronyse a local folder with irods vault by checking the sha256.
    ##If the folder doesn't exit on irods it's created then synchronised
    print()

def IDUSH():
    ##equivalent of the unix du -sh but on irods
    ##get the size (in bites) of all the file containing in a folder, add them and convert to human readable 
    print() 
##########################################################################################################################################################################################################################################################################################
#### if __name__ == "__main__" 
##########################################################################################################################################################################################################################################################################################

if __name__ == "__main__":
    main()