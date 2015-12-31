#
#  Extract the available images in a given directory.
#  Works just by taking the existing directory list.
#
_subuser_get_images_from_dirs()
{
    local _TMP_=$IFS
    IFS=$'\n'
    for dir in $1;do
        find "$dir" -maxdepth 1 -type d -exec basename {} \;|grep -v '.git'|sort
    done
    IFS=$_TMP_
}


#
#  Extract the images contained in a repository.
#  The 'default' one path is known, others are taken fron the registry.
#
_subuser_get_images_from_repo()
{
    local repo_dir

    if [ "$1" == "default" ];then
        repo_dir="$HOME/.subuser/repositories/default/"
    else
        repo_dir=`grep "^ \"$1\": {" ~/.subuser/registry/repositories.json -A2 |
            tr -d '\n' |
            sed -r 's/.* "source-dir": "(.*)"/\1/g'`
    fi

    _subuser_get_images_from_dirs "$repo_dir"
}


#
#  Find all available subuser images.
#  Look in the default repository and the ones listed in the registry.
#
_subuser_get_images()
{
    local from_registry
    from_registry=`grep '^  "source-dir": "' ~/.subuser/registry/repositories.json |
                   sed -r 's/^  "source-dir": "(.*)"/\1/g'`

    _subuser_get_images_from_dirs "$HOME/.subuser/repositories/default/"$'\n'"$from_registry"
}


#
#  List all the subusers created.
#  Works by simpistic parsing of the registry.
#
_subuser_get_subusers()
{
    grep '^ "' ~/.subuser/registry/subusers.json |sed -r 's/^ "(.*)": \{/\1/g'
}


#
#  List all subusers, excluding the system ones.
#
_subuser_get_user_subusers()
{
    _subuser_get_subusers | grep -v '^!'
}


#
#  List all the shortcuts created by subuser.
#
_subuser_get_shortcuts()
{
    find ~/.subuser/bin/  -maxdepth 1 -type f -exec basename {} \;
}


#
#  List all the added repositories.
#  The default one is included, others are parsed from the registry.
#
_subuser_get_repositories()
{
    (echo default
     grep '^ "' ~/.subuser/registry/repositories.json |
        sed -r 's/^ "(.*)": \{/\1/g')
}


#
#  Subuser bash completion main function.
#
_subuser_bash_completion()
{
    local cur command opts
    COMPREPLY=()

    cur="${COMP_WORDS[COMP_CWORD]}"
    command="${COMP_WORDS[1]}"

    #
    #  The basic options we'll complete.
    #
    opts="describe dry-run list print-dependency-info remove-old-images"
    opts="$opts repair repository run subuser test test-images update"

    #
    #  Complete the arguments of the commands.
    #  This is done modifying the "opts" variable to show the available choices.
    #
    case "${command}" in
        #
        #  Complete the "describe" command
        #
        describe)
            case "${COMP_WORDS[2]}" in
                image)
                    opts=`_subuser_get_images`
                    ;;

                subuser)
                    opts=`_subuser_get_user_subusers`
                    ;;

                *)
                    opts="image subuser"
                    ;;
            esac
            ;;

        #
        #  Complete the "dry-run" command
        #
        dry-run)
            opts=`_subuser_get_user_subusers`
            ;;

        #
        #  Complete the "list" command
        #
        list)
            opts="available installed-images repositories subusers"

            case "${COMP_WORDS[2]}" in
                available)
                    opts="--broken --internal --short"
                    ;;

                installed-images)
                    opts="--broken --internal --short"
                    ;;

                repositories)
                    opts="--broken --internal --short"
                    ;;

                subusers)
                    opts="--broken --internal --short"
                    ;;

                *)
                    ;;
            esac
            ;;

        #
        #  Complete the "print-dependency-info" command
        #
        print-dependency-info)
            opts=`_subuser_get_images`
            ;;

        #
        #  Complete the "remove-old-images" command
        #
        remove-old-images)
            opts="--dry-run --repo="
            ;;

        #
        #  Complete the "repair" command
        #
        repair)
            opts=`_subuser_get_user_subusers`
            ;;

        #
        #  Complete the "repository" command
        #
        repository)
            case "${COMP_WORDS[2]}" in
                add)
                    COMPREPLY=($(compgen -d -- ${cur}))

                    return 0
                    ;;

                remove)
                    opts=`_subuser_get_repositories`
                    ;;

                *)
                    opts="add remove"
            esac
            ;;

        #
        #  Complete the "run" command
        #
        run)
            opts=`_subuser_get_user_subusers`
            ;;

        #
        #  Complete the "subuser" command
        #
        subuser)
            case "${COMP_WORDS[2]}" in
                add)
                    opts=`_subuser_get_user_subusers`
                    ;;

                create-shortcut)
                    opts=`_subuser_get_user_subusers`
                    ;;

                edit-permissions)
                    opts=`_subuser_get_user_subusers`
                    ;;

                remove)
                    opts=`_subuser_get_user_subusers`
                    ;;

                remove-shortcut)
                    opts=`_subuser_get_shortcuts`
                    ;;

                run)
                    opts=`_subuser_get_user_subusers`
                    ;;

                *)
                    opts="add create-shortcut edit-permissions remove remove-shortcut run"
            esac
            ;;

        #
        #  Test doesn't take parameters
        #
        test)
            ;;

        #
        #  Complete the "test-images" command
        #
        test-images)
            if [ "$COMP_CWORD" -eq 2 ];then
                opts=`_subuser_get_repositories`
            else
                opts=`_subuser_get_images_from_repo "${COMP_WORDS[2]}"`
            fi
            ;;

        #
        #  Complete the "test-images" command
        #
        update)
            case "${COMP_WORDS[2]}" in
                all)
                ;;

                lock-subuser-to)
                    opts=`_subuser_get_user_subusers`
                    ;;

                log)
                ;;

                rollback)
                ;;

                subusers)
                ;;

                unlock-subuser)
                    opts=`_subuser_get_user_subusers`
                    ;;

                *)
                    opts="all lock-subuser-to log rollback subusers unlock-subuser"
            esac
    esac

    #
    #  Complete the command section
    #
    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))

    return 0
}

complete -F _subuser_bash_completion subuser
