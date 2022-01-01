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

try:
  import pysubs2
except:
  from lib import pysubs2

if sys.version_info[0] == 2:
    p2 = True
else:
    unicode = str
    p2 = False

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
  AddItem(__language__(33004), "plugin://%s/?action=browsedual" % (__scriptid__))

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

def charset_detect(filename):
    with open(filename,'rb') as fi:
        rawdata = fi.read()
    encoding = chardet.detect(rawdata)['encoding']
    if encoding.lower() == 'gb2312':  # Decoding may fail using GB2312
        encoding = 'gbk'
    return encoding

def merge(file):
    subs=[]
    subs.append(pysubs2.SSAFile.from_string('', 'srt'))
    for sub in file:
      subs.append(pysubs2.load(sub, encoding=charset_detect(sub)))
    ass = os.path.join(__temp__, "%s.ass" %(str(uuid.uuid4())))

    top_style = pysubs2.SSAStyle()
    bottom_style=top_style.copy()
    top_style.alignment = 8
    top_style.fontsize = int(__addon__.getSetting('top_fontsize'))
    if(__addon__.getSetting('top_bold') == 'true'):
      top_style.bold = 1
    top_style.fontname = unicode(__addon__.getSetting('top_font'))
    if (__addon__.getSetting('top_color') == 'Yellow'):
      top_style.primarycolor = pysubs2.Color(255, 255, 0, 0)
    elif (__addon__.getSetting('top_color') == 'White'):
      top_style.primarycolor = pysubs2.Color(255, 255, 255, 0)
      top_style.secondarycolor = pysubs2.Color(255,255,255,0)
    if (__addon__.getSetting('top_background') == 'true'):
      top_style.backcolor = pysubs2.Color(0,0,0,128)
      top_style.outlinecolor = pysubs2.Color(0,0,0,128)
      top_style.borderstyle = 4
    top_style.shadow = int(__addon__.getSetting('top_shadow'))
    top_style.outline = int(__addon__.getSetting('top_outline'))

    bottom_style.alignment = 2
    bottom_style.fontsize= int(__addon__.getSetting('bottom_fontsize'))
    if (__addon__.getSetting('bottom_bold') =='true'):
      bottom_style.bold = 1
    bottom_style.fontname = unicode(__addon__.getSetting('bottom_font'))
    if (__addon__.getSetting('bottom_color') == 'Yellow'):
      bottom_style.primarycolor=pysubs2.Color(255, 255, 0, 0)
    elif (__addon__.getSetting('bottom_color') == 'White'):
      bottom_style.primarycolor=pysubs2.Color(255, 255, 255, 0)
    if (__addon__.getSetting('bottom_background') == 'true'):
      bottom_style.backcolor=pysubs2.Color(0,0,0,128)
      bottom_style.outlinecolor=pysubs2.Color(0,0,0,128)
      bottom_style.borderstyle=4
    bottom_style.shadow = int(__addon__.getSetting('bottom_shadow'))
    bottom_style.outline = int(__addon__.getSetting('bottom_outline'))

    subs[0].styles['top-style'] = top_style
    subs[0].styles['bottom-style'] = bottom_style

    if __addon__.getSetting('autoShft') == 'true':
      timeThresh = int(__addon__.getSetting('autoShftAmt'))
    else:
      timeThresh = -1
    l1 = len(subs[1])
    if len(subs) >= 3:
      l2 = len(subs[2])
    else:
      l2 = 0
    i = 0
    j = 0
    prevStart1 = -1
    prevEnd1 = 999999
    prevIndex2 = -1
    while i < l1 or j < l2:
      if i < l1:
        line1 = subs[1][i]
        line1.style = u'bottom-style'
        subs[0].append(line1)

      if timeThresh < 0:
        j = i
        if j < l2:
          line2 = subs[2][j]
          line2.style = u'top-style'
          subs[0].append(line2)
      else:
        while j < l2:
          line2 = subs[2][j]
          if i < l1 and line2.start > line1.start + timeThresh:
            break

          line2.style = u'top-style'
          if i < l1:
            if abs(line2.start - line1.start) <= timeThresh:
              if prevIndex2 < 0 or line1.start > subs[0][prevIndex2].end:
                line2.start = line1.start
              else:
                line2.start = subs[0][prevIndex2].end + 10
            if abs(line2.end - line1.end) <= timeThresh:
              line2.end = line1.end
          if prevIndex2 >= 0 and subs[0][prevIndex2].start == prevStart1:
            if line2.start > prevEnd1:
              subs[0][prevIndex2].end = prevEnd1
            elif line2.start <= prevEnd1:
              subs[0][prevIndex2].end = line2.start - 10
          prevIndex2 = len(subs[0])
          subs[0].append(line2)
          j = j + 1

        if i < l1:
          prevStart1 = line1.start
          prevEnd1 = line1.end
        else:
          prevStart1 = -1
          prevEnd1 = 999999

      i = i + 1

    subs[0].save(ass,format_='ass')
    return ass

def unzip(zip, exts):
  xbmc.executebuiltin('Extract("%s","%s")' % (zip,__temp__,), True)

  for file in xbmcvfs.listdir(zip)[1]:
    file = os.path.join(__temp__, file)
    if (os.path.splitext( file )[1] in exts):
      return file

  xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__ , __language__(33007))))
  return ''

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
  subtitlefile = xbmcgui.Dialog().browse(1, __language__(33003), "video", ".zip|" + exts, False, False, __subtitlepath__, False)
  if subtitlefile != __subtitlepath__:
    if subtitlefile.endswith('.zip'):
      subtitlefile = unzip(subtitlefile, __exts__)
    if subtitlefile != '':
      Download(subtitlefile)

elif params['action'] == 'browsedual':
  subtitlefile1 = xbmcgui.Dialog().browse(1, __language__(33005), "video", ".zip|.srt", False, False, __subtitlepath__, False)
  if subtitlefile1 != __subtitlepath__:
    if subtitlefile1.endswith('.zip'):
      subtitlefile1 = unzip(subtitlefile1, [ ".srt" ])

    if subtitlefile1 != '':
      subs=[]
      subs.append(subtitlefile1)

      subtitlefile2 = xbmcgui.Dialog().browse(1, __language__(33006), "video", ".zip|.srt", False, False, __subtitlepath__, False)
      if subtitlefile2 == __subtitlepath__ or subtitlefile2 == None:
        subtitlefile2 = ""
      else:
        if subtitlefile2.endswith('.zip'):
          subtitlefile2 = unzip(subtitlefile2, [ ".srt" ])
        if subtitlefile2 == '':
          subtitlefile1 = ''
        else:
          subs.append(subtitlefile2)

      if subtitlefile1 != '':
        finalfile = merge(subs)
        Download(finalfile)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
