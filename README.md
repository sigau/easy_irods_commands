# easicmd
## Short description
easicmd is a python script written to facilitate/automate the use of irods for new users and add the autocompletion for some irods commands by using prompt_toolkit module.

## Dependancies
- python 3.6 for the f-string (the script can be rewritten fo older version of python by replacing f-string by str.format()) 
- [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/en/master/) (the script install it the first time your run it if it's not already install)

## Commands
```
Possible COMMANDS :

	add_meta	: add_meta or add_meta [irods path]
		  if you don't give an irods path you'll be ask an option ([f] for file or [C] for a folder) then you will have to chose your object help by autocompletion

	help	: print this help and leave
	idush	: equivalent to du -sh for an irods folder

	imkdir	 : imkdir -p reinforce by auto completion

	irm	: irm [option]
		 option are [-f] for a file and [-C] for a folder 
		 allow to irm one or multiple (if * used) folder/file in irods. You don't need to know the path in irods as it will be helped by autocompletion

	pull	: pull [option] [local path]
		  irsync/iget folder/file from irods to local with auto completion
		  For a file add option -f
		  For a folder add option -C
		  path can be full path or '.' for current folder
		  if no path given, a list of all the folder from root will be proposed (can be very long if you have many)

	push	: irsync/iput folder/file (given by a path) from local to irods with auto completion

	rm_meta	: rm_meta or rm_meta [irods path]
		  if you don't give an irods path you'll be ask an option ([f] for file or [C] for a folder) then you will have to chose your object help by autocompletion

	search_by_meta	: search_by_meta [option] or search_by_meta
		 option are [-f] for a file, [-C] for a folder and [-u] for a user

	search_name	: search_name [option]
		 option are [-f] for a file and [-C] for a folder 
		 search for a file or a folder in irods

	show_meta	: show_meta [option] or show_meta
		 option are [-f] for a file and [-C] for a folder
 
	synchro	: synchro [local path to folder]
		 synchronise the contain of a local folder with irods based on the sha256
		 the folder will be synchronise on /zone/home/user/  
		 can be fully automated with the help of when-changed (https://github.com/joh/when-changed) with : when-changed -r -q [folder] -c 'easicmd.py synchro [folder]'
```

## AUTOCOMPLETION
As it is IRODS doesn't allow the autocompletion by using tab for data on irods (kind of with *i-commands-auto.bash* see in useful_stuff). The python module *prompt_toolkitC allow us to add some kind of autocompletion when it come to choosing data on irods. 
When you will have to select a data from irods a list where you can navigate by using TAB or direction keys will be displayed on your screen :
![screenshot/example_1.png](screenshot/example_1.png)

## Examples 
**To simplify when we talk about irods file it refer to data_object and irods folder to collection.**
### PUSH : PUT LOCAL DATA ON IRODS
To put a data (file or folder) on irods you just have to give a path to the data. Then you will be asked where in irods you want to put it. 
When you use **push** to upload data the sha256 is calculated and stock in the icat (option -K in iput).
After "pushing" your data on irods you will be asked if you want to add metadata to your new irods object.

```
### PUT THE LOCAL FOLDER "PROJECT_1" IN THE IRODS FOLDER "MY_PROJECT" AND ADD METADATA
$ ./easicmd.py push PROJECT_1
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/MY_PROJECT                             
                               /lbbeZone/home/gdebaecker/irods_test                                   
                               /lbbeZone/home/gdebaecker/irods_test/raw_data                          
                               /lbbeZone/home/gdebaecker/irods_test/raw_data/fast5                    
                               /lbbeZone/home/gdebaecker/MY_PROJECT                                                        
                               /lbbeZone/home/gdebaecker/NeGa                                         
                  
Running recursive pre-scan... pre-scan complete... transferring data...
C- /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_1:
0/2 -  0.00% of files done   0.000/0.000 MB -  0.00% of file sizes done
Processing file.fastq - 0.000 MB   2021-11-03.17:06:50
   file.fastq                      0.000 MB | 0.047 sec | 0 thr |  0.000 MB/s
1/2 - 50.00% of files done   0.000/0.000 MB -  0.00% of file sizes done
Processing file.fasta - 0.000 MB   2021-11-03.17:06:50
   file.fasta                      0.000 MB | 0.041 sec | 0 thr |  0.000 MB/s

add metadata ?(y/n): y
attribut (empty to stop) : client
value : MISTER_X
unit : Top_Secret
                       
$ ils -r MY_PROJECT
/lbbeZone/home/gdebaecker/MY_PROJECT:
  C- /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_1
/lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_1:
  file.fasta
  file.fastq

```
### PULL : GET BACK DATA FROM IRODS 
To get back data from irods you have to give **a type ( [-f] for a file and [-C] for a folder )** and the **local path** where you want to download the data. 
If you don't give a path the script will scan all your local data from the root-folder and ask you where you want to put it (it can take some time if you have many folder).
```
### PUT THE IRODS FOLDER "PROJECT_2" IN THE LOCAL FOLDER "MY_LOCAL_PROJECT"
$ ./easicmd.py pull -C MY_LOCAL_PROJECT/
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_2                           
                               /lbbeZone/home/gdebaecker/irods_test                                   
                               /lbbeZone/home/gdebaecker/irods_test/raw_data                          
                               /lbbeZone/home/gdebaecker/irods_test/raw_data/fast5                    
                               /lbbeZone/home/gdebaecker/MY_PROJECT                                   
                               /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_2                         
                               /lbbeZone/home/gdebaecker/NeGa                                         
                  
0/3 -  0.00% of files done   0.000/0.000 MB -  0.00% of file sizes done
Processing file_bis.r - 0.000 MB   2021-11-03.17:35:48
   file_bis.r                      0.000 MB | 0.036 sec | 0 thr |  0.000 MB/s
1/3 - 33.33% of files done   0.000/0.000 MB -  0.00% of file sizes done
Processing file.fasta - 0.000 MB   2021-11-03.17:35:48
   file.fasta                      0.000 MB | 0.029 sec | 0 thr |  0.000 MB/s
2/3 - 66.67% of files done   0.000/0.000 MB -  0.00% of file sizes done
Processing file.fastq - 0.000 MB   2021-11-03.17:35:48
   file.fastq                      0.000 MB | 0.027 sec | 0 thr |  0.000 MB/s

$ls MY_LOCAL_PROJECT
PROJECT_2/

### PUT THE CONTAIN OF IRODS FOLDER "PROJECT_2" IN THE LOCAL FOLDER "MY_LOCAL_PROJECT"
$ ./easicmd.py pull -C MY_LOCAL_PROJECT/
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_2
irods file (tap tab) : %
   file_bis.r                      0.000 MB | 0.037 sec | 0 thr |  0.000 MB/s
   file.fasta                      0.000 MB | 0.030 sec | 0 thr |  0.000 MB/s
   file.fastq                      0.000 MB | 0.035 sec | 0 thr |  0.000 MB/s

$ls MY_LOCAL_PROJECT
file_bis.r  file.fasta  file.fastq

### DOWNLOAD ONE SPECIFIC FAST5 IRODS FILE IN MY CURRENT LOCAL FOLDER
$./easicmd.py pull -f .
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/irods_test/raw_data/fast5
irods file (tap tab) :FAL56006_29db37dd_251.fast5
0/1 -  0.00% of files done   0.000/181.788 MB -  0.00% of file sizes done
Processing FAL56006_29db37dd_251.fast5 - 181.788 MB   2021-11-03.17:42:38
From server: NumThreads=46, addr:lbbe-irods-local, port:20099, cookie=549953450
FAL56006_29db37dd_251.fast5 - 169.932/181.788 MB - 93.48% done   2021-11-03.17:42:38
FAL56006_29db37dd_251.fast5 - 181.788/181.788 MB - 100.00% done   2021-11-03.17:42:38
   FAL56006_29db37dd_251.fas     181.788 MB | 1.709 sec | 46 thr | 106.344 MB/s

$ls FAL56006_29db37dd_251.fast5
FAL56006_29db37dd_251.fast5
```
### SYNCHRO : SYNCHRONISE MODIFIED DATA FROM A LOCAL FOLDER WITH IRODS

```

```

### IMKDIR : CREATE AN IRODS WITHOUT KNOWING THE FULL TREE VIEW

```

```

### IRM : REMOVE DATA FROM IRODS
When you no longer need a data on irods or you need to make some place you can remove them by using *irm*. This command take as argument the type of the irods data you want to remove and then with the autocompletion you can choose which data you want to remove. You can use "*" to remove several irods objects.

```
### REMOVE ALL THE ".r" file from the "MY_project" irods folder
$ ils ./MY_PROJECT/
/lbbeZone/home/gdebaecker/MY_PROJECT:
  file_bis_2.r
  file_bis_3.r
  file_bis_4.r
  file_bis_5.r
  file_bis.r
  file.fasta
  file.fastq
  C- /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_2

./easicmd.py irm -f
you can use * as wildcard
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/MY_PROJECT
irods file (tap tab) :*.r

$ ils ./MY_PROJECT/
/lbbeZone/home/gdebaecker/MY_PROJECT:
  file.fasta
  file.fastq
  C- /lbbeZone/home/gdebaecker/MY_PROJECT/PROJECT_2

REMOVE THE "MY_PROJECT" irods folder
$ ils
/lbbeZone/home/gdebaecker:
  C- /lbbeZone/home/gdebaecker/irods_test
  C- /lbbeZone/home/gdebaecker/MY_PROJECT
  C- /lbbeZone/home/gdebaecker/NeGa
  C- /lbbeZone/home/gdebaecker/sr_aselus

$ ./easicmd.py irm -C
you can use * as wildcard
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/MY_PROJECT

$ ils
/lbbeZone/home/gdebaecker:
  C- /lbbeZone/home/gdebaecker/irods_test
  C- /lbbeZone/home/gdebaecker/NeGa
  C- /lbbeZone/home/gdebaecker/sr_aselus
```

### ADD_META : ADD METADATA ASSOCIATED WITH AN OBJECT ON IRODS

```

```

### RM_META : REMOVING METADATA ASSOCIATED WITH AN OBJECT ON IRODS

```

```

### SHOW_META : SHOW ALL THE METADATA ASSOCIATED WITH AN OBJECT ON IRODS

```

```

### SEARCH_BY_META : SEARCH FOR IRODS OBJECTS (FOLDER/FILE) BASED ON THE METADATA

```

```

### SEARCH_NAME : SEARCH FOR IRODS OBJECT BASED ON (PARTS) OF THE OBJECT NAME

```

```

### IDUSH : AN IRODS EQUIVALENT TO du -sh  
If you want to know the size of a folder on irods you can use idush. It make the sum of the size of all the irods files inside an irods folder and print it. If you don't known if you will have enough place on your disk before the download you can verify it with idush.

```
$ ./easicmd.py idush
ifolder (empty = /zone/home/user ): /lbbeZone/home/gdebaecker/irods_test/raw_data/fast5                               
                               /lbbeZone/home/gdebaecker/irods_test                                   
                               /lbbeZone/home/gdebaecker/irods_test/raw_data                          
                               /lbbeZone/home/gdebaecker/irods_test/raw_data/fast5                    

913.7MiB

```


## To-Do List
- [x] 
- [ ] 
- [ ] 