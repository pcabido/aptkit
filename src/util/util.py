# -*- coding: utf-8 -*-
import os
import sys
import shutil
import gobject
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

def rmdir(path):
    """
    Deletes a dir.
    """
    try:
        shutil.rmtree(path, ignore_errors=True)
    except:
        pass

def mkdir(path, removeFirst=False):
    """
    Creates a dir.
    """
    if removeFirst:
        if os.path.isdir(path):
            rmdir(path)
    
    dirs = path.split("/")
    dir = ""
                
    for dirname in dirs:
        dir += dirname + "/"
        if not os.path.isdir(dir) and len(dir)>0:
            os.mkdir(dir)
    
def list2dic(list):
    """
    Converts a list to a dictionary.
    """
    Dic = {}
    for l in list:
        if l != "":
            tmpStr = l.split(": ")
            Dic[tmpStr[0]] = tmpStr[1]
        
    return Dic

def changePackageListValue(list, indexName, name, indexVersion, version, indexChange, newval):
    """
    Changes a value in the package list.
    """
    try:
        for l in list:
            if l[indexName] == name and l[indexVersion] == version:
                l[indexChange] = newval
                return True
        
        return False
    except:
        return False
    
def removeDuplicates(list):
    """
    Removes duplicates from a list.
    """
    try:
        if list:
            list.sort()
            last = list[-1]
            for i in range(len(list)-2, -1, -1):
                if last==list[i]: 
                    del list[i]
                else: 
                    last=list[i]
        return list
    except:
        return []


def findStrInDic(str, dic):
    """
    Finds a dictionary element that contains a certain string.
    """
    for key, value in dic.items():
        if str.lower() in value.lower():
            return True
         
    return False
 
def dicKey(dic, val):
    """
    Returns a dictionary key that matches a certain value.
    """
    for key, value in dic.items():
        if value == val:
            return key
        
    return ""

def iligalChars(str, list=[]):
    """
    Returns true or false when a certain value is in the list or default chars.
    """
    if list == []:
        if (':' in str) or ('#' in str) or ('?' in str) or ('£' in str) or ('€' in str) \
        or ('=' in str) or ('<' in str) or ('>' in str) or ('ª' in str) or ('º' in str) \
        or ('%' in str) or ('^' in str) or ('»' in str) or ('«' in str) or ('(' in str) \
        or (')' in str) or ('[' in str) or (']' in str) or ('{' in str) or ('}' in str) \
        or ('!' in str) or ('"' in str) or ('@' in str) or ('|' in str) or ('+' in str) \
        or ('¨' in str) or ('`' in str) or ('&' in str) or ('$' in str):
            return True
    else:
        for l in list:
            if l in str:
                return True
    
    return False

def pbarValue(val, default=0):
    """
    Defines a progress value.
    """
    if default == 0:
        if val <= 0.07:
            return 0.07
        elif val <= 0.12:
            return 0.12
        elif val <= 0.25:
            return 0.25
        elif val <= 0.5:
            return 0.5
        elif val <= 0.75:
            return 0.75
        elif val <= 0.95:
            return 0.95
    elif default == 10:
        if val <= 0.05:
            return 0.05
        elif val <= 0.1:
            return 0.1
        elif val <= 0.2:
            return 0.2
        elif val <= 0.3:
            return 0.3
        elif val <= 0.4:
            return 0.4
        elif val <= 0.5:
            return 0.5
        elif val <= 0.6:
            return 0.6
        elif val <= 0.7:
            return 0.7
        elif val <= 0.8:
            return 0.8
        elif val <= 0.9:
            return 0.9
    
    return 1