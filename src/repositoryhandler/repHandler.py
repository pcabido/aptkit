# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)

import apt
import apt_pkg
import apt_inst
import os
import shutil
from src.util import util, aptutil

apt_pkg.init()         

class rephandle:
    
    def __init__(self, kitsSourcesList, tmpDir, localDir=""):
        """
        Initializes the repository handler class.
        """
        
        self._sourceList = kitsSourcesList
        self._tmpDir = tmpDir
        self._localDir = localDir
        self._packages = []
        self._localKits = []
        
    def update(self, deleteFiles=False):
        """
        Fetches the packages from the kit repository.
        """
        
        try:
            if deleteFiles:
                for root, dirs, files in os.walk(self._tmpDir):
                    for name in files:
                        filename = os.path.join(root, name)
                        if os.path.isfile(filename):
                            os.remove(filename)
                            
                util.rmdir(self._tmpDir)
            
            util.mkdir(self._tmpDir)
            util.mkdir(self._tmpDir + '/partial')
            util.mkdir(self._tmpDir + '/sources.list.d')

            #define opcoes apt
            apt_pkg.Config.Set("Dir::Etc::sourceparts", self._tmpDir + '/sources.list.d')
            apt_pkg.Config.Set("Dir::Etc::sourcelist", self._sourceList)
            apt_pkg.Config.Set("Dir::State::Lists", self._tmpDir) 
            
            cache = apt.Cache()
            try:
                res = cache.update(apt.progress.TextFetchProgress())
            except:
                return False
            
            return True
        except IOError:
            print "update: error\n"
            return False
    
    def clean(self):
        """
        Deletes all temporary files.
        """
        
        try:
            for root, dirs, files in os.walk(self._tmpDir):
                for name in files:
                    filename = os.path.join(root, name)
                    if os.path.isfile(filename):
                        os.remove(filename)
                            
            util.rmdir(self._tmpDir)
            
            return True
        except IOError:
            print "clean: error\n"
            return False
        
    def loadPackages(self, deleteFiles=False):
        """
        Reads the packages files that were fetched from the repository.
        """
        
        try:
            self._packages = []
            tmpListLine = []
            for root, dirs, files in os.walk(self._tmpDir):
                for name in files:       
                   filename = os.path.join(root, name)
                   if filename[-8:] == "Packages":
                       try:
                           tmpFile = open(filename, "r")
                           tmpData = tmpFile.read()
                           tmpListData = tmpData.split("Package: ")
                           tmpFilename = filename.split("_")
                           
                           for pkg in tmpListData:
                               if pkg != "":
                                   tmpSplitDesc = pkg.split("Description: ")
                                   tmpSplitDesc[1] = "Description: " + tmpSplitDesc[1]
                                   tmpGlobalInfo = tmpSplitDesc[0].split("\n")
                                   tmpGlobalInfo[0] = "Package: " + tmpGlobalInfo[0]
                                   tmpDic = util.list2dic(tmpGlobalInfo)
                                   #tmpDic['Description'] = tmpSplitDesc[1]
                                   tmpDic['ShortDesc'] = aptutil.getShortDesc(tmpSplitDesc[1])
                                   tmpDic['LongDesc'] = aptutil.getLongDesc(tmpSplitDesc[1])
                                   tmpDic['Installed'] = False
                                   self._packages.append(tmpDic)
                       except:
                           pass
            #remove os ficheiros na directorias e subdirectorias
            if deleteFiles:
                for root, dirs, files in os.walk(self._tmpDir):
                    for name in files:
                        filename = os.path.join(root, name)
                        if os.path.isfile(filename):
                            os.remove(filename)
                            
                util.rmdir(self._tmpDir)
            
            if len(self._packages) == 0:
                return False
            
            return True
        except IOError:
            print "loadPackages: error\n"
            return False
    
    def loadLocalKits(self):
        """
        Reads the packages files that are in the local dir.
        """
        
        try:
            self._localKits = []
            for root, dirs, files in os.walk(self._localDir):
                for name in files:       
                   filename = os.path.join(root, name)
                   #check if extension is .deb
                   tmpFilename = os.path.splitext(filename)
                   if tmpFilename[1] == ".deb":
                       try:
                           tmpDic = {}
                           controlFile = apt_inst.debExtractControl(open(filename))
                           sections = apt_pkg.ParseSection(controlFile)
                           #criar o dicionario
                           tmpDic['Installed'] = False
                           tmpDic['Package'] = sections["Package"]
                           tmpDic['Priority'] = sections["Priority"]
                           tmpDic['Section'] = sections["Section"]
                           tmpDic['Version'] = sections["Version"]
                           tmpDic['Architecture'] = sections["Architecture"]
                           tmpDic['Maintainer'] = sections["Maintainer"]
                           #tmpDic['Description'] = sections["Description"]
                           tmpDic['ShortDesc'] = aptutil.getShortDesc(sections["Description"])
                           tmpDic['LongDesc'] = aptutil.getLongDesc(sections["Description"])
                           tmpDic['Depends'] = aptutil.stripDepends(apt_pkg.ParseDepends(sections["Depends"]))
                           self._localKits.append(tmpDic)
                       except:
                           pass
            return True       
        except IOError:
            print "error\n"
            return False
    
    def setTmpDir(self, tmpDir):
        """
        Defines or redifines the local dir.
        """
        
        self._tmpDir = tmpDir
        
    def checkInstalled(self):
        """
        Checks witch packages are installed in the current system.
        """
        
        installedPackages = aptutil.readAptInstalled().split(", ")
        if installedPackages == []:
            return
        else:
            for value in self._packages:
                for pkg in installedPackages:
                    if value['Package'] == pkg:
                        value['Installed'] = True
        return
    
    def getPackages(self):
        """
        Returns the packages.
        """
        return self._packages
    
    def getLocalKits(self):
        """
        Returns the local packages.
        """
        return self._localKits
    
    def findPackages(self, strToFind, packageList):
        """
        Finds the packages that have a certain string.
        """
        
        matchingSearch = []
        for dic in packageList:
           if util.findStrInDic(strToFind, dic):
               matchingSearch.append(dic)
                
        return matchingSearch
    
    def getSections(self):
        """
        Returns the various sections that exist in the repository packages.
        """
        sections = ['all']
        for dic in self._packages:
                sections.append(dic['Section'])
                
        for dic in self._localKits:
                sections.append(dic['Section'])
        
        result = util.removeDuplicates(sections)
        return result
    
