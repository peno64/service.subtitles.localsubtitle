# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import shutil

import uuid
import json
import chardet

if sys.version_info[0] == 2:
    p2 = True
else:
    unicode = str
    p2 = False

from resources.lib.dualsubs import mergesubs

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString
__exts__       = [ ".srt", ".sub", ".ssa", ".ass", ".idx", ".smi", ".aqt", ".scc", ".jss", ".ogm", ".pjs", ".rt", ".smi" ]

try:
    translatePath = xbmcvfs.translatePath
except AttributeError:
    translatePath = xbmc.translatePath

__cwd__        = translatePath( __addon__.getAddonInfo('path') )
if p2:
    __cwd__ = __cwd__.decode("utf-8")

__resource__   = translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
if p2:
    __resource__ = __resource__.decode("utf-8")

__profile__    = translatePath( __addon__.getAddonInfo('profile') )
if p2:
    __profile__ = __profile__.decode("utf-8")

__temp__       = translatePath( os.path.join( __profile__, 'temp', '') )
if p2:
    __temp__ = __temp__.decode("utf-8")

if xbmcvfs.exists(__temp__):
  shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

__msg_box__       = xbmcgui.Dialog()

__subtitlepath__  = translatePath("special://subtitles")

if __subtitlepath__ == None:
  __subtitlepath__ = ""

__subtitle__      = ""
if __subtitlepath__ != "":
  __subtitle__      = __subtitlepath__ + "subtitle.srt"


sys.path.append (__resource__)

# Make sure the manual search button is disabled
try:
  if xbmc.getCondVisibility("Window.IsActive(subtitlesearch)"):
      window = xbmcgui.Window(10153)
      window.getControl(160).setEnableCondition('!String.IsEqual(Control.GetLabel(100),"{}")'.format(__scriptname__))
except:
  #ignore
  window = ''

def AddItem(name, url):
  listitem = xbmcgui.ListItem(label          = "",
                              label2         = name
                             )

  listitem.setProperty( "sync", "false" )
  listitem.setProperty( "hearing_imp", "false" )

  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)


def Search():
  if __subtitle__ != "":
    if xbmcvfs.exists(__subtitle__):
      AddItem(__subtitle__, "plugin://%s/?action=download" % (__scriptid__))

  AddItem(__language__(33002), "plugin://%s/?action=browse" % (__scriptid__))
  AddItem(__language__(33011), "plugin://%s/?action=browsesingle" % (__scriptid__))
  AddItem(__language__(33004), "plugin://%s/?action=browsedual" % (__scriptid__))
  AddItem(__language__(33008), "plugin://%s/?action=settings" % (__scriptid__))

def get_params(string=""):
  param=[]
  if string == "":
    paramstring=sys.argv[2]
  else:
    paramstring=string
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]

  return param

params = get_params()

def unzip(zip, exts):
  filename = None
  for file in xbmcvfs.listdir(zip)[1]:
    file = os.path.join(__temp__, file)
    if (os.path.splitext( file )[1] in exts):
      filename = file
      break

  if filename != None:
    xbmc.executebuiltin('Extract("%s","%s")' % (zip,__temp__,), True)
  else:
    xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__ , __language__(33007))))
  return filename

def Download(filename):
  listitem = xbmcgui.ListItem(label=filename)
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=filename,listitem=listitem,isFolder=False)

if params['action'] == 'manualsearch':
  __msg_box__.ok('LocalSubtitle', __language__(33001))
  Search()

elif params['action'] == 'search':
  Search()

elif params['action'] == 'download':
  if xbmcvfs.exists(__subtitle__):
    Download(__subtitle__)

elif params['action'] == 'browse':
  exts = ''
  for ext in __exts__:
    exts = exts + '|' + ext
  exts = exts[1:]
  while True:
    subtitlefile = __msg_box__.browse(1, __language__(33003), "video", ".zip|" + exts, False, False, __subtitlepath__, False)
    if subtitlefile != __subtitlepath__:
      if subtitlefile.endswith('.zip'):
        subtitlefile = unzip(subtitlefile, __exts__)
    if subtitlefile == __subtitlepath__ or subtitlefile != None:
      break

  if subtitlefile != __subtitlepath__:
    Download(subtitlefile)

elif params['action'] == 'browsesingle' or params['action'] == 'browsedual':
  while True:
    if params['action'] == 'browsesingle':
      title = __language__(33003)
    elif __addon__.getSetting('dualsub_swap') == 'true':
      title = __language__(33006)
    else:
      title = __language__(33005)
    subtitlefile1 = __msg_box__.browse(1, title, "video", ".zip|.srt", False, False, __subtitlepath__, False)
    if subtitlefile1 != __subtitlepath__:
      if subtitlefile1.endswith('.zip'):
        subtitlefile1 = unzip(subtitlefile1, [ ".srt" ])
    if subtitlefile1 == __subtitlepath__ or subtitlefile1 != None:
      break

  if subtitlefile1 != __subtitlepath__:
    subs=[]
    subs.append(subtitlefile1)

    if params['action'] != 'browsesingle':
      while True:
        if __addon__.getSetting('dualsub_swap') == 'true':
          title = __language__(33005)
        else:
          title = __language__(33006)
        title = title + ' ' + __language__(33009)
        subtitlefile2 = __msg_box__.browse(1, title, "video", ".zip|.srt", False, False, __subtitlepath__, False)
        if subtitlefile2 == __subtitlepath__:
          break
        else:
          if subtitlefile2.endswith('.zip'):
            subtitlefile2 = unzip(subtitlefile2, [ ".srt" ])
          if subtitlefile2 != None:
            subs.append(subtitlefile2)
            break

    substemp=[]
    for sub in subs:
      # Python seems not to be able to access files on special kodi locations like smb: (samba)
      # See https://forum.kodi.tv/showthread.php?tid=372745
      # To work-around that, the kodi copy function from xbmcvfs is used to copy the file from the specified location to the temp folder which is on the local OS and thus accessible by Python
      # See https://romanvm.github.io/Kodistubs/_autosummary/xbmcvfs.html
      subtemp = os.path.join(__temp__, "%s" %(str(uuid.uuid4())))
      xbmcvfs.copy(sub, subtemp)
      substemp.append(subtemp)

    finalfile = mergesubs(substemp)

    # And now the temp files are removed again
    for subtemp in substemp:
      xbmcvfs.delete(subtemp)

    Download(finalfile)

elif params['action'] == 'settings':
  __addon__.openSettings()
  __msg_box__.ok('LocalSubtitle', __language__(32530))

xbmcplugin.endOfDirectory(int(sys.argv[1]))
