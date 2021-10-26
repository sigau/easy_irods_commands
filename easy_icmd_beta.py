#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys,os,re, time, csv
import subprocess
import fnmatch
import pkg_resources
#from prompt_toolkit import prompt
#from prompt_toolkit.completion import WordCompleter

#pip install prompt_toolkit 

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
####  function's definition
##########################################################################################################################################################################################################################################################################################



def pushC(itype):
    irods_collection()
    local_collection()
    local_col_completer= WordCompleter(local_Sfolder) #we give a list of string that will be use for the autocompletion 
    icol_completer= WordCompleter(icollection) 
    FROM= prompt("local folder: ", completer=local_col_completer) #equivalent to input() but with the autocompletion ##FROM folder we want to send to irods here (FROM -> TO)
    if itype == "f":
        list_local_file(FROM) #FROM is the folder we want to know the file inside 
        file_completer=WordCompleter(local_file)
        FROM_file= prompt("local file: ", completer=file_completer)    
    TO= prompt("irods folder: ", completer=icol_completer)
    if TO =="" :
        subprocess.run("icd")
        TO=(subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")
    if itype == "f" :
        cmd_push=f"iput -PKV {FROM}/{FROM_file} {TO}"
    else :
        cmd_push=f"irsync -rKV {FROM} i:{TO}"
    subprocess.run(cmd_push.split())

    #add metadata
    ask_meta=input("add metadata ?(y/n)")
    if ask_meta == "y" or ask_meta == "Y" or ask_meta == "yes" or ask_meta == "YES" or ask_meta == "Yes":
        if itype == "f":
            file_i=f"{TO}/{FROM_file}"
            add_meta(file_i)
        else :
            add_meta(TO)

def pullC(itype):
    irods_collection()
    local_collection()
    local_col_completer= WordCompleter(local_Sfolder) 
    icol_completer= WordCompleter(icollection)
    FROM= prompt("irods folder: ", completer=icol_completer)
    if itype == "f":
        list_ifile(FROM)
        ifile_completer= WordCompleter(ifile)
        FROM_file= prompt("irods file: ", completer=ifile_completer)
    TO= prompt("local folder: ", completer=local_col_completer)
    if itype == "f" :
        cmd_push=f"iget -PKV {FROM}/{FROM_file} {TO}"
    else:
        cmd_push=f"irsync -rKV i:{FROM} {TO}"
    subprocess.run(cmd_push.split())

def irods_collection():
    ##create a list with all the collection in irods for autocompletion later 
    global icollection
    subprocess.run("icd")
    icmd="ils -r"
    icollection=[]
    ils=(subprocess.run(icmd.split(), capture_output=True).stdout).decode("utf-8")
    for i in ils.split("\n"):
        if "  C- " in i :
            icollection.append(i.replace("  C- ",""))

def local_collection():
    #create a list of the local folder/subfolder from the current directory  
    global local_Sfolder
    cmd="find ~/ -type d -not -path '*/\.*' "
    lsd=(subprocess.check_output(cmd, shell=True,text=True )).rstrip()
    local_Sfolder=lsd.split("\n")

def add_meta(objects):
    #determinate type
    cmd_ils=f'ils {objects}'
    ils=(subprocess.run(cmd_ils.split(), capture_output=True).stdout).decode("utf-8")
    if fnmatch.fnmatch(objects,'*.*') :
        itype="-d"
    else:
        itype="-C"
    
    #loop for metadata
    attribut="placeholder"
    while attribut != "" :
        attribut=input("attribut : " )
        if attribut =="" :
            break
        value=input("value : ")
        unit=input("unit : ")
        cmd_meta=f"imeta add {itype} {objects} {attribut} {value} {unit}"
        subprocess.run(cmd_meta.split())
    #cmd_meta_ls=f"imeta ls {itype} {objects}"
    #subprocess.run(cmd_meta_ls.split())

def imeta_irmw(type_rm):
    irods_collection()
    icol_completer= WordCompleter(icollection)
    TO= prompt("irods folder: ", completer=icol_completer)
    if type_rm == "f" :
        list_ifile(TO)
        ifile_completer=WordCompleter(ifile)
        file_i= prompt("file irods: ", completer=ifile_completer)
    attribut=input("attribut (empty for all): ")
    if attribut =="":   # % is the wildcards of irods
        attribut="%"
    if type_rm == "f":
        cmd_irm=f"imeta rmw -d {TO}/{file_i} {attribut} % %"
    else :
        cmd_irm=f"imeta rmw -C {TO} {attribut} % %"
    subprocess.run(cmd_irm.split())

def imkdir():
    irods_collection()
    icol_completer= WordCompleter(icollection)
    mkdir= prompt("create : ",completer=icol_completer)
    cmd_imkdir=f"imkdir -p {mkdir}" #-p create parents folder if needed
    subprocess.run(cmd_imkdir.split())

def irm(type_rm):
    irods_collection()
    icol_completer= WordCompleter(icollection)
    rm= prompt("irm folder: ",completer=icol_completer)    
    if type_rm == "f":
        list_ifile(rm)
        ifile_completer= WordCompleter(ifile)
        rm_file=prompt("irm file (* for wildcard): ", completer=ifile_completer)
        if "*" in rm_file:
            for i in ifile :
                if fnmatch.fnmatch(i,rm_file):
                    cmd_rm=f"irm {rm}/{i}"
                    subprocess.run(cmd_rm.split())
        else :
            cmd_rm=f"irm {rm}/{rm_file}"
            subprocess.run(cmd_rm.split())

    else:
        cmd_irm=f"irm -rf {rm}"
        subprocess.run(cmd_irm.split())

def list_ifile(folder):
    icd=f"icd {folder}"
    subprocess.run(icd.split())
    global ifile
    ifile=[]
    ils=(subprocess.run("ils", capture_output=True).stdout).decode("utf-8")
    for i in ils.split("\n"):
        if "  C- " not in i and "/" not in i : #take everything except for the collection
            ifile.append(i.replace("  ",""))

def list_local_file(folder):
    global local_file
    local_file=[]
    ls=f"ls -p {folder} | grep -v /"
    ls_list=(subprocess.run(ls.split(), capture_output=True).stdout).decode("utf-8")
    for i in ls_list.split("\n"): #transform the plain output in a list spliting with the \n
        if os.path.isfile(f"{folder}/{i}"):
            local_file.append(i)

def list_sha_irods():
    global ilist_sha
    ilist_sha=[]
    subprocess.run("icd")
    ichksum_cmd="ichksum ." #get the modified sha for all the files in irods
    ichksum=(subprocess.run(ichksum_cmd.split(),capture_output=True).stdout).decode("utf-8")
    for i in ichksum.split("\n") :
        if "sha2:" in i:
            sha=i.split("sha2:")[1]
            ilist_sha.append(sha)

def show_meta(object_type):
    irods_collection()
    icol_completer=WordCompleter(icollection)
    ifolder=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if ifolder == "" :
        subprocess.run("icd")
        ifolder=(subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")
    if object_type == "f" :
        list_ifile(ifolder)
        irods_files_completer=WordCompleter(ifile)
        irods_files=prompt("file: ",completer=irods_files_completer)
        cmd_imetaLs=f"imeta ls -d {irods_files}"
    else:
        cmd_imetaLs=f"imeta ls -C {ifolder}"
    subprocess.run(cmd_imetaLs.split())

def search_by_dico():
    dico_attribute={}
    irods_collection()
    for ifolder in icollection:
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

    ##query imeta qu -d/-C {atribut}
    itype=input("search for a folder (C) or a file (d) or user (u): " )
    if itype == "C" or itype == "c" or itype == "folder" or itype == "collection" :
        itype = "-C"
    elif itype == "d" or itype == "file" or itype == "data-object" or itype == "f":
        itype = "-d"
    elif itype == "u" or itype == "U" or itype == "user" :
        itype = "-u"
    else :
        print("possible input are 'C' ,'f' and 'u'")
        sys.exit()
    
    qu_attribute_completer=WordCompleter(dico_attribute.keys)
    qu_attribute=prompt("attribute: ",completer=qu_attribute_completer)
    qu_value_completer=WordCompleter(dico_attribute[qu_attribute])
    qu_value=prompt("value (% as *): ",completer=qu_value_completer)
    if "%" in qu_value :
        operation="like"
    else:
        operation= "="
    cmd_imetaQu=f"imeta qu {itype} {qu_attribute} {operation} {qu_value}"
    subprocess.run(cmd_imetaQu.split())    

def synchronise(folder):
    #automase with https://github.com/joh/when-changed ? 
    #synchronise automaticly a folder with irods vault by checking the sha256
    #usage of sha2 ? --> https://docs.irods.org/4.2.7/system_overview/tips_and_tricks/
    #make list of ifolder --> icollection 
    #find path of local folder in list of ifolder
    irods_collection()
    list_sha_irods()
    print(f"folder:{folder}")
    subprocess.run("pwd")
    dir_content=os.listdir(folder)
    for i in dir_content :
        
        if os.path.isfile(f"{folder}/{i}"):
            path_to_file=f"{folder}/{i}"
            cmd_sha=f"sha256sum {path_to_file} | awk '{{print $1}}' | xxd -r -p | base64"
            sha_256=(subprocess.check_output(cmd_sha, shell=True,text=True )).rstrip()
            if sha_256 not in ilist_sha:
                exist=False
                ### the (sub)folder is already in irods 
                for content in icollection:
                    if folder in content :
                        exist=True
                        break
                ### the (sub)folder is not yet in irods
                if exist==False :
                    cmd_imkdir=f"imkdir -p {folder}"
                    subprocess.run(cmd_imkdir.split())
                    irods_collection()
                
                cmd_iput=f"irsync -K {path_to_file} i:{folder}" #input need -f (force) to update an already existing file (aka modify file)
                subprocess.run(cmd_iput.split())

        else :
            synchronise(f"{folder}/{i}") #if folder recursive function 

def idush():
    irods_collection()
    icol_completer= WordCompleter(icollection)
    ifolder=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if ifolder == "" :
        subprocess.run("icd")
        ifolder=(subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")
    
    cmd_ils=f"ils -rl {ifolder}"
    ils=(subprocess.run(cmd_ils.split(),capture_output=True).stdout).decode("utf-8")
    total_bits=0
    for line in ils.split("\n"):
        if "/" not in line and line !="":
            bits=int(line.split()[3])
            total_bits += bits
    print(sizeof_fmt(total_bits))


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

##########################################################################################################################################################################################################################################################################################
### fonction help 
##########################################################################################################################################################################################################################################################################################

def helper():
    print("\nPossible OPTION :\t(For using the autocompletion use TAB)\n")
    print("\thelp   : print this help and leave")
    print("\tpush : irsync/iput folder/file from local to irods with auto completion, for a file add option f (./irods_cmd.py push or ./irods_cmd.py push f) ")
    print("\tpull : irsync/iget folder/file from irods to local with auto completion, for a file add option f (./irods_cmd.py pull or ./irods_cmd.py pull f)")
    print("\tadd_meta : add metadata to a folder/file on irods using auto completion, for a file add option f (you can use $ as a * for multiple files)")
    print("\trm_meta : remove metadata, for a file add option f")
    print("\tshow_meta : show metadata associated with a folder/file, for a file add option f")
    print("\timkdir : imkdir -p reinforce by auto completion")
    print("\tirm : irm reinforce by auto completion, for a file add option f (./irods_cmd.py irm f)")
    print("\tsynchro {folder} : synchronise the contain of a local folder with irods")
    print("\tsearch : search for a folder/file on irods based on the metadata")
    print("\tdush : equivalent du -sh for an irods folder ")
    print("\n\tATTENTION WITH PULL/PUSH A FOLDER WE USE IRSYNC SO AS WITH RSYNC :\n\tirsync source destination/ : will create a folder source in destination \n\tirsync source/ destination/ : will copy the content of source in destination")


##########################################################################################################################################################################################################################################################################################
### "main"
##########################################################################################################################################################################################################################################################################################

if len(sys.argv)>1 :
    if sys.argv[1] == "push":
        if len(sys.argv)>2 and sys.argv[2] == "f":
            pushC("f")
        else :
            pushC(0)
    
    elif sys.argv[1] == "pull":
        if len(sys.argv)>2 and sys.argv[2] == "f":
            pullC("f")
        else :
            pullC(0)

    elif sys.argv[1] == "add_meta":
        if len(sys.argv)>2 and sys.argv[2] == "f":
            irods_collection()
            icol_completer= WordCompleter(icollection)
            TO= prompt("irods folder (empty = /zone/home/user ): ", completer=icol_completer) #TO= irods folder 
            if TO == "" :
                subprocess.run("icd")
                TO=(subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")
            list_ifile(TO)
            ifile_completer= WordCompleter(ifile)
            TO_file= prompt("irods file: ", completer=ifile_completer) #TO_file = file in the folder(TO) on irods
            file_i=f"{TO}/{TO_file}"
            add_meta(file_i)

        else:
            irods_collection()
            icol_completer= WordCompleter(icollection)
            TO= prompt("irods folder (empty = /zone/home/user ): ", completer=icol_completer)
            if TO == "" :
                subprocess.run("icd")
                TO=(subprocess.run("ipwd",capture_output=True).stdout).decode("utf-8")
            list_ifile(TO)
            add_meta(TO)
    
    elif sys.argv[1] == "rm_meta" :
        if len(sys.argv)>2 and sys.argv[2] == "f":
            imeta_irmw("f")
        else:
            imeta_irmw(0)

    elif sys.argv[1] == "imkdir" :
        imkdir()

    elif sys.argv[1] == "irm" :
        if len(sys.argv)>2 and sys.argv[2] == "f":
            irm("f")
        else :
            irm(0)
    elif sys.argv[1] == "synchro":
        if len(sys.argv)>2 :
            path=sys.argv[2]
            os.chdir(f"{path}/..")
            if path[-1] == "/":
                path=path[:-1]
            basename=(path.split("/"))[-1]
            synchronise(basename)

        else :
            path=input("which folder ? :")
            os.chdir(f"{path}/..")
            if path[-1] == "/":
                path=path[:-1]
            basename=(path.split("/"))[-1]
            synchronise(basename)

    elif sys.argv[1] == "search" :
        search_by_dico()

    elif sys.argv[1] == "show_meta" :
        if len(sys.argv)>2 and sys.argv[2] == "f":
             show_meta("f")
        else :
            show_meta(0)

    elif sys.argv[1] == "dush" :
        idush()

    else:
        helper()
else:
    helper()


##########################################################################################################################################################################################################################################################################################
### Hic sunt dracones 
##########################################################################################################################################################################################################################################################################################
