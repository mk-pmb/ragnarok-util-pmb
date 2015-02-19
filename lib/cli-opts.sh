#!/bin/bash
# -*- coding: utf-8, tab-width: 2 -*-


function dbgp () {
  local MIN_LVL="$1"; shift
  [ "${DEBUGLEVEL:-0}" -ge "$MIN_LVL" ] && echo "D: $*" >&2
}


function cfg_set_default () {
  [ -n "${CFG[$1]}" ] || CFG["$1"]="$2"
}


function cfg_read_defaults () {
  local CFG_FN=
  local CFG_LNS=()
  local CFG_LN=
  local CFG_OPT=
  for CFG_FN in "$@"; do
    dbgp 2 "check cfg: $CFG_FN"
    [ -f "$CFG_FN" ] || continue
    dbgp 2 "found cfg: $CFG_FN"
    CFG_LN="$(sed -nre ' s~^\s*([A-Za-z0-9_\.\-]+)\s*[=:]\s*~\1=~p' "$CFG_FN")"
    readarray -t CFG_LNS <<<"$CFG_LN"
    for CFG_LN in "${CFG_LNS[@]}"; do
      CFG_OPT="${CFG_LN%%=*}"
      [ -n "$CFG_OPT" ] || continue
      CFG_LN="${CFG_LN#*=}"
      if [ -n "${CFG[$CFG_OPT]}" ]; then
        dbgp 4 "cfg opt: skip: already set: $CFG_OPT"
      else
        dbgp 4 "cfg opt: set: $CFG_OPT = '$CFG_LN'"
        CFG["$CFG_OPT"]="$CFG_LN"
      fi
    done
    return 0
  done
  return 1
}


function cfg_resolve_paths () {
  local O_NAME=
  local O_PATH=
  for O_NAME in "$@"; do
    O_PATH="${CFG[$O_NAME]}"
    case "$O_PATH" in
      '~/'* ) O_PATH="$HOME${O_PATH#\~}";;
    esac
    [ "$O_PATH" == "${CFG[$O_NAME]}" ] && continue
    dbgp 2 "resolved '$O_NAME' path to '$O_PATH'"
    CFG["$O_NAME"]="$O_PATH"
  done
}








# scroll
