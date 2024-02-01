#!/usr/bin/env python3 
# -*- coding: utf-8 -*

##########################################################################################################################################################################################################################################################################################
####  calling library
##########################################################################################################################################################################################################################################################################################


import sys,os,re, time, csv, queue, threading
import subprocess
import fnmatch
import pkg_resources
import pickle
import platform
import json
from irods.session import iRODSSession
from irods.column import Criterion
from irods.models import DataObject, DataObjectMeta, Collection, CollectionMeta, User
from irods.meta import iRODSMeta
from irods.user import iRODSUser
from pprint import pprint
from irods.collection import iRODSCollection
from irods.access import iRODSAccess
from cryptography.fernet import Fernet


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
####  identify platform
##########################################################################################################################################################################################################################################################################################

global pickle_meta_dictionary_path
global pickle_irods_path_path 
global pickle_additional_path_path
global irods_key_path
global irods_password_path
global irods_info_files

if platform.system() == "Linux":
    pickle_meta_dictionary_path = os.path.expanduser("~/.neo_irods_metadata_local_save.pkl")
    pickle_irods_path_path = os.path.expanduser("~/.neo_irods_collection_save.pkl")
    pickle_additional_path_path = os.path.expanduser("~/.neo_irods_additional_path_save.pkl")
    irods_key_path = os.path.expanduser("~/.easicmd.key")
    irods_password_path = os.path.expanduser("~/.easicmd.psw")
    irods_info_files = os.path.expanduser("~/.easicmd.info")

elif platform.system() == "Windows":
    pickle_meta_dictionary_path = os.path.expanduser("~\.irods_metadata_local_save.pkl")
    pickle_irods_path_path = os.path.expanduser("~\.irods_collection_save.pkl")
    pickle_additional_path_path = os.path.expanduser("~\.irods_additional_path_save.pkl")
    irods_key_path = os.path.expanduser("~\.easicmd.key")
    irods_password_path = os.path.expanduser("~\.easicmd.psw")
    irods_info_files = os.path.expanduser("~\.easicmd.info")

elif platform.system() == "Darwin":
    pickle_meta_dictionary_path= os.path.expanduser("~/.irods_metadata_local_save.pkl")
    pickle_irods_path_path = os.path.expanduser("~/.irods_collection_save.pkl")
    pickle_additional_path_path = os.path.expanduser("~/.irods_additional_path_save.pkl")
    irods_key_path = os.path.expanduser("~/.easicmd.key")
    irods_password_path = os.path.expanduser("~/.easicmd.psw")
    irods_info_files = os.path.expanduser("~/.easicmd.info")



##########################################################################################################################################################################################################################################################################################
#### number of threads to used
##########################################################################################################################################################################################################################################################################################
nb_threads = (os.cpu_count() - 1) 
if nb_threads == 0 :
    nb_threads = 1

##########################################################################################################################################################################################################################################################################################
####  main function
##########################################################################################################################################################################################################################################################################################

def main() :
    ## get the user irods information for creating a session
    get_irods_info()
    
    if len(sys.argv)>1:
        if sys.argv[1] == "push":
            if len(sys.argv)>2 :
                if os.path.isfile(sys.argv[2]) or os.path.isdir(sys.argv[2]) :
                    args=sys.argv[2]
                    if args[-1] == "/":
                        args=args[:-1]
                    PUSH(args)
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
                    elif sys.argv[2] == "-C" or sys.argv[2] == "C":
                        PULL("-C",False)
                    else:
                        print("possible option for type is -f or -C\n command should look like easicmd.py pull -f/-C local/path/to/download" )
                else :
                    print("you need to give at least the type of data you want to download from irods (-f or -C ) \nyou can also give the path to which you want to download the object\n command should look like easicmd.py pull -f/-C local/path/to/download")
        
        elif sys.argv[1]=="imkdir":
            get_irods_collection()
            mkdir=prompt("create : ",completer=icol_completer)
            IMKDIR(mkdir)
        
        elif sys.argv[1]=="irm":
            if len(sys.argv)>2 :
                if sys.argv[2] != "-f" and sys.argv[2] != "-C":
                    print("possible options are [-C] for a folder or [-f] for a file")

                else :
                    #print("you can use * as wildcard")
                    call_iobject(sys.argv[2])
                    IRM(sys.argv[2], iobject)
            else :
                #print("you can use * as wildcard while giving the file/folder name")
                asking('remove')
                IRM(ask, iobject)


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
        
        elif sys.argv[1] == "idush" :
            get_irods_collection()
            irods_path=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
            IDUSH(irods_path)

        elif sys.argv[1] == "ichmod" :
            asking("Give permission for a")
            ICHMOD(iobject)

        elif sys.argv[1] == "build_dico_meta":
            building_attributes_dictionnary()

        elif sys.argv[1] == "add_path":
            ADD_ADDITIONAL_PATH()

        elif sys.argv[1] == "rm_path":
            RM_ADDITIONAL_PATH()

        elif sys.argv[1] == "search_name":
            tofind=input("your search : ")
            if len(sys.argv)>2 :
                if sys.argv[2] != "-f" and sys.argv[2] != "-C":
                    SEARCH_BY_NAME(tofind,type_iobject=None)
                elif sys.argv[2] == "-f" or sys.argv[2] == "-C":
                    SEARCH_BY_NAME(tofind,type_iobject=sys.argv[2])
            else:
                SEARCH_BY_NAME(tofind,type_iobject=None)

        elif sys.argv[1] == "test" :
            PUSH_SPEEDTEST(sys.argv[2],sys.argv[3])

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
    print("\tadd_path\t: add additional path to your irods path autocompletion (e.g : not my home but a common folder for a project)(stock in a file for later)")
    print("\tbuild_dico_meta\t: create a file in your home directory containing the dictionary with your metadata attribute and value.\n\t\tAs it's in local you just to have to run this the first time and when you add metadata it will be update.\n\t\tThis is usefull because when you have many file in your irods vault it take a very long time to get this dictionary if you have to do it every time you need the autocompletion for metadata  ")
    print("\thelp\t: print this help and leave")
    print("\tichmod\t: give right to other user/group over some of your data (e.g give read right over one iCollection)")
    print("\tidush\t: equivalent to du -sh for an irods folder\n")
    print("\timkdir\t : imkdir -p reinforce by autocompletion\n")
    print("\tirm\t: irm [option]\n\t\t option are [-f] for a file and [-C] for a folder \n\t\t allow to irm one or multiple (if * used) folder/file in irods. You don't need to know the path in irods as it will be helped by autocompletion\n")
    print("\tpull\t: pull [option] [local path]\n\t\t  irsync/iget folder/file from irods to local with autocompletion\n\t\t  For a file add option -f\n\t\t  For a folder add option -C\n\t\t  path can be full path or '.' for current folder\n\t\t  if no path given, a list of all the folder from root will be proposed (can be very long if you have many)\n")     
    print("\tpush\t: irsync/iput folder/file (given by a path) from local to irods with auto completion\n")
    print("\trm_meta\t: rm_meta or rm_meta [irods path]\n\t\t  if you don't give an irods path you'll be asked an option ([f] for file or [C] for a folder) then you will have to chose your object help by autocompletion\n")
    print("\trm_path\t: remove additional path you already add but don't need anymore\n")
    print("\tsearch_by_meta\t: search_by_meta [option] or search_by_meta\n\t\t option are [-f] for a file, [-C] for a folder and [-u] for a user\n")
    print("\tsearch_name\t: search_name [option]\n\t\t option are [-f] for a file and [-C] for a folder or nothing for both \n\t\t search for a file or a folder in irods\n")    
    print("\tshow_meta\t: show_meta [option] or show_meta\n\t\t option are [-f] for a file and [-C] for a folder\n ")
    #print("\tsynchro\t: synchro [local path to folder] [optional:irods path]\n\t\t synchronise the contain of a local folder with irods [in irods path if given or in /zone/home/user by default] based on the sha256\n\t\t the folder will be synchronised on /zone/home/user/  \n\t\t can be fully automated with the help of when-changed (https://github.com/joh/when-changed) with : when-changed -r -q [folder] -c 'easicmd.py synchro [folder]' ")
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
def name():
    print("  ______               _____   _____    _____   __  __   _____  ")
    print(" |  ____|     /\      / ____| |_   _|  / ____| |  \/  | |  __ \ ")
    print(" | |__       /  \    | (___     | |   | |      | \  / | | |  | |")
    print(" |  __|     / /\ \    \___ \    | |   | |      | |\/| | | |  | |")
    print(" | |____   / ____ \   ____) |  _| |_  | |____  | |  | | | |__| |")
    print(" |______| /_/    \_\ |_____/  |_____|  \_____| |_|  |_| |_____/\n")


## Générer une clé secrète
def generate_key():
    return Fernet.generate_key()

## Enregistrer la clé dans un fichier
def save_key(key, filename=irods_key_path):
    with open(filename, "wb") as key_file:
        key_file.write(key)

## Charger la clé depuis un fichier
def load_key(filename=irods_key_path):
    return open(filename, "rb").read()

## Crypter une chaîne de caractères
def encrypt_message(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

## Décrypter une chaîne de caractères
def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

def save_pswd(PASSWORD):
    ## Générer et enregistrer une clé
    key = generate_key()
    save_key(key)
    ## Crypter la chaîne
    encrypted_message = encrypt_message(PASSWORD, key)
    ## Enregistrer la chaîne cryptée dans un fichier
    with open(irods_password_path, "wb") as file:
        file.write(encrypted_message)

def get_irods_password():
    global PASSWORD
    PASSWORD = ""

    ## Verify if a key path exist 
    ## If it exist the password has been save and encrypt so we have to decrypt it
    if os.path.isfile(irods_key_path):
        ## Charger la clé depuis le fichier
        loaded_key = load_key()

        ## Lire la chaîne cryptée depuis le fichier
        with open(irods_password_path) as file:
            loaded_encrypted_message = file.read()

        ## Décrypter la chaîne
        PASSWORD = decrypt_message(loaded_encrypted_message, loaded_key)

    ## password wasn't save we can just ask it 
    else :
        caller = __name__
        if caller == "__main__" : 
            PASSWORD=input("ENTER YOUR IRODS PASSWORD : ")
            ## Do the user want to save it 
            answer=input(f"Do you want to save it for later (the password will be encrypt and stock in {irods_password_path} [Y/N] : ")
            if answer == "Y" or answer == "y" or answer == "yes" or answer == "YES" : 
                save_pswd(PASSWORD)

def get_irods_info():
    global irods_config
    ## le fichier config existe deja 
    if os.path.isfile(irods_info_files) :
        with open(irods_info_files) as f:
            irods_config = json.loads(f.read())
        get_irods_password()
        irods_config["password"] = PASSWORD

    
    else :
        ## le fichier config n'hesite pas
        ## if i call this functtion from api_gui_easicmd.py or api_easicmd.py I don't want the same reaction 
        ## I'm calling from api_easicmd.py
        caller = __name__
        if caller == "__main__" : 
            print(f"creating the irods config file in {irods_info_files} (equivalent to irods_environment.json with icommand/iinit)")
            host = input("host: ")
            port = input("port: ")
            user = input("user: ")
            zone = input("zone: ")
            irods_config = {'host': host, 'port': port, 'user': user, 'zone': zone}
            with open(irods_info_files,"w") as f :
                json.dump(irods_config,f)
            get_irods_password()
            irods_config["password"] = PASSWORD
            
        ## else : I'm calling from api_gui_easicmd.py


def irods_collection():
    ##create a list with all the collection in irods for autocompletion later 
    global icol_completer
    global list_of_icollection

    list_of_icollection=[]

    ##Create a irods session
    with iRODSSession(**irods_config) as session:
        results=session.query(Collection.name)
    ## keep all the results in a list of collections
    for result in results:
        list_of_icollection.append(result[Collection.name])
        list_of_icollection.sort()
    ## Save all the collection in a local file to save time later
    new_path_file=os.path.expanduser(pickle_additional_path_path)
    ## create a object storing the collection for automatic completion
    icol_completer=WordCompleter(list_of_icollection)


def initialise_irods_collection():
    ## create a pickles with all the irods folder to save time later 
    print("create a file with all the irods folder to save time later\nif you already have some irods folder it can take a bit of time ")
    irods_collection()
    pickles_path=os.path.expanduser(pickle_irods_path_path)
    with open(pickles_path,"wb") as f:
        pickle.dump(list_of_icollection, f)
    print("a list or your irods collection have been save ")


def get_irods_collection():
    ## read the pickles with the irods collection and if not existing create it 
    ## you don't have to "recalculate" your collection only read thge pickles 
    global icol_completer
    global list_of_icollection
    pickles_path=os.path.expanduser(pickle_irods_path_path)
    if os.path.isfile(pickles_path):
        with open(pickles_path,"rb") as f:
            list_of_icollection=pickle.load(f)
            icol_completer=WordCompleter(list_of_icollection)

    else:
        initialise_irods_collection()
    

def update_irods_collection(action,path):
    ##update the pickles file when you push a folder or remove one 
    global list_of_icollection
    get_irods_collection()
    pickles_path=os.path.expanduser(pickle_irods_path_path)

    ## we push a new folder we have to add this folder and subfolder in our list
    if action=="add" :
        ##Create a irods session
        with iRODSSession(**irods_config) as session:
            results=session.query(Collection.name).filter(Criterion("like", Collection.name, path))

        for result in results:
            list_of_icollection.append(result[Collection.name])
        
        list_of_icollection.sort()
        list_of_icollection = list(dict.fromkeys(list_of_icollection)) ## no double in my list please

    ## we remove a folder we have to remobe this folder and subfolder from our list                
    else:
        list_tmp=[]
        for j in list_of_icollection:
            if path not in j :
                list_tmp.append(j)
        list_of_icollection = list_tmp
        list_of_icollection = list(dict.fromkeys(list_of_icollection)) ## no double in my list please
        
    ## save the update list            
    with open(pickles_path,"wb") as f:
        pickle.dump(list_of_icollection, f)
    print("your irods collecion pickle have been updated ")


def update_irods_collection2(action,path):
    ##update the pickles file when you push a folder or remove one 
    global list_of_icollection
    get_irods_collection()
    pickles_path=os.path.expanduser(pickle_irods_path_path)

    ## we push a new folder we have to add this folder and subfolder in our list
    if action=="add" :
        ##Create a irods session
        list_of_icollection.append(path)
        
        list_of_icollection.sort()
        list_of_icollection = list(dict.fromkeys(list_of_icollection)) ## no double in my list please

    ## we remove a folder we have to remobe this folder and subfolder from our list                
    else:
        list_tmp=[]
        for j in list_of_icollection:
            if path not in j :
                list_tmp.append(j)
        list_of_icollection = list_tmp
        list_of_icollection = list(dict.fromkeys(list_of_icollection)) ## no double in my list please
        
    ## save the update list            
    with open(pickles_path,"wb") as f:
        pickle.dump(list_of_icollection, f)
    print("your irods collecion pickle have been updated ")


def list_ifile(ifolder):
    ##list with all the ifile of a collection in irods for autocompletion later
    global ifile_completer
    global ifile
    ifile=[]
    
    ##Create a irods session
    with iRODSSession(**irods_config) as session:
        results=session.query(Collection.name,DataObject.name).filter(Criterion("=", Collection.name, ifolder))

    for result in results:
        ifile.append(result[DataObject.name])
    ifile.sort()
    ifile_completer=WordCompleter(ifile)
 

def local_collection():
    ##create a list of the local folder/subfolder from the current/roots directory for autocompletion later
    ##can take very long time if you have many folder  
    global folder_completer
    dossiers_non_caches = [d for d in lister_dossiers_recursivement(os.path.expanduser("~"))] ## from the user home 
    #dossiers_non_caches = [d for d in lister_dossiers_recursivement(os.getcwd())] ## from the current folder
    #dossiers_non_caches = [d for d in lister_dossiers_recursivement("/")] ##from root
    folder_completer=WordCompleter(dossiers_non_caches)


def lister_dossiers_recursivement(chemin):
    dossiers = []
    try:
        for nom in os.listdir(chemin):
            chemin_complet = os.path.join(chemin, nom)
            # Exclure les dossiers cachés
            if os.path.isdir(chemin_complet) and not (nom.startswith('.') or nom.startswith('$')):
                dossiers.append(chemin_complet)
                dossiers.extend(lister_dossiers_recursivement(chemin_complet))
    except PermissionError as e:
        print(f"Erreur de permission pour le dossier '{chemin}': {e}")
    return dossiers


def list_local_file(folder):
    ##create a list of all the files in a local folder for autocompletion later
    ##can take very long time if you have many
    global file_completer
    local_file=[]
    local_file = [f for f in os.listdir(os.path.expanduser(folder)) if os.path.isfile(os.path.join(os.path.expanduser(folder), f))]
    local_file.sort()
    file_completer=WordCompleter(local_file)


def identify_loc_object(object):
    ##identify is the object is a folder or a file and and associate a itype for irods commands
    global is_file
    if os.path.isfile(os.path.expanduser(object)) :
        type_iobject="-d"
        is_file=True
    else:
        type_iobject="-C"
        is_file=False
    return type_iobject


def identify_iobject(iobject):
    global is_ifile
    with iRODSSession(**irods_config) as session:
        if session.data_objects.exists(iobject):
            type_iobject="-d"
            is_ifile=True
        elif  session.collections.exists(iobject) : 
            type_iobject="-C"
            is_ifile=False
        else:
            print("it's not a folder nor a file try again")
            sys.exit()
    return type_iobject


def call_iobject(type_iobject):
    global iobject
    get_irods_collection()
    iobject=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if iobject == "":
        iobject=f"/{irods_config['zone']}/home/{irods_config['user']}"
    if type_iobject == "-f":
        list_ifile(iobject)
        iobject=(iobject+"/"+prompt("irods file (tap tab) :",completer=ifile_completer))


def sizeof_fmt(num, suffix="O"):
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
    get_irods_collection()
    ##building the dictionary
    ## get attributes
    with iRODSSession(**irods_config) as session:
        for ifolder in list_of_icollection:
            ## for every collection we get the attribute/value pair
            ## and stock them in a dictionary to use them later 
            collection= session.collections.get(ifolder)
            metadata_collection= collection.metadata.items()
            for metadata_item in metadata_collection:
                attribut=metadata_item.name
                value= metadata_item.value
                if attribut not in dico_attribute:
                    dico_attribute[attribut]=set()
                    dico_attribute[attribut].add(value)
                else :
                    dico_attribute[attribut].add(value)
            ## too many request giving error and invalid authentification
            ##will work on it later
            #list_ifile(ifolder)
                # for irods_file in ifile:
                #     obj = session.data_objects.get(irods_file)
                #     obj_metadata=obj.metadata.items()
                #     for metadata_obj in obj_metadata :
                #         obj_attr =  metadata_obj.name
                #         obj_value = metadata_obj.value
                #         if obj_attr not in dico_attribute:
                #             dico_attribute[obj_attr]=set()
                #             dico_attribute[obj_attr].add(obj_value)
                #         else:
                #             dico_attribute[obj_attr].add(obj_value)
    ## Save the dictionary in an extern text file
    file_name=os.path.expanduser(pickle_meta_dictionary_path)
    with open(file_name,"wb") as f :
        pickle.dump(dico_attribute, f)
    print(f"Dictionary have been save in {file_name}")


def read_attributes_dictionnary():
    global dico_attribute
    dico_attribute={}
    file_name=os.path.expanduser(pickle_meta_dictionary_path)
    if os.path.isfile(file_name):
        with open(file_name,"rb") as f:
            dico_attribute=pickle.load(f)
    else:
        f=open(file_name,"wb")
        f.close()


def get_user():
    ##get all the users in a instance (for exemple share folders with them)
    global list_user
    with iRODSSession(**irods_config) as session:
        #l=(list((x[User.id], x[User.name]) for x in session.query(User))) ## list username + userid
        list_user=(list(x[User.name] for x in session.query(User))) ## list username


def get_group():
    global list_group
    with iRODSSession(**irods_config) as session:
        groups = session.query(User).filter( User.type == 'rodsgroup' )
    list_group= [x[User.name] for x in groups]


def get_irods_addin_path():
    new_path_file=os.path.expanduser(pickle_additional_path_path)
    if not os.path.isfile(new_path_file):
        list_new_path=[]
        with open(new_path_file,"wb") as f:
            pickle.dump(list_new_path, f)
        print("irods list of path updated")


def copy_folder_to_irods(racine, local_folder_path, irods_destination_path,session,list_of_icollection):
    for root, dirs, files in os.walk(local_folder_path):
        ## Create the iRODS collection for the local folder if it does not exist
        relative_path = racine.split("/")[-1]+"/"+ os.path.relpath(root, local_folder_path)
        irods_collection_path = os.path.join(irods_destination_path, relative_path)
        if irods_collection_path.endswith("/."):
            irods_collection_path = irods_collection_path[:-2]
        if irods_collection_path not in list_of_icollection:
            session.collections.create(irods_collection_path)
            ## update the pickle file contining the list of collection
            update_irods_collection2("add",irods_collection_path)

        ##Copy the files from the local folder to the iRODS collection
        for file in files:
            local_file_path = os.path.join(root, file)
            irods_file_path = os.path.join(irods_collection_path, file)
            session.data_objects.put(local_file_path,irods_file_path,num_threads=nb_threads)

    ## Recursively copy the sub-folders
    for dir in dirs:
        local_subfolder_path = os.path.join(root, dir)
        irods_subfolder_path = os.path.join(irods_destination_path, relative_path, dir)
        copy_folder_to_irods(racine, local_subfolder_path, irods_subfolder_path, session, list_of_icollections)


def copy_irod_to_folder(session, irods_path, local_path, recursive=False):
    ## copy from https://github.com/Computational-Plant-Science/irods_python_client
    
    #if identify_iobject(irods_path) == "-d" :
    if session.data_objects.exists(irods_path):
        to_file_path = os.path.join(local_path, os.path.basename(irods_path))
        print(to_file_path)
        session.data_objects.get(irods_path, to_file_path)
    elif session.collections.exists(irods_path):
        if recursive:
            coll = session.collections.get(irods_path)
            local_path = os.path.join(local_path, os.path.basename(irods_path))
            if not os.path.isdir(local_path) :
                os.mkdir(local_path)

            for file_object in coll.data_objects:
                copy_irod_to_folder(session, os.path.join(irods_path, file_object.path), local_path, True)
                #print(os.path.join(irods_path, file_object.path))
                #session.data_objects.get(os.path.join(irods_path, file_object.path), local_path)
            for collection in coll.subcollections:
                copy_irod_to_folder(session, collection.path, local_path, True)
        else:
            raise FileNotFoundError("Skipping directory " + irods_path)
    else:
        raise FileNotFoundError(irods_path + " Does not exist")


def get_input(message, channel):
    response = input(message)
    channel.put(response)


def input_with_timeout(message, timeout):
    channel = queue.Queue()
    message = message + " [{} sec timeout] ".format(timeout)
    thread = threading.Thread(target=get_input, args=(message, channel))
    # by setting this as a daemon thread, python won't wait for it to complete
    thread.daemon = True
    thread.start()

    try:
        response = channel.get(True, timeout)
        return response
    except queue.Empty:
        pass
    return None


def get_recursive_folder_size(chemin_irods, session):
    # Initialisez la taille totale
    taille_totale = 0

    # Obtenez le dossier iRODS
    dossier = session.collections.get(chemin_irods)

    # Parcourez les objets à l'intérieur du dossier et ajoutez leurs tailles
    for objet in dossier.data_objects:
        taille_totale += objet.size

    # Parcourez les sous-dossiers de manière récursive et ajoutez leurs tailles
    for sous_dossier in dossier.subcollections:
        taille_totale += get_recursive_folder_size(sous_dossier.path, session)

    return taille_totale
##########################################################################################################################################################################################################################################################################################
#### called function's definition (function that will be "called" by the user/main )
##########################################################################################################################################################################################################################################################################################

def PUSH_SPEEDTEST(local_object,irods_path):
    ##test to speedtest the api version against the icommands 
    with iRODSSession(**irods_config) as session:
        temps_debut = time.time()
        session.data_objects.put(local_object,irods_path,num_threads=nb_threads)
        temps_fin = time.time()
        temps_total = temps_fin - temps_debut
    print(temps_total)




def PUSH(local_object) :
    ##send an object to irods by irsync and add meta data on it 
    ##object can be folder or file given by path
    identify_loc_object(local_object)    
    get_irods_collection()
    
    irods_path=prompt("ifolder (empty = /zone/home/user ): ",completer=icol_completer)
    if irods_path=="": 
        irods_path=f"/{irods_config['zone']}/home/{irods_config['user']}"
    with iRODSSession(**irods_config) as session:
        if is_file:
            ## the new object is a file 
            session.data_objects.put(local_object,irods_path,num_threads=nb_threads)
        else :
            ##the new object is a folder
            copy_folder_to_irods(local_object,local_object,irods_path,session,list_of_icollection)

    ask_add_meta=input_with_timeout("add metadata ?(y/n): ",10)
    time.sleep(3)
    ## get new iobject
    if local_object[-1] == "/": #if a folder is given with the / in the end we remove it 
        local_object=local_object[:-1]
    if "/" in local_object: ##when path (path/to/object) given we keep only the end as in irods 
        local_object=(local_object.split("/"))[-1] ## the new path will be irods_path/object
    new_iobject=(f"{irods_path}/{local_object}").replace("//", "/") 
    
    ##add meta 
    if ask_add_meta == "y" or ask_add_meta == "Y" or ask_add_meta == "yes" or ask_add_meta == "YES" or ask_add_meta == "Yes":
        ADD_META(new_iobject)


def PULL(type_iobject,local_path) :
    ##get back an object from irods and copy it on local folder or on a given path
    call_iobject(type_iobject)
    if not local_path :
        local_collection()
        local_path=prompt("local folder :",completer=folder_completer)
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    ## we want to download a file
    with iRODSSession(**irods_config) as session:
        if type_iobject == "-f" :
            ## we want to download all the file containing a patern (e.g *.md5)
            if "*" in iobject  or "%" in iobject :
                print("not working yet --> download one by one or download the collection")
            else:
            ## we want this exact file
                session.data_objects.get(iobject,local_path)
        #we want to download a folder
        else:
            copy_irod_to_folder(session,iobject,local_path, recursive=True)


def ADD_META(iobject):
    ##loop to add meta data to a given object on irods that can be collection(folder), DataObject(file) or user
    read_attributes_dictionnary() ##if you don't want to have autocompletion on this command comment this
    change=False
    list_value=[]
    list_key=[]

    ## is my iobject a file in irods or a folder 
    identify_iobject(iobject)
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
        if attribut in dico_attribute.keys():    
            value_completer=WordCompleter(dico_attribute[attribut])
            value=prompt("value : ",completer=value_completer)
        else :
            value=input("value : ")
        unit=input("unit : ")

        ## iobject is a file in irods 
        with iRODSSession(**irods_config) as session:
            if is_ifile :
                obj=session.data_objects.get(iobject)
            ## iobject is a folder
            else :
                obj=session.collections.get(iobject)
            obj.metadata.add(attribut,value,unit)

        if attribut not in dico_attribute:
            dico_attribute[attribut]=set()
            dico_attribute[attribut].add(value)
            change=True
        else:
            if value not in dico_attribute[attribut]:
                dico_attribute[attribut].add(value)
                change=True
    
    ###UPDATE dictionary file
    if change == True :
        file_name=os.path.expanduser(pickle_meta_dictionary_path)
        with open(file_name,"wb") as f :
            pickle.dump(dico_attribute, f)
        print(f"Dictionary have been update in {file_name}")


def IRM_META(iobject):
    ##easy way of removing metadata from a object (remove all, one attribut)
    identify_iobject(iobject)
    with iRODSSession(**irods_config) as session:
        if is_ifile :
            obj=session.data_objects.get(iobject)
            ## iobject is a folder
        else :
            obj=session.collections.get(iobject)
        metadata=obj.metadata.items()
        attribut=input("attribut (empty to stop, * for all) : ")
        if attribut == "":
            sys.exit()
        if attribut != "*":
            value=input("value : ")
            unit=input("unit : ")
        if attribut != "*":
            obj.metadata.remove(attribut,value,unit)
        else :
            for avu in obj.metadata.items():
                obj.metadata.remove(avu)


def IMKDIR(mkdir):
    ##easy way for creating an irods collection helped with autocompletion if you don't know the exact tree view
    
    with iRODSSession(**irods_config) as session:
        session.collections.create(mkdir, recurse=True)
    update_irods_collection2("add",mkdir)


def IRM(type_iobject,iobject):
    ##easy way for deleting an object on irods helped with autocompletion. 
    ##can be collection(folder) or one/multiple Data_Object(file)
    with iRODSSession(**irods_config) as session:
        if type_iobject == "-C":
            session.collections.remove(iobject,recurse=True, force=True)
            update_irods_collection2("remove", iobject)
        else:
            session.data_objects.unlink(iobject, force=True)
    

def SHOW_META(iobject):
    ##easy way for showing the meta data associate with an irods object helped with autocompletion
    ##can be collection(folder), Data_Object(file) or user
    identify_iobject(iobject)
    meta_result=""
    with iRODSSession(**irods_config) as session:
        if is_ifile:
            obj = session.data_objects.get(iobject)
        else :
            obj = session.collections.get(iobject)
        metadata=obj.metadata.items()

        for attribut, value in metadata:
            print(f"attribut : {attribut}\tvalue : {value}")
            meta_result= meta_result + f"attribut : {attribut}\tvalue : {value}\n"
    
    return meta_result


def SEARCH_BY_META(type_iobject=None):
    ##Search for an object(s) in irods by query the metadata associate with it/them
    ##The attributes exiting in irods are save in a dictionary as key with the (metadata)
    ##values associate with this attribute as (dictionary) values
    ##so the user can't ask for nonexistent attribut/values
    print("not working yet sorry ! ")
    sys.exit()
    read_attributes_dictionnary()
    ##building the query
    list_operation=["=","like","\'>\'","\'<\'"]
    list_liaison=["","and",'or']
    liaison="placeholder"
    result= set()
    build_cmd_C=""
    build_cmd_F=""
    
    while liaison != "" :
        qu_attribute_completer=WordCompleter(dico_attribute.keys)
        qu_attribute=prompt("attribute: ",completer=qu_attribute_completer)
        qu_value_completer=WordCompleter(dico_attribute[qu_attribute])
        qu_value=prompt("value (* for all): ",completer=qu_value_completer).replace("*","%")
        operation_completer=WordCompleter(list_operation)
        operation=prompt("operation (like if your value contain *): ",completer=operation_completer)
        liaison_completer=WordCompleter(list_liaison)
        liaison=prompt("liaison (empty to stop): ",completer=liaison_completer)
        if not type_iobject:
            build_cmd_C = build_cmd_C + f"CollectionMeta.name == '{qu_attribute}' and CollectionMeta.value == '{qu_value}' {liaison} "
            build_cmd_F = build_cmd_F + f"DataObjectMeta.name == '{qu_attribute}' and DataObjectMeta.value == '{qu_value}' {liaison} "
        elif type_iobject == "-C":
            build_cmd_C = build_cmd_C + f"CollectionMeta.name == '{qu_attribute}' and CollectionMeta.value == '{qu_value}' {liaison} "
        else :
            build_cmd_F = build_cmd_F + f"DataObjectMeta.name == '{qu_attribute}' and DataObjectMeta.value == '{qu_value}' {liaison} "
    with iRODSSession(**irods_config) as session:
        if build_cmd_F != "":
            cmd_F = session.query(Collection.name,DataObject.name).filter(build_cmd_F)
            print(cmd_F)
            for result_F in cmd_F:
                result.add(f"{result_F[Collection.name]}/{result_F[DataObject.name]}")
        if build_cmd_C != "":
            cmd_C = session.query(Collection.name).filter(build_cmd_C)
            for result_C in cmd_C:
                result.add(result_C[Collection.name])
    
    for i in sorted(result):
        print(i)        
    return sorted(result)



def SEARCH_BY_NAME(tofind,type_iobject=None):
    ##search a file (like ilocate) or a folder store in the irods vault 
    result= set()
    tofind="%"+tofind.replace("*","%")+"%"
    tofind.replace("%%","%")
    with iRODSSession(**irods_config) as session:
        if not type_iobject :
            #list folder and file corresponding to the query
            #list collection
            results_C = session.query(Collection.name).filter(Criterion("like", Collection.name, tofind))
            ## list file
            results_F = session.query(Collection.name,DataObject.name).filter(Criterion("like", DataObject.name, tofind))
            for result_C in results_C:
                result.add(result_C[Collection.name])
            for result_F in results_F:
                result.add(f"{result_F[Collection.name]}/{result_F[DataObject.name]}")
        if type_iobject == "-C":
            results_C = session.query(Collection.name).filter(Criterion("like", Collection.name, tofind))
            for result_C in results_C:
                result.add(result_C[Collection.name])
        if type_iobject == "-f":
            results_F = session.query(Collection.name,DataObject.name).filter(Criterion("like", DataObject.name, tofind))
            for result_F in results_F:
                result.add(f"{result_F[Collection.name]}/{result_F[DataObject.name]}")
    toprint=""
    for i in sorted(result):
        print(i)
        toprint=toprint + i + "\n"

    return toprint
    

def IDUSH(irods_path):
    ##equivalent of the unix du -sh but on irods
    ##get the size (in bites) of all the file containing in a folder, add them and convert to human readable 
    if irods_path=="": 
        irods_path=f"/{irods_config['zone']}/home/{irods_config['user']}"
    with iRODSSession(**irods_config) as session:
        print(sizeof_fmt(get_recursive_folder_size(irods_path,session)))
        size=sizeof_fmt(get_recursive_folder_size(irods_path,session))
        
    return size


def ICHMOD(iobject):
    ## allow to add right to other user/group on your irods collection/object
    first_choice=["group","user"]
    list_right=["read","write","own","remove/null"]
    group_or_user_completer=WordCompleter(first_choice)
    group_or_user=prompt("group or user : ",completer=group_or_user_completer)
    if group_or_user == "group" :
        get_group()
        list_receiver=list_group
    elif group_or_user == "user" :
        get_user()
        list_receiver=list_user
    else :
        ICHMOD(iobject)
    
    receiver_completer=WordCompleter(list_receiver)
    receiver=prompt("give acces to : ",completer=receiver_completer)
    right_completer=WordCompleter(list_right)
    right=prompt("which right : ",completer=right_completer)
    if right == "remove/null" :
        right="null"
    
    identify_iobject(iobject)
    with iRODSSession(**irods_config) as session:
        if is_ifile:
            session.acls.set(iRODSAccess(right,iobject,receiver),recursive=False)
        else :
            session.acls.set(iRODSAccess(right,iobject,receiver),recursive=True)


def ADD_ADDITIONAL_PATH():
    ## Add additional path to the autocompletion (e.g someone give you right on collection not in your zone/home/user )
    new_path_file=os.path.expanduser(pickle_additional_path_path)
    if os.path.isfile(new_path_file):
        with open(new_path_file,"rb") as f:
            list_new_path=pickle.load(f)
    else :
        list_new_path=[]
    new_path=input("give a new IRODS PATH (empty to stop) : ")
    if new_path == "":
        sys.exit()
    else:
        if new_path not in list_new_path:
            list_new_path.append(new_path)
        with open(new_path_file,"wb") as f:
            pickle.dump(list_new_path, f)
        print("irods list of path updated")
        print(f"updating the irods collection pickle with new collection from {new_path}")
        update_irods_collection2("add", new_path)

        ADD_ADDITIONAL_PATH()


def RM_ADDITIONAL_PATH():
    ##remove additional path you don't need anymore
    new_path_file=os.path.expanduser(pickle_additional_path_path)
    if os.path.isfile(new_path_file):
        with open(new_path_file,"rb") as f:
            list_new_path=pickle.load(f)
        
        list_path_completer=WordCompleter(list_new_path)
        to_remove=prompt("which to remove (empty to stop):",completer=list_path_completer)
        if to_remove == "":
            sys.exit()
        list_new_path.remove(to_remove)
        
        with open(new_path_file,"wb") as f:
            pickle.dump(list_new_path, f)
        print("irods list of path updated")
        update_irods_collection2("remove", to_remove)

        RM_ADDITIONAL_PATH()
    else:
        print("there is no additional path to remove")   

def EDITIONARY():
    action_list=["ADD","EDIT","REMOVE"]
    read_attributes_dictionnary()
    attribute_completer=WordCompleter(read_attribute_dictionnary.keys())
    attribute=prompt("choose a attribute or create a new one : ",completer=attribute_completer)
    action_completer=WordCompleter(action_list)
    action=prompt("action (add/edit/rm) : ",completer=action_completer)


##########################################################################################################################################################################################################################################################################################
#### if __name__ == "__main__" 
##########################################################################################################################################################################################################################################################################################

if __name__ == "__main__":
    main()