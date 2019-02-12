#!/usr/bin/env bash
#
# display Bash Completion
# =======================
#
# Bash completion support for [display](https://digsim.is-a-geek.com/rhode).
#
# The script is inspired by the Syncany bash completion script
# available at [3]
#
# Installation
# ------------
#
# 1. Place it in a `bash-completion.d` folder:
#
#   * /etc/bash-completion.d
#   * /usr/local/etc/bash-completion.d
#   * ~/bash-completion.d
#
# 2. Open new bash, and type `display [TAB][TAB]`
#
# Documentation
# -------------
# The script is called by bash whenever [TAB] or [TAB][TAB] is pressed after
# 'sy (..)'. By reading entered command line parameters, it determines possible
# bash completions and writes them to the COMPREPLY variable. Bash then
# completes the user input if only one entry is listed in the variable or
# shows the options if more than one is listed in COMPREPLY.
#
# The script first determines the current parameter ($cur), the previous
# parameter ($prev), the first word ($firstword) and the last word ($lastword).
# Using the $firstword variable (= the command) and a giant switch/case,
# completions are written to $complete_words and $complete_options.
#
# If the current user input ($cur) starts with '-', only $command_options are
# displayed/completed, otherwise only $command_words.
#
# References
# ----------
# [1] http://stackoverflow.com/a/12495480/1440785
# [2] http://tiswww.case.edu/php/chet/bash/FAQ
# [3] https://github.com/syncany/syncany/blob/7a15d5f17e1a894de97f05389aaa133d7c0acd95/gradle/bash/syncany.bash-completion

shopt -s progcomp

_displayCalendar()
{
    local cur prev firstword lastword complete_words complete_options

    # Don't break words at : and =, see [1] and [2]
	COMP_WORDBREAKS=${COMP_WORDBREAKS//[:=]}
    # COMP_WORDS is an array of words in the current command line.
    # COMP_CWORD is the index of the current word (the one the cursor is
    # in). So COMP_WORDS[COMP_CWORD] is the current word; we also record
    # the previous word here, although this specific script doesn't
    # use it yet.
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    firstword=$(_sy_get_firstword)
	lastword=$(_sy_get_lastword)

    GLOBAL_COMMANDS="display"
    GLOBAL_OPTIONS="-h -v"
    SYNC_OPTS="\
		-s --start-date\
		-e --end-date\
		   --clear\
		   --no-clear"


    case "${firstword}" in
        sync)
            case "${prev}" in
                --start-date|-s|--end-date|-e)
                    complete_words=`date +%Y%m%d`
                    ;;
                *)
                    complete_options=${SYNC_OPTS}
                    complete_words=${SYNC_OPTS}
                    ;;
            esac
            ;;
        *)
            complete_words="$GLOBAL_COMMANDS"
			complete_options="$GLOBAL_OPTIONS"
			;;
    esac

    # Either display words or options, depending on the user input
	if [[ $cur == -* ]]; then
	    # Only perform completion if the current word starts with a dash ('-'),
		COMPREPLY=( $( compgen -W "$complete_options" -- $cur ))
	else
		COMPREPLY=( $( compgen -W "$complete_words" -- $cur ))
	fi

	return 0
}

# Determines the first non-option word of the command line. This
# is usually the command
_sy_get_firstword() {
	local firstword i

	firstword=
	for ((i = 1; i < ${#COMP_WORDS[@]}; ++i)); do
		if [[ ${COMP_WORDS[i]} != -* ]]; then
			firstword=${COMP_WORDS[i]}
			break
		fi
	done

	echo $firstword
}

# Determines the last non-option word of the command line. This
# is usally a sub-command
_sy_get_lastword() {
	local lastword i

	lastword=
	for ((i = 1; i < ${#COMP_WORDS[@]}; ++i)); do
		if [[ ${COMP_WORDS[i]} != -* ]] && [[ -n ${COMP_WORDS[i]} ]] && [[ ${COMP_WORDS[i]} != $cur ]]; then
			lastword=${COMP_WORDS[i]}
		fi
	done

	echo $lastword
}


complete -F _displayCalendar displayCalendar