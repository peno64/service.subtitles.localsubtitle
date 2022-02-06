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

def charset_detect(filename, bottom):
    if bottom:
      setting = 'bottom_characterset'
    else:
      setting = 'top_characterset'
    encoding = __addon__.getSetting(setting)
    if encoding == 'Auto':
      with open(filename,'rb') as fi:
          rawdata = fi.read()
      # see https://chardet.readthedocs.io/en/latest/supported-encodings.html
      encoding = chardet.detect(rawdata)['encoding']
      if encoding.lower() == 'gb2312':  # Decoding may fail using GB2312
          encoding = 'gbk'
    else:
      # see https://docs.python.org/3/library/codecs.html
      choices = {'Arabic (ISO)': 'iso-8859-6', 'Arabic (Windows)': 'windows-1256', 'Baltic (ISO)': 'iso-8859-13', 'Baltic (Windows)': 'windows-1257', 'Central Europe (ISO)': 'iso-8859-2', 'Central Europe (Windows)': 'windows-1250', 'Chinese Simplified': 'gb2312', 'Chinese Traditional (Big5)': 'cp950', 'Cyrillic (ISO)': 'iso-8859-5', 'Cyrillic (Windows)': 'windows-1251', 'Greek (ISO)': 'iso-8859-7', 'Greek (Windows)': 'windows-1253', 'Hebrew (ISO)': 'iso-8859-8', 'Hebrew (Windows)': 'windows-1255', 'Hong Kong (Big5-HKSCS)': 'big5-hkscs', 'Japanese (Shift-JIS)': 'csshiftjis', 'Korean': 'iso2022_kr', 'Nordic Languages (ISO)': 'iso-8859-10', 'South Europe (ISO)': 'ISO-8859-3', 'Thai (ISO)': 'iso-8859-11', 'Thai (Windows)': 'cp874', 'Turkish (ISO)': 'iso-8859-9', 'Turkish (Windows)': 'windows-1254', 'UTF8': 'utf8', 'UTF16': 'utf16', 'UTF32': 'utf32', 'Vietnamese (Windows)': 'windows-1258', 'Western Europe (ISO)': 'iso-8859-15', 'Western Europe (Windows)': 'windows-1252'}
      encoding = choices.get(encoding, 'default')

    return encoding

def setminTime(minTime, prevIndex, subs, line1):
    if minTime > 0 and prevIndex >= 0:
      line0 = subs[0][prevIndex]
      l = line0.end - line0.start
      if l < minTime:
        l = minTime
        if not line1 is None and line0.start + l > line1.start:
          l = line1.start - line0.start - 50
        line0.end = line0.start + l
    return len(subs[0])

def merge(file):
    subs=[]
    subs.append(pysubs2.SSAFile.from_string('', 'srt'))
    bottom = not __addon__.getSetting('dualsub_swap') == 'true'
    for sub in file:
      try:
        result = pysubs2.load(sub, encoding=charset_detect(sub, bottom))
      except Exception as e:
        __msg_box__.ok(__language__(32031), str(e))
        raise e

      subs.append(result)

      bottom = not bottom
    ass = os.path.join(__temp__, "%s.ass" %(str(uuid.uuid4())))

    if not p2:
      myunicode = str
    else:
      myunicode = unicode

    top_style = pysubs2.SSAStyle()
    bottom_style=top_style.copy()
    top_style.alignment = 8
    top_style.fontsize = int(__addon__.getSetting('top_fontsize'))
    if(__addon__.getSetting('top_bold') == 'true'):
      top_style.bold = 1
    top_style.fontname = myunicode(__addon__.getSetting('top_font'))
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
    bottom_style.fontname = myunicode(__addon__.getSetting('bottom_font'))
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

    if __addon__.getSetting('dualsub_swap') == 'true':
      subs[0].styles['top-style'] = bottom_style
      subs[0].styles['bottom-style'] = top_style
    else:
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
    prevIndexBottom = -1
    prevIndexTop = -1
    minTime = int(__addon__.getSetting('minTime'))
    while i < l1 or j < l2:
      if i < l1:
        line1 = subs[1][i]
        line1.style = u'bottom-style'
        prevIndexBottom = setminTime(minTime, prevIndexBottom, subs, line1)
        #line1.text=unicode(line1.text, 'windows-1254')
        #line1.text=unicode('tarara', 'windows-1254')
        subs[0].append(line1)

      if timeThresh < 0:
        j = i
        if j < l2:
          line2 = subs[2][j]
          line2.style = u'top-style'
          prevIndexTop = setminTime(minTime, prevIndexTop, subs, line2)
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
          prevIndexTop = setminTime(minTime, prevIndexTop, subs, line2)
          subs[0].append(line2)
          j = j + 1

        if i < l1:
          prevStart1 = line1.start
          prevEnd1 = line1.end
        else:
          prevStart1 = -1
          prevEnd1 = 999999

      i = i + 1

    setminTime(minTime, prevIndexBottom, subs, None)
    setminTime(minTime, prevIndexTop, subs, None)

    subs[0].save(ass,format_='ass')
    return ass

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

elif params['action'] == 'browsedual':
  while True:
    if __addon__.getSetting('dualsub_swap') == 'true':
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

    finalfile = merge(subs)
    Download(finalfile)

elif params['action'] == 'settings':
  __addon__.openSettings()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
