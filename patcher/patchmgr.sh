#!/bin/bash
# -*- coding: utf-8, tab-width: 2 -*-
SELFPATH="$(readlink -m "$0"/..)"


source "$SELFPATH"/../lib/cli-opts.sh --lib || exit $?


function main () {
  local -A CFG
  cfg_read_defaults "$HOME"/.{config/,}ragnarok/ragpatch-pmb.cfg

  local POS_ARGN=()
  local POS_ARGS=()
  local OPT=
  while [ "$#" -gt 0 ]; do
    OPT="$1"; shift
    case "$OPT" in
      '' ) ;;
      --show-patch-version ) CFG[action]="${OPT#--}";;
      -- ) POS_ARGS+=( "$@" ); break;;
      --*=* )
        OPT="${OPT#--}"
        CFG["${OPT%%=*}"]="${OPT#*=}";;
      -* ) return 1$(echo "E: $0: unsupported option: $OPT" >&2);;
      * )
        case "${POS_ARGN[0]}" in
          '' ) return 1$(echo "E: $0: unexpected positional argument." >&2);;
          '+' ) POS_ARGS+=( "$OPT" );;
          * ) CFG["${POS_ARGN[0]}"]="$OPT"; POS_ARGN=( "${POS_ARGN[@]:1}" );;
        esac;;
    esac
  done

  cfg_set_default action update
  cfg_set_default gamedir "$PWD"
  cfg_read_defaults "${CFG[gamedir]}"/ragpatch-pmb.cfg
  cfg_set_default patch-cache "${CFG[gamedir]}/ragpatch.cache"
  cfg_resolve_paths gamedir patch-cache

  [ -n "${CFG[patchver]}" ] || CFG[patchver]="$(detect_patch_version)"

  case "${CFG[action]}" in
    show-patch-version ) <<<"${CFG[patchver]}" grep .; return $?;;
  esac

  if [ "$(type -t "acn_${CFG[action]//-/_}")" == 'function' ]; then
    acn_"${CFG[action]//-/_}" "$@"
    return $?
  fi

  echo "E: action not implemented: ${CFG[action]}" >&2
  return 1
}



function detect_patch_version () {
  # detect current installed patch number for lookup in Patch2.txt
  head -c 4 "${CFG[gamedir]}/patch.inf" | od -A n -t u4 | tr -cd '0-9\n'
}















main "$@"; exit $?
