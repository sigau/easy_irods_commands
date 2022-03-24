#/usr/bin/env bash

_easicmd_completion()
{
    local opts
    opts="add_meta add_path build_dico_meta help ichmod idush imkdir irm pull push rm_meta search_by_meta search_name show_meta synchro"
    case $COMP_CWORD in
        1)
            COMPREPLY=( $(compgen -W "${opts}" -- "${COMP_WORDS[COMP_CWORD]}") )
            ;;
        *)
            COMPREPLY=( $(compgen -o default -- "${COMP_WORDS[COMP_CWORD]}") )
            ;;
    esac
    return 0
}

complete -F _easicmd_completion ./easicmd.py
complete -F _easicmd_completion easicmd.py