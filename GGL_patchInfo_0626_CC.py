#-*- coding: cp949 -*-
#-*- coding: utf-8 -*-

# Script Name = PatchInfo.gfz Auto Writer
# Author & Editor => Hanghyun Ted Cho

# PatchInfo 파싱 작업 관련 추가된 모듈
#----------------------------------------------------------------------------
import os
import sys
import win32api
import binascii
import datetime
import time
import shutil
import xml.dom.minidom
from xml.dom.minidom import *
#----------------------------------------------------------------------------


# PatchInfo 파싱 작업 관련 추가된 전역변수
#----------------------------------------------------------------------------
global get_FileCRC
global new_NewversionInfo
global new_PatchDataFileName
global old_NewversionInfo
global old_PatchDataFileName
global old_FileCRC
#----------------------------------------------------------------------------


# PatchInfo 파일 작업 후 변경된 사항에 대해 커맨드 창에서 확인할 수 있는 로그 추가
#----------------------------------------------------------------------------
if __name__ == '__main__' :
    import logging
    import optparse

    LOGGING_LEVELS = {'critical': logging.CRITICAL,
                      'error': logging.ERROR,
                      'warning': logging.WARNING,
                      'info': logging.INFO,
                      'debug': logging.DEBUG}

    parser = optparse.OptionParser()
    parser.add_option('-l', '--logging-level', help='Logging level')
    parser.add_option('-f', '--logging-file', help='Logging file name')
    (options, args) = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(options.logging_level, logging.NOTSET)
    logging.basicConfig(level=logging_level, filename=options.logging_file,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
#----------------------------------------------------------------------------
 
 
# XML 파일 파싱
#----------------------------------------------------------------------------
xml_PatchInfo = xml.dom.minidom.parse('./PatchInfo.gfz')
#----------------------------------------------------------------------------     


# Root 경로내 변수로 저장되는 파일을 찾고 파일명을 추출하고 old 버전 필드를 PatchInfo에 추가함
#----------------------------------------------------------------------------------------------------------------------------------------------         
for root, dirs, files in os.walk("./"):
    for file in files:
        if file.startswith('company'):
            ext = os.path.splitext(file)[1]  
            if ext == '.BIN':
                new_PatchDataFileName = file
                new_PatchDataFileNames = os.path.splitext(new_PatchDataFileName)[0]
                new_NewversionInfo = new_PatchDataFileNames[23:26]
                
                # 로그 추가
                logging.info(new_PatchDataFileName)
                logging.info(new_NewversionInfo)
                
                # 기존 타겟 태그내 값을  old_ 변수에 저장함
                PatchInfos = xml_PatchInfo.getElementsByTagName("PatchInfo") 

                NewversionInfo = xml_PatchInfo.getElementsByTagName("NewversionInfo")
                for PatchInfo in PatchInfos:
                    NewversionInfoObj = PatchInfo.getElementsByTagName("NewversionInfo")[0]
                    NewversionInfo.append(NewversionInfoObj)
                old_NewversionInfo = (" ".join(t.nodeValue for t in NewversionInfo[0].childNodes if t.nodeType == t.TEXT_NODE))

                PatchDataFileName = xml_PatchInfo.getElementsByTagName("PatchDataFileName")
                for PatchInfo in PatchInfos:
                    PatchDataFileNameObj = PatchInfo.getElementsByTagName("PatchDataFileName")[0]
                    PatchDataFileName.append(PatchDataFileNameObj)    
                old_PatchDataFileName = " ".join(t.nodeValue for t in PatchDataFileName[0].childNodes if t.nodeType == t.TEXT_NODE)

                FileCRC = xml_PatchInfo.getElementsByTagName("FileCRC")
                for PatchInfo in PatchInfos:
                    FileCRCObj = PatchInfo.getElementsByTagName("FileCRC")[0]
                    FileCRC.append(FileCRCObj)    
                old_FileCRC = " ".join(t.nodeValue for t in FileCRC[0].childNodes if t.nodeType == t.TEXT_NODE)

                if old_NewversionInfo < new_NewversionInfo:
                    NewversionInfoObj.firstChild.replaceWholeText(new_NewversionInfo)
                    PatchDataFileNameObj.firstChild.replaceWholeText(new_PatchDataFileName)
                    
                    # 신규 패치 파일의 crc32 값을 추출하여 get_FileCRC 변수에 저장함
                    def CRC32_from_file(filename): 
                        buf = open(filename,'rb').read() 
                        buf = (binascii.crc32(buf) & 0xFFFFFFFF) 
                        return "%08X" % buf 

                    get_FileCRC = CRC32_from_file(new_PatchDataFileName)
                    get_FileCRC = get_FileCRC.lower()
                    
                    # 커맨드 로그 추가
                    logging.info(get_FileCRC)
                    
                    FileCRCObj.firstChild.replaceWholeText("0x" + get_FileCRC)
                else:
                    None
                
                # 새로운 패치 생성으로 기존 패치팩의 OldVersionInfo 정보를 동일한 필드로 추가함    
                PatchInfos = xml_PatchInfo.getElementsByTagName("PatchInfo")[0]

                upper_OldVersionInfo = xml_PatchInfo.getElementsByTagName("OldVersionInfo")
                New_OldVersionInfo = xml_PatchInfo.createElement("OldVersionInfo")
                New_OldVersionInfo.setAttribute("version", old_NewversionInfo)
                New_OldVersionInfo.setAttribute("PatchDataFileName", old_PatchDataFileName)
                New_OldVersionInfo.setAttribute("FileCRC", old_FileCRC)

                if old_NewversionInfo < new_NewversionInfo:
                    PatchInfos.insertBefore(New_OldVersionInfo, upper_OldVersionInfo[0])
                    
                    newline = xml_PatchInfo.createTextNode('\n')
                    PatchInfos.insertBefore(newline, upper_OldVersionInfo[0])
#---------------------------------------------------------------------------------------------------------------------------------------------- 


# PatchInfo 파싱 전 현재 날짜 및 시간이 기입된 백업 파일을 생성함(ex. PatchInfo_lastversion_20140620113145)
#---------------------------------------------------------------------------------------------------------------------------------------------- 
now = datetime.datetime.now()
for root, dirs, files in os.walk("./"):
    file = os.listdir("./")
    destination = "./PatchInfo_"
    for file in files:
        file = "PatchInfo.gfz"
        shutil.copy(os.path.join("./", file), destination+new_NewversionInfo+now.strftime("_%Y%m%d%H%M%S"))
#---------------------------------------------------------------------------------------------------------------------------------------------- 

                                     
# 런처 버전이 변경된 경우, Root내 이동된 신규 Launcher_New.exe 파일의 이름 및 버전 정보를 가져와 기존 태그에 업데이트 해줌
#-------------------------------------------------------------------------------------
getVer_Launcher = win32api.GetFileVersionInfo(r'.\Launcher_new.exe', '\\') 
'{}.{}.{}.{}'.format(                                                                                      
    win32api.HIWORD(getVer_Launcher['FileVersionMS']),
    win32api.LOWORD(getVer_Launcher['FileVersionMS']),
    win32api.HIWORD(getVer_Launcher['FileVersionLS']),
    win32api.LOWORD(getVer_Launcher['FileVersionLS']))                    

new_Launcher = '{}.0{}.{}.0{}'.format( 
                win32api.HIWORD(getVer_Launcher['FileVersionMS']),
                win32api.LOWORD(getVer_Launcher['FileVersionMS']),
                win32api.HIWORD(getVer_Launcher['FileVersionLS']),
                win32api.LOWORD(getVer_Launcher['FileVersionLS']))

new_Launchers = new_Launcher.replace(".", "")
NeedPatcherPatchlist = xml_PatchInfo.getElementsByTagName("NeedPatcherPatch")

bitdll1 = NeedPatcherPatchlist[0]
if bitdll1.attributes["PatcherFileTime"]:
    a = bitdll1.attributes["PatcherFileTime"]
    bitdll1.attributes["PatcherFileTime"].value.replace(a.value, new_Launchers)
    a.value = bitdll1.attributes["PatcherFileTime"].value.replace(a.value, new_Launchers)

#-------------------------------------------------------------------------------------

# Root 경로내 변수로 저장되는 파일을 찾고 파일명을 추출하고 CC 데이터의 old 버전 필드를 PatchInfo에 추가함
#----------------------------------------------------------------------------------------------------------------------------------------------  
for root, dirs, files in os.walk("./"):
        for file in files:
            # CCPATCHDATA 파일의 이름을 검색함
            if file.startswith('CCPATCHDATA'):
                ext = os.path.splitext(file)[1]  
                if ext == '.BIN':
                    new_CCDataFileName = file
                    new_CCDataFileNames = os.path.splitext(new_CCDataFileName)[0]
                    new_CCNewversionInfo = new_CCDataFileNames[17:19]
                    
                    # 로그 추가
                    logging.info(new_CCDataFileName)
                    logging.info(new_CCNewversionInfo)
                
                    # 타겟 태그내 값을 new_CCNewversionInfo, new_CCDataFileName 변수 값으로 교체함
                    PatchInfos = xml_PatchInfo.getElementsByTagName("PatchInfo") 

                    CCNewversionInfo = xml_PatchInfo.getElementsByTagName("CCNewversionInfo")
                    for PatchInfo in PatchInfos:
                        CCNewversionInfoObj = PatchInfo.getElementsByTagName("CCNewversionInfo")[0]
                        CCNewversionInfo.append(CCNewversionInfoObj)
                    old_CCNewversionInfo = (" ".join(t.nodeValue for t in CCNewversionInfo[0].childNodes if t.nodeType == t.TEXT_NODE))

                    CCDataFileName = xml_PatchInfo.getElementsByTagName("CCDataFileName")
                    for PatchInfo in PatchInfos:
                        CCDataFileNameObj = PatchInfo.getElementsByTagName("CCDataFileName")[0]
                        CCDataFileName.append(CCDataFileNameObj)    
                    old_CCDataFileName = " ".join(t.nodeValue for t in CCDataFileName[0].childNodes if t.nodeType == t.TEXT_NODE)

                    CCFileCRC = xml_PatchInfo.getElementsByTagName("CCFileCRC")
                    for PatchInfo in PatchInfos:
                        CCFileCRCObj = PatchInfo.getElementsByTagName("CCFileCRC")[0]
                        CCFileCRC.append(CCFileCRCObj)    
                    old_CCFileCRC = " ".join(t.nodeValue for t in CCFileCRC[0].childNodes if t.nodeType == t.TEXT_NODE)

                    if old_CCNewversionInfo < new_CCNewversionInfo:
                        CCNewversionInfoObj.firstChild.replaceWholeText(new_CCNewversionInfo)
                        CCDataFileNameObj.firstChild.replaceWholeText(new_CCDataFileName)
                    
                        # 신규 패치 파일의 crc32 값을 추출하여 변수에 저장함
                        def CRC32_from_file(filename): 
                            buf = open(filename,'rb').read() 
                            buf = (binascii.crc32(buf) & 0xFFFFFFFF) 
                            return "%08X" % buf 

                        get_CCFileCRC = CRC32_from_file(new_CCDataFileName)
                        get_CCFileCRC = get_CCFileCRC.lower()
                        
                        # 커맨드 로그 추가
                        logging.info(get_CCFileCRC)
                    
                        CCFileCRCObj.firstChild.replaceWholeText("0x" + get_CCFileCRC)
                    else:
                        None
                
                    # 새로운 패치 적용에 따른 기존 패치팩의 OldVersionInfo 정보를 동일한 포맷으로 생성하여 기존 OldVersionInfo 태그 상단 라인에  추가함    
                    PatchInfos = xml_PatchInfo.getElementsByTagName("PatchInfo")[0]

                    upper_CCOldVersionInfo = xml_PatchInfo.getElementsByTagName("CCOldVersionInfo")
                    New_CCOldVersionInfo = xml_PatchInfo.createElement("CCOldVersionInfo")
                    New_CCOldVersionInfo.setAttribute("version", old_CCNewversionInfo)
                    New_CCOldVersionInfo.setAttribute("CCDataFileName", old_CCDataFileName)
                    New_CCOldVersionInfo.setAttribute("CCFileCRC", old_CCFileCRC)

                    if old_CCNewversionInfo < new_CCNewversionInfo:
                        PatchInfos.insertBefore(New_CCOldVersionInfo, upper_CCOldVersionInfo[0])
                    
                        newline = xml_PatchInfo.createTextNode('\n')
                        PatchInfos.insertBefore(newline, upper_CCOldVersionInfo[0])
#----------------------------------------------------------------------------------------------------------------------------------------------  

#print(xml_PatchInfo.toxml())


if old_NewversionInfo < new_NewversionInfo:
    xml_PatchInfo.writexml( open('PatchInfo.gfz', 'w'))
    win32api.MessageBox(0, 'New PatchInfo Create Complete', 'PatchInfoGenerate', 0x00001001)
elif  old_CCNewversionInfo < new_CCNewversionInfo:
    xml_PatchInfo.writexml( open('PatchInfo.gfz', 'w'))
    win32api.MessageBox(0, 'New PatchInfo Create Complete', 'PatchInfoGenerate', 0x00001001) 
else:
    None


