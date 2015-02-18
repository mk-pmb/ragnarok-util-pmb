-*- coding: utf-8, tab-width: 2 -*-

Ragnarok utility collection
===========================

ragtar
-----
* list archive contents:
```bash
$ ragtar tzf 2009-10-13_data_BGM.rgz
BGM/
BGM/53.mp3
```
* list archive content details:
  * first row is hex byte offset of file record in the un-gzip-ed stream.
```bash
$ ragtar tvzf 2014-09-16_aPatchClient.rgz
@0000000      / PatchClient
@000000e      / PatchClient/Lua Files
@0000026      / PatchClient/Lua Files/ServerInfoz
@000004a   1851 PatchClient/Lua Files/ServerInfoz/ServerInfo_FR.lub
@00007bf      / PatchClient/Lua Files/SkinInfoz
@00007e1   4916 PatchClient/Lua Files/SkinInfoz/SkinInfo_FR.lub
@0001b4b  31560 PatchClient/Replay.bmp
@00096b0      = 4 directories, 3 files, 38327 bytes
```
* extract files:
```bash
$ ragtar xvzf 2014-09-16_aPatchClient.rgz --exist=skip
dir exists:     PatchClient
dir exists:     PatchClient/Lua Files
dir exists:     PatchClient/Lua Files/ServerInfoz
skip file:      PatchClient/Lua Files/ServerInfoz/ServerInfo_FR.lub
create dir:     PatchClient/Lua Files/SkinInfoz
create file:    PatchClient/Lua Files/SkinInfoz/SkinInfo_FR.lub
skip file:      PatchClient/Replay.bmp
$ ragtar xvzf 2013-02-28_data_gm.rgz --exist=replace
replace file:   patch.inf
```






License
=======
GNU GPL v2

