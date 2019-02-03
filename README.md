# LocalSubtitle

kodi addon to add a local subtitle to a video

This addon is a kodi subtitle addon to apply a local subtitle to the current playing video.
Kodi has its own possibility to load a local subtitle (via Browse for subtitle...) but that sometimes does not work (hanging) and that is why this addon was created.
This addon is opened via Download subtitle like all other subtitle addons.
There are two ways to select a local subtitle.
If a location of subtitles is defined in kodi, Settings, Player, Language, Custom subtitle folder, then the addin searches a file with name subtitle.srt on that location.
On Raspberry Pi, a possible place is /storage/videos because that is a share that can be accessed by any computer in the network but any folder accessable by kodi will do.
subtitle.srt is fixed. If the location is not defined or subtitle.srt is not found then subtitle.srt will not be proposed.
And there is always a Browse option. If above location is set then the browse starts in this folder. Else at top level.

The addon can be downloaded from https://github.com/peno64/LocalSubtitle/releases or the latest version can be downloaded or installed via the file browser from http://users.telenet.be/peno/localsubtitle/
Installation instructions for the latter can be found in https://github.com/peno64/LocalSubtitle/tree/master/localsubtitle/installation
To manually install, put the zip file somewhere where kodi can access it.
Then in kodi, choose Install from zip file, navigate to the zip and choose it.
