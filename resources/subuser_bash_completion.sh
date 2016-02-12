#
#  List the images contained in a repository.
#
_subuser_get_images_from_repo()
{
    subuser list available | grep "@$1$"
}


#
#  List all available subuser images.
#
_subuser_get_images()
{
    subuser list available
}


#
#  List all the subusers created.
#
_subuser_get_subusers()
{
    subuser list subusers
}

#
#  List all the added repositories.
#
_subuser_get_repositories()
{
    subuser list repositories
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
    opts="describe list pkg print-dependency-info remove-old-images"
    opts="$opts repair repository registry run subuser test update version"

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
                    opts=`_subuser_get_subusers`
                    ;;

                *)
                    opts="image subuser"
                    ;;
            esac
            ;;

        #
        #  Complete the "list" command
        #
        list)
            opts="available installed-images repositories subusers"

            case "${COMP_WORDS[2]}" in
                available)
                    opts="--broken --internal --long"
                    ;;

                installed-images)
                    opts="--broken --internal --long"
                    ;;

                repositories)
                    opts="--broken --internal --long"
                    ;;

                subusers)
                    opts="--broken --internal --long"
                    ;;

                *)
                    ;;
            esac
            ;;

        #
        #  Complete the "pkg" command
        #
        pkg)
            opts="add init test"

            # If current word starts with "-", autocomplete with options
            if [[ "$cur" == -* ]];then
                opts="--accept --build-context= --image-file= --image-sources-dir= --prompt"
            else
                case "${COMP_WORDS[2]}" in
                    add)
                        # Complete with directories and exit
                        COMPREPLY=($(compgen -d -- ${cur}))

                        return 0
                        ;;

                    init)
                        ;;

                    test)
                        # Complete with directories and exit
                        COMPREPLY=($(compgen -d -- ${cur}))

                        return 0
                        ;;
                esac
            fi
            ;;

        #
        #  Complete the "print-dependency-info" command
        #
        print-dependency-info)
            opts=`_subuser_get_images`
            ;;

        #
        #  Complete the "registry" command
        #
        registry)
            opts="livelog log rollback"

            # If current word starts with "-", autocomplete with options
            if [[ "$cur" == -* ]];then
                opts="--json"
            else
                case "${COMP_WORDS[2]}" in
                    livelog)
                    ;;

                    log)
                    ;;

                    rollback)
                    ;;
                esac
            fi
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
            opts=`_subuser_get_subusers`

            # If current word starts with "-", autocomplete with options
            if [[ "$cur" == -* ]];then
                opts="--accept --prompt"
            fi
            ;;

        #
        #  Complete the "repository" command
        #
        repository)
            case "${COMP_WORDS[2]}" in
                add)
                    # Complete with directories and exit
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
            opts=`_subuser_get_subusers`
            ;;

        #
        #  Complete the "subuser" command
        #
        subuser)
            # If current word starts with "-", autocomplete with options
            if [[ "$cur" == -* ]];then
                opts="--accept --prefix= --prompt"
            else
                case "${COMP_WORDS[2]}" in
                    add)
                        opts=`_subuser_get_subusers`
                        ;;

                    add-to-path)
                        opts=`_subuser_get_subusers`
                        ;;

                    edit-permissions)
                        opts=`_subuser_get_subusers`
                        ;;

		    expose-entrypoints)
                        opts=`_subuser_get_subusers`
                        ;;

		    hide-entrypoints)
                        opts=`_subuser_get_subusers`
                        ;;

                    remove)
                        opts=`_subuser_get_subusers`
                        ;;

                    remove-from-path)
                        opts=`_subuser_get_subusers`
                        ;;

                    run)
                        opts=`_subuser_get_subusers`
                        ;;

                    *)
                        opts="add add-to-path edit-permissions expose-entrypoints hide-entrypoints remove remove-from-path run"
                esac
            fi
            ;;

        #
        #  Test doesn't take parameters
        #
        test)
            ;;

        #
        #  Complete the "test-images" command
        #
        update)
            # If current word starts with "-", autocomplete with options
            if [[ "$cur" == -* ]];then
                opts="--accept --prompt"
            else
                case "${COMP_WORDS[2]}" in
                    all)
                    ;;

                    lock-subuser-to)
                        opts=`_subuser_get_subusers`
                        ;;

                    log)
                        ;;

                    rollback)
                        ;;

                    subusers)
                        opts=`_subuser_get_subusers`
                        ;;

                    unlock-subuser)
                        opts=`_subuser_get_subusers`
                        ;;

                    *)
                        opts="all lock-subuser-to log rollback subusers unlock-subuser"
                esac
            fi
            ;;

        #
        #  Version can only take a parameter
        #
        version)
            opts="--json"
            ;;
    esac

    #
    #  Complete the command section
    #
    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))

    return 0
}

complete -F _subuser_bash_completion subuser
