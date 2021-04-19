#-*- coding: cp949 -*-
#-*- coding: utf-8 -*-

# Script Name = PatchInfo.gfz Auto Writer
# Author & Editor => Hanghyun Ted Cho

# PatchInfo �Ľ� �۾� ���� �߰��� ���
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


# PatchInfo �Ľ� �۾� ���� �߰��� ��������
#----------------------------------------------------------------------------
global get_FileCRC
global new_NewversionInfo
global new_PatchDataFileName
global old_NewversionInfo
global old_PatchDataFileName
global old_FileCRC
#----------------------------------------------------------------------------


# PatchInfo ���� �۾� �� ����� ���׿� ���� Ŀ�ǵ� â���� Ȯ���� �� �ִ� �α� �߰�
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
 
 
# XML ���� �Ľ�
#----------------------------------------------------------------------------
xml_PatchInfo = xml.dom.minidom.parse('./PatchInfo.gfz')
#----------------------------------------------------------------------------     


# Root ��γ� ������ ����Ǵ� ������ ã�� ���ϸ��� �����ϰ� old ���� �ʵ带 PatchInfo�� �߰���
#----------------------------------------------------------------------------------------------------------------------------------------------         
for root, dirs, files in os.walk("./"):
    for file in files:
        if file.startswith('company'):
            ext = os.path.splitext(file)[1]  
            if ext == '.BIN':
                new_PatchDataFileName = file
                new_PatchDataFileNames = os.path.splitext(new_PatchDataFileName)[0]
                new_NewversionInfo = new_PatchDataFileNames[23:26]
                
                # �α� �߰�
                logging.info(new_PatchDataFileName)
                logging.info(new_NewversionInfo)
                
                # ���� Ÿ�� �±׳� ����  old_ ������ ������
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
                    
                    # �ű� ��ġ ������ crc32 ���� �����Ͽ� get_FileCRC ������ ������
                    def CRC32_from_file(filename): 
                        buf = open(filename,'rb').read() 
                        buf = (binascii.crc32(buf) & 0xFFFFFFFF) 
                        return "%08X" % buf 

                    get_FileCRC = CRC32_from_file(new_PatchDataFileName)
                    get_FileCRC = get_FileCRC.lower()
                    
                    # Ŀ�ǵ� �α� �߰�
                    logging.info(get_FileCRC)
                    
                    FileCRCObj.firstChild.replaceWholeText("0x" + get_FileCRC)
                else:
                    None
                
                # ���ο� ��ġ �������� ���� ��ġ���� OldVersionInfo ������ ������ �ʵ�� �߰���    
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


# PatchInfo �Ľ� �� ���� ��¥ �� �ð��� ���Ե� ��� ������ ������(ex. PatchInfo_lastversion_20140620113145)
#---------------------------------------------------------------------------------------------------------------------------------------------- 
now = datetime.datetime.now()
for root, dirs, files in os.walk("./"):
    file = os.listdir("./")
    destination = "./PatchInfo_"
    for file in files:
        file = "PatchInfo.gfz"
        shutil.copy(os.path.join("./", file), destination+new_NewversionInfo+now.strftime("_%Y%m%d%H%M%S"))
#---------------------------------------------------------------------------------------------------------------------------------------------- 

                                     
# ��ó ������ ����� ���, Root�� �̵��� �ű� Launcher_New.exe ������ �̸� �� ���� ������ ������ ���� �±׿� ������Ʈ ����
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

# Root ��γ� ������ ����Ǵ� ������ ã�� ���ϸ��� �����ϰ� CC �������� old ���� �ʵ带 PatchInfo�� �߰���
#----------------------------------------------------------------------------------------------------------------------------------------------  
for root, dirs, files in os.walk("./"):
        for file in files:
            # CCPATCHDATA ������ �̸��� �˻���
            if file.startswith('CCPATCHDATA'):
                ext = os.path.splitext(file)[1]  
                if ext == '.BIN':
                    new_CCDataFileName = file
                    new_CCDataFileNames = os.path.splitext(new_CCDataFileName)[0]
                    new_CCNewversionInfo = new_CCDataFileNames[17:19]
                    
                    # �α� �߰�
                    logging.info(new_CCDataFileName)
                    logging.info(new_CCNewversionInfo)
                
                    # Ÿ�� �±׳� ���� new_CCNewversionInfo, new_CCDataFileName ���� ������ ��ü��
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
                    
                        # �ű� ��ġ ������ crc32 ���� �����Ͽ� ������ ������
                        def CRC32_from_file(filename): 
                            buf = open(filename,'rb').read() 
                            buf = (binascii.crc32(buf) & 0xFFFFFFFF) 
                            return "%08X" % buf 

                        get_CCFileCRC = CRC32_from_file(new_CCDataFileName)
                        get_CCFileCRC = get_CCFileCRC.lower()
                        
                        # Ŀ�ǵ� �α� �߰�
                        logging.info(get_CCFileCRC)
                    
                        CCFileCRCObj.firstChild.replaceWholeText("0x" + get_CCFileCRC)
                    else:
                        None
                
                    # ���ο� ��ġ ���뿡 ���� ���� ��ġ���� OldVersionInfo ������ ������ �������� �����Ͽ� ���� OldVersionInfo �±� ��� ���ο�  �߰���    
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


