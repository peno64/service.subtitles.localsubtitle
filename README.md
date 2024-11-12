# service.subtitles.localsubtitle

kodi addon to add a local subtitle to a video and since version 1.6.0 also dual subtitles.

This addon is a kodi subtitle addon to apply a local subtitle to the current playing video.
Kodi has its own possibility to load a local subtitle (via Browse for subtitle...) but that sometimes does not work (hanging) and that is why this addon was initially created.
This addon is opened via Download subtitle like all other subtitle addons.

There are two ways (actually three) to select a local subtitle.

If a location of subtitles is defined in kodi, Settings, Player, Language, Custom subtitle folder, then the addon searches a file with name subtitle.srt on that location.
On Raspberry Pi, a possible place is /storage/videos because that is a share that can be accessed by any computer in the network but any folder accessable by kodi will do.
subtitle.srt is fixed. If the location is not defined or subtitle.srt is not found then subtitle.srt will not be proposed.

And there is always a Browse Single Subtitle option and a Browse Dual Subtitle option. If above location is set then the browse starts in this folder. Else at top level.
The following subtitle extensions are allowed: .srt, .sub, .ssa, .ass, .idx, .smi, .aqt, .scc, .jss, .ogm, .pjs, .rt, .smi
However if dual subtitles are chosen then only .srt subtitle files are allowed.
Since version 1.7.0 also a zip file with a subtitle is allowed. Both for single and dual subtitles.

The difference between with Kodi Settings and with Addon settings is that with Kodi settings the settings from Kodi settings are used: (Settings, Player, Language, Subtitles) (Font, size, ...)
With Addon Settings the settings defined in the Addon are used
The difference between single subtitle and dual subtitle is the following.
When Dual Subtitle is chosen then it is possible to select 2 subtitle files.
There are 3 ways to show the two subtitles. Bottom, top or above each other at the bottom or next to each other at the bottom.
As such subtitles of two languages can be displayed at the same time. But it is also possible to only select one subtitle. This to also have the advantages of dual function functionality.
As extra several extra feastures are added in this case:
- Minimal time subtitles on screen: For the slow readers
- Auto shift subtitles: to synchronize the two subtitles such that they are displayed at the same time
- Font, character set, color, ... selection: This overrules the kodi settings

# Installation in kodi:
Via repository https://peno64.github.io/repository.peno64/
