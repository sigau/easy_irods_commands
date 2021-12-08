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
                if os.path.isfile(sys.argv[2]) or os.path.isdir(sys.argv[2]) :
                    PUSH(sys.argv[2])
                else :
                    print("Give a correct local path to upload to irods")    
            else:
                print("Give a local path to upload to irods")
        
        elif sys.argv[1] == "pull":
            if len(sys.argv)>3 :
                if sys.argv[2] == "-f" or sys.argv[2] == "f":
                    PULL("-f",sys.argv[3])
                elif sys.argv[2] == "-C" or sys.argv[2] == "C":
                    PULL("-C",sys.argv[3])
                else:
                    print("possible option for type is -f or -C\n command should look like easicmd.py pull -f/-C local/path/to/download" )
            elif len(sys.argv)>2:
                if sys.argv[2] == "-f" or sys.argv[2] == "f":
                    PULL("-f",False)
                elif sys.argv[2] == "C" or sys.argv[2] == "C":
                    PULL("-C",False)
                else:
                    print("possible option for type is -f or -C\n command should look like easicmd.py pull -f/-C local/path/to/download" )
            else :
                print("you need to give at least the type of data you want to download from irods (-f or -C ) \nyou can also give the path to which you want to download the object\n command should look like easicmd.py pull -f/-C local/path/to/download")

        elif sys.argv[1] == "add_meta":
            if len(sys.argv)>2 :
                if sys.argv[2] == "-f" or sys.argv[2] == "-C":
                    call_iobject(sys.argv[2])
                    ADD_META(iobject)
                else :
                    asking("add metadata to")
                    ADD_META(iobject)
            else :
                asking("add metadata to")
                ADD_META(iobject)

        elif sys.argv[1]=="rm_meta":
            if len(sys.argv)>2 :
                if sys.argv[2] == "-f" or sys.argv[2] == "-C" :
                    call_iobject(sys.argv[2])
                    IRM_META(iobject)
                else :
                    asking("remove metadata from")
                    IRM_META(iobject)    
            else:
                asking("remove metadata from")
                IRM_META(iobject)

        elif sys.argv[1]=="imkdir":
            IMKDIR()

        elif sys.argv[1]=="irm":
            if len(sys.argv)>2 :
                if sys.argv[2] != "-f" and sys.argv[2] != "-C":
                    print("possible options are [-C] for a folder or [-f] for a file")

                else :
                    print("you can use * as wildcard")
                    call_iobject(sys.argv[2])
                    IRM(sys.argv[2], iobject)
            else :
                print("you can use * as wildcard while giving the file/folder name")
                asking('remove')
                IRM(ask, iobject)

        elif sys.argv[1] == "idush" :
            IDUSH()

        elif sys.argv[1] == "show_meta" :
            if len(sys.argv)>2 :
                if sys.argv[2] != "-f" and sys.argv[2] != "-C":
                    print("possible options are [-C] for a folder or [-f] for a file")

                else :
                    call_iobject(sys.argv[2])
                    SHOW_META(iobject)
            else:
                asking("show metadata associate with a")
                SHOW_META(iobject)

        elif sys.argv[1] == "search_by_meta":
            if len(sys.argv)>2 :
                if sys.argv[2] != "-f" and sys.argv[2] != "-C" and sys.argv[2] != "-u" and sys.argv[2] != "-d":
                    print("possible options are [-C] for a folder , [-f] for a file or [-u] for a user")

                else :
                    type_iobject=sys.argv[2]
                    if type_iobject == "-f":
                        type_iobject = "-d"
                    SEARCH_BY_META(type_iobject)
            else:
                type_iobject=input("search for a folder [-C], a file [-f] or a user [-u] : ")
                if type_iobject != "-f" and type_iobject != "-C" and type_iobject != "-u" :
                    print("possible options are [-C] for a folder , [-f] for a file or [-u] for a user")

                else :
                    if type_iobject == "-f":
                        type_iobject = "-d"
                    SEARCH_BY_META(type_iobject)
        
        elif sys.argv[1] == "search_name":
            if len(sys.argv)>2 :
                if sys.argv[2] == "-f" or sys.argv[2] == "-C" :
                    SEARCH_BY_NAME(sys.argv[2])
                else:
                    print("possible options are [-C] for a folder or [-f] for a file")
            else:
                ask=input("search for a file [f] or a folder [C] :")
                if ask == "f" or ask == "C" :
                    ask="-"+ask
                    SEARCH_BY_NAME(ask)
                else :
                    print("possible options are [-C] for a folder or [-f] for a file")
        
        elif sys.argv[1] == "synchro" :
            if len(sys.argv) == 3 :
                path=sys.argv[2]
                os.chdir(f"{path}/..")
                if path[-1] == "/":
                    path=path[:-1]
                basename=(path.split("/"))[-1]
                NEW_SYNCHRONISE(basename, None)
            elif len(sys.argv) == 4 :
                path=sys.argv[2]
                os.chdir(f"{path}/..")
                if path[-1] == "/":
                    path=path[:-1]
                basename=(path.split("/"))[-1]
                NEW_SYNCHRONISE(basename, sys.argv[3])
            else :
                print("Give a local path to upload to irods")
        
        
        else :
            help()
    else :
        help()

##########################################################################################################################################################################################################################################################################################
### fonction help 
##########################################################################################################################################################################################################################################################################################

def help():
    name()
    print("\nPossible COMMANDS :\n")
    print("\tadd_meta\t: add_meta or add_meta [irods path]\n\t\t if you don't give an irods path you'll be asked an option ([f] for file or [C] for a folder) then you will have to chose your object help by autocompletion\n")
    print("\thelp\t: print this help and leave")
    print("\tidush\t: equivalent to du -sh for an irods folder\n")
    print("\timkdir\t : imkdir -p reinforce by autocompletion\n")
    print("\tirm\t: irm [option]\n\t\t option are [-f] for a file and [-C] for a folder \n\t\t allow to irm one or multiple (if * used) folder/file in irods. You don't need to know the path in irods as it will be helped by autocompletion\n")
    print("\tpull\t: pull [option] [local path]\n\t\t  irsync/iget folder/file from irods to local with autocompletion\n\t\t  For a file add option -f\n\t\t  For a folder add option -C\n\t\t  path can be full path or '.' for current folder\n\t\t  if no path given, a list of all the folder from root will be proposed (can be very long if you have many)\n")     
    print("\tpush\t: irsync/iput folder/file (given by a path) from local to irods with auto completion\n")
    print("\trm_meta\t: rm_meta or rm_meta [irods path]\n\t\t  if you don't give an irods path you'll be asked an option ([f] for file or [C] for a folder) then you will have to chose your object help by autocompletion\n")
    print("\tsearch_by_meta\t: search_by_meta [option] or search_by_meta\n\t\t option are [-f] for a file, [-C] for a folder and [-u] for a user\n")
    print("\tsearch_name\t: search_name [option]\n\t\t option are [-f] for a file and [-C] for a folder \n\t\t search for a file or a folder in irods\n")    
    print("\tshow_meta\t: show_meta [option] or show_meta\n\t\t option are [-f] for a file and [-C] for a folder\n ")
    print("\tsynchro\t: synchro [local path to folder] [optional:irods path]\n\t\t synchronise the contain of a local folder with irods [in irods path if given or in /zone/home/user by default] based on the sha256\n\t\t the folder will be synchronised on /zone/home/user/  \n\t\t can be fully automated with the help of when-changed (https://github.com/joh/when-changed) with : when-changed -r -q [folder] -c 'easicmd.py synchro [folder]' ")
    print("\n\tSee some examples on https://github.com/sigau/easy_irods_commands ")

##########################################################################################################################################################################################################################################################################################
####             It's dangerous to go alone, take a coder
##########################################################################################################################################################################################################################################################################################

#                                   /   \
#  _                        )      ((   ))     (
# (@)                      /|\      ))_((     /|\
# |-|                     / | \    (/\|/\)   / | \                      (@)
# | | -------------------/--|-voV---\`|'/--Vov-|--\---------------------|-|
# |-|                         '^`   (o o)  '^`                          | |
# | |                               `\Y/'                               |-|
# |-|                        |_|. _   _    _ _|_                        | |
# | |                        | ||(_  _\|_|| | |                         |-|
# |-|                                                                   | |
# | |                        _| _ _  _ _  _  _  _                       |-|
# |-|                       (_|| (_|(_(_)| |(/__\                       | |
# |_|___________________________________________________________________| |
# (@)              l   /\ /         ( (       \ /\   l                `\|-|
#                  l /   V           \ \       V   \ l                  (@)
#                  l/                _) )_          \I
#                                    `\ /'

##########################################################################################################################################################################################################################################################################################
#### tools function's definition (function that will only be use by other functions to avoid redundancy )
##########################################################################################################################################################################################################################################################################################

def irods_collection():
    ##create a list with all the collection in irods for autocompletion later 
    global icol_completer
    global list_of_icollection
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
    global ifile
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
    
def list_sha_irods2():
    #same as  list_sha_irods() but for testing new_synchro:
    global list_isha2
    list_isha2={}
    cmd_ichecksum="ichksum ." ##get the modified sha for all the files in irods
    ichksum=(subprocess.run(cmd_ichecksum.split(),capture_output=True).stdout).decode("utf-8")
    for i in ichksum.split("\n"):
        if i!= "" and i[0] == "C" :
            collection=i.split()[1].replace(":", "")
            list_isha2[collection]=[]
        elif "sha2:" in i :
            isha=i.split("sha2:")[1]
            list_isha2[collection].append(isha)
    #print(list_isha2)


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

def asking(string):
    global ask
    ask=input(f"{string} folder (C) or file (f) : ")
    if ask != "f" and ask != "C" :
        print("possible options are [C] for a folder or [f] for a file")
        sys.exit()
    else:
        ask="-"+ask
        call_iobject(ask)

def building_attributes_dictionnary():
    global dico_attribute
    dico_attribute={}
    ##building the dictionary
    irods_collection()
    for ifolder in list_of_icollection:
        cmd_imetaLsD=f"imeta ls -C {ifolder}"
        imetaLsD=(subprocess.run(cmd_imetaLsD.split(),capture_output=True).stdout).decode("utf-8")
        for line in imetaLsD.split("\n"):
            if "attribute:" in line :
                attribut=line.split(":")[1]
            if "value:" in line :
                value=line.split(":")[1]
                if attribut not in dico_attribute:
                    dico_attribute[attribut]=set()
                    dico_attribute[attribut].add(value)
                else :
                    dico_attribute[attribut].add(value)
        list_ifile(ifolder)
        for irods_file in ifile:
            cmd_imetaLsF=f"imeta ls -d {irods_file}"
            imetaLsF=(subprocess.run(cmd_imetaLsF.split(),capture_output=True).stdout).decode("utf-8")
            for ligne in imetaLsF.split("\n"):
                if "attribute:" in ligne :
                    attribut=ligne.split(":")[1]
                if "value:" in ligne :
                    value=ligne.split(":")[1]
                    if attribut not in dico_attribute:
                        dico_attribute[attribut]=set()
                        dico_attribute[attribut].add(value)
                    else :
                        dico_attribute[attribut].add(value)

def auto_parsing_meta():
    ##automatically add metadata based on the parsing of the file/folder info like date/format/author
    print()

def name():
    print("  ______               _____   _____    _____   __  __   _____  ")
    print(" |  ____|     /\      / ____| |_   _|  / ____| |  \/  | |  __ \ ")
    print(" | |__       /  \    | (___     | |   | |      | \  / | | |  | |")
    print(" |  __|     / /\ \    \___ \    | |   | |      | |\/| | | |  | |")
    print(" | |____   / ____ \   ____) |  _| |_  | |____  | |  | | | |__| |")
    print(" |______| /_/    \_\ |_____/  |_____|  \_____| |_|  |_| |_____/\n")

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
        cmd_push=f"iput -PKVf {local_object} {irods_path}"
    else:
        cmd_push=f"iput -rPKVf {local_object} {irods_path}"
    subprocess.run(cmd_push.split())
    
    ##add meta 
    ask_add_meta=input("add metadata ?(y/n): ")
    if ask_add_meta == "y" or ask_add_meta == "Y" or ask_add_meta == "yes" or ask_add_meta == "YES" or ask_add_meta == "Yes":
        if local_object[-1] == "/": #if a folder is given with the / in the end we remove it 
            local_object=local_object[:-1]
        if "/" in local_object: ##when path (path/to/object) given we keep only the end as in irods 
            local_object=(local_object.split("/"))[-1] ## the new path will be irods_path/object
        new_iobject=(f"{irods_path}/{local_object}").replace("//", "/")
        ADD_META(new_iobject)
        print("\n")
        SHOW_META(new_iobject)

def PULL(type_iobject,local_path) :
    ##get back an object from irods and copy it on local folder or on a given path
    call_iobject(type_iobject)
    if not local_path :
        local_collection()
        local_path=prompt("local folder :",completer=folder_completer)
    if type_iobject == "-f" :
        if "%" in iobject :
            cmd_pull=(f"irsync -rKV i:{iobject} {local_path}".replace("//", "/")).replace("%", "")
        else :
            cmd_pull=f"iget -PKV {iobject} {local_path}".replace("//", "/")
    else :
        cmd_pull=f"iget -rPKV {iobject} {local_path}".replace("//", "/")
    subprocess.run(cmd_pull.split())
    

def ADD_META(iobject):
    ##loop to add meta data to a given object on irods that can be collection(folder), DataObject(file) or user
    building_attributes_dictionnary() ##if you don't want to have autocompletion on this command comment this
    list_value=[]
    list_key=[]
    for i in dico_attribute.values():   ##AND THIS
        for j in i : ## as every dictionary is a list we can't just use list(dict.values()) but use a loop on every list even if their compose of only one value
            if j not in list_value:
                list_value.append(j)
    for key in dico_attribute.keys(): ##AND THIS
        list_key.append(key)
    list_key.sort(key=str.lower)
    list_value.sort(key=str.lower)
    attribut="placeholder"
    while attribut !="":
        attribut_completer=WordCompleter(list_key) ##if you don't want to have autocompletion on this command comment this
        attribut=prompt("attribut (empty to stop) : ",completer=attribut_completer) ##AND THIS
        #attribut=input("attribut (empty to stop) : " ) ##if you don't want to have autocompletion on this command UNcomment this
        if attribut =="" :
            break
        value_completer=WordCompleter(list_value)   ##if you don't want to have autocompletion on this command comment this
        value=prompt("value : ",completer=value_completer)  ##AND THIS
        #value=input("value : ")    ##if you don't want to have autocompletion on this command UNcomment this
        unit=input("unit : ") 
        cmd_add_meta=f"imeta add {identify_iobject(iobject)} {iobject} {attribut} {value} {unit}"
        subprocess.run(cmd_add_meta.split())


def IRM_META(iobject):
    ##easy way of removing metadata from a object (remove all, one attribut)
    attribut=input("attribut (empty for all): ")
    if attribut =="":   
        attribut="%" ## % is the wildcards of irods
    cmd_irm_meta=f"imeta rmw {identify_iobject(iobject)} {iobject} {attribut} % %"
    subprocess.run(cmd_irm_meta.split())


def IMKDIR():
    ##easy way for creating an irods collection helped with autocompletion if you don't know the exact tree view
    irods_collection()
    mkdir=prompt("create : ",completer=icol_completer)
    cmd_imkdir=f"imkdir -p {mkdir}" ##-p create parents folder if needed
    subprocess.run(cmd_imkdir.split())


def IRM(type_iobject,iobject):
    ##easy way for deleting an object on irods helped with autocompletion. 
    ##can be collection(folder) or one/multiple Data_Object(file)
    if type_iobject == "-C":
        option="-rf"
    else :
        option="-f"
    if "*" in iobject:
        if type_iobject == "-C":
            count_slash=iobject.count("/")
            for i in list_of_icollection:
                if fnmatch.fnmatch(i,iobject) and i.count("/") == count_slash: ##ifiobject match in i and don't consider the subfolder of i 
                    cmd_irm=f"irm {option} {i}"
                    subprocess.run(cmd_irm.split())
        else :
            path=(iobject.split("/"))[:-1]
            path="/".join(path)
            for j in ifile:
                full_path=path+"/"+j
                if fnmatch.fnmatch(full_path, iobject): 
                    cmd_irm=f"irm {option} {full_path}"
                    subprocess.run(cmd_irm.split())                
    else :
        cmd_irm=f"irm {option} {iobject}"
        subprocess.run(cmd_irm.split())
        

def SHOW_META(iobject):
    ##easy way for showing the meta data associate with an irods object helped with autocompletion
    ##can be collection(folder), Data_Object(file) or user
    cmd_imeta_ls=f"imeta ls {identify_iobject(iobject)} {iobject}"
    subprocess.run(cmd_imeta_ls.split())


def SEARCH_BY_META(type_iobject):
    ##Search for an object(s) in irods by query the metadata associate with it/them
    ##The attributes exiting in irods are save in a dictionary as key with the (metadata) values associate with this attribute as (dictionary) values
    ##so the user can't ask for nonexistent attribut/values
    building_attributes_dictionnary()
    ##building the query
    list_operation=["=","like","\'>\'","\'<\'"]
    list_liaison=["","and",'or']
    liaison="placeholder"
    try :
        # qu_attribute_completer=WordCompleter(dico_attribute.keys)
        # qu_attribute=prompt("attribute: ",completer=qu_attribute_completer)
        # qu_value_completer=WordCompleter(dico_attribute[qu_attribute])
        # qu_value=prompt("value (% as *): ",completer=qu_value_completer)
        # if "%" in qu_value :
        #     operation="like"
        # else:
        #     operation= "="
        # ##run the query
        # cmd_imetaQu=f"imeta qu {type_iobject} {qu_attribute} {operation} {qu_value}"
        # subprocess.run(cmd_imetaQu.split())
        cmd_imetaQu=f"imeta qu {type_iobject}"
        while liaison != "" :
            qu_attribute_completer=WordCompleter(dico_attribute.keys)
            qu_attribute=prompt("attribute: ",completer=qu_attribute_completer)
            qu_value_completer=WordCompleter(dico_attribute[qu_attribute])
            qu_value=prompt("value (% as *): ",completer=qu_value_completer)
            operation_completer=WordCompleter(list_operation)
            operation=prompt("operation (like if your value contain % as a *): ",completer=operation_completer)
            liaison_completer=WordCompleter(list_liaison)
            liaison=prompt("liaison (empty to stop): ",completer=liaison_completer)
            cmd_imetaQu=f"{cmd_imetaQu} {qu_attribute} {operation} {qu_value} {liaison}"
        ##run the query
        qu_result=subprocess.check_output(cmd_imetaQu, shell=True,text=True )
        print(f"\n{qu_result}")
        #subprocess.run(cmd_imetaQu.split())
    except KeyError:
        print("Oops!  This attribute doesn't exist. Try again... (tap TAB to see the existing attributes)")
        SEARCH_BY_META(type_iobject)


def SEARCH_BY_NAME(type_iobject):
    ##search a file (with ilocate) or a folder store in the irods vault 
    if type_iobject == "-f" :
        search=input("your query(% as *) : ")
        cmd_ilocate=f"ilocate {search}"
        subprocess.run(cmd_ilocate.split())
    else :
        irods_collection()
        search=input("your query (you can use *): ")
        for i in list_of_icollection:
            if fnmatch.fnmatch(i, search) : ##if search match in i
                print(i)

def SYNCHRONISE(local_folder):
    ##synchronyse a local folder with irods vault by checking the sha256.
    ##If the folder doesn't exit on irods it's created then synchronised
    #automate with https://github.com/joh/when-changed ?
    irods_collection()
    list_sha_irods()
    dir_content=os.listdir(local_folder)
    for i in dir_content:
        if os.path.isfile(f"{local_folder}/{i}"):
            path_to_file=f"{local_folder}/{i}"
            cmd_sha=f"sha256sum {path_to_file} | awk '{{print $1}}' | xxd -r -p | base64"
            sha_256=(subprocess.check_output(cmd_sha, shell=True,text=True )).rstrip()
            if sha_256 not in list_isha:
                exist=False
                ### the (sub)folder is already in irods 
                for content in list_of_icollection:
                    if local_folder in content :
                        exist=True
                        break
                ### the (sub)folder is not yet in irods
                if exist==False :
                    cmd_imkdir=f"imkdir -p {local_folder}"
                    subprocess.run(cmd_imkdir.split())
                    irods_collection()
                cmd_iput=f"irsync -K {path_to_file} i:{local_folder}" #input need -f (force) to update an already existing file (aka modify file)
                subprocess.run(cmd_iput.split())
        else :
            SYNCHRONISE(f"{local_folder}/{i}") ##if folder recursive function

def NEW_SYNCHRONISE(local_folder,irods_path):
    irods_collection()
    list_sha_irods2()
    dir_content=os.listdir(local_folder)
    ##is the folder in irods ?
    exist=False
    search=f"*/{local_folder}"
    for collection in list_of_icollection :
        if fnmatch.fnmatch(collection, search ) :
            full_irods_path=collection
            exist=True
            break
    if exist == False :
        if irods_path :
            full_irods_path=f"{irods_path}/{local_folder}".replace("//", "/")
        else :
            ipwd=((subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")).replace("\n", "")
            full_irods_path=f"{ipwd}/{local_folder}".replace("//", "/")
        cmd_imkdir=f"imkdir -p {full_irods_path}"
        subprocess.run(cmd_imkdir.split())
        irods_collection() ##refresh with the new values
        list_sha_irods2() ##same
    
    ##synchronisation
    for objects in dir_content:
        objects_path=f"{local_folder}/{objects}".replace("//", "/")
        if os.path.isfile(objects_path) :
            cmd_sha=f"sha256sum {objects_path} | awk '{{print $1}}' | xxd -r -p | base64"
            sha_256=(subprocess.check_output(cmd_sha, shell=True,text=True )).rstrip()
            if sha_256 not in list_isha2[full_irods_path]:
                cmd_iput=f"irsync -K {objects_path} i:{full_irods_path}"
                subprocess.run(cmd_iput.split())
        else:
            size=len(objects_path.split("/"))-1 ## as we create each time from the same collection the new collection we need to give him always 
            new_irods_path="/".join((full_irods_path.split("/"))[:-size]) ## the same collection as irods_path or it recreate the full folder in the collection
            NEW_SYNCHRONISE(objects_path, new_irods_path)
        
def IDUSH():
    ##equivalent of the unix du -sh but on irods
    ##get the size (in bites) of all the file containing in a folder, add them and convert to human readable 
    irods_collection()
    irods_path=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if irods_path=="": 
        irods_path=((subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")).replace("\n", "/")
    cmd_ils=f"ils -rl {irods_path}"
    ils=(subprocess.run(cmd_ils.split(),capture_output=True).stdout).decode("utf-8")
    total_bits=0
    for line in ils.split("\n"):
        if "/" not in line and line !="":
            bits=int(line.split()[3])
            total_bits += bits
    print(sizeof_fmt(total_bits))

##########################################################################################################################################################################################################################################################################################
#### if __name__ == "__main__" 
##########################################################################################################################################################################################################################################################################################

if __name__ == "__main__":
    main()