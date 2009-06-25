# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)
import apt_inst
import apt_pkg
import os
import shutil
import sys
from src.util import util, aptutil

def readMetapackageFile(filename):
    """
    Reads a metapackage file and returns a dictionary with the values.
    """
    
    try:
        metapackage = {}
        controlFile = apt_inst.debExtractControl(open(filename))
        sections = apt_pkg.ParseSection(controlFile)
        
        depends = aptutil.stripDepends(apt_pkg.ParseDepends(sections["Depends"])).split(", ")
        
        #obter o postinst se existir
        
        #tratar as varias sections e criar o metapackage com os dados obtidos
        metapackage['Package'] = sections["Package"]
        metapackage['Priority'] = sections["Priority"]
        metapackage['Section'] = sections["Section"]
        metapackage['Version'] = sections["Version"]
        metapackage['Architecture'] = sections["Architecture"]
        metapackage['Maintainer'] = sections["Maintainer"]
        metapackage['Description'] = sections["Description"]
        metapackage['Depends'] = depends
        
        return metapackage
    except:
        print "readMetapackageFile: error\n"
        return {}           

class metapackage:
    
    def __init__(self, filename="", path="", Name="", Priority="", Section="", Version="", Arch="", Maintainer="", SDescription="", LDescription="", Description="", Depends="", postinst=""):
        """
        Initializes the metapackage.
        """
        
        #assumo que o filename ja foi passado correctamente (ex. <foo>_<VersionNumber>-<DebianRevisionNumber>_<DebianArchitecture>)
        self._filename = filename
        self._path = path
        
        #control file data
        self._Name = Name
        self._Priority = Priority
        self._Section = Section
        self._Version = Version
        self._Architecture = Arch
        self._Maintainer = Maintainer
        #contem uma lista com as dependencias
        self._Depends = Depends
        
        self._postinst = postinst
        
        self._ShortDescription = SDescription
        self._LongDescription = LDescription
        
        if Description == "":
            self._Description = self._ShortDescription + "\n " + self._LongDescription
        else:
            self._Description = Description
    
    #gets
    def getFilename(self):
        return self._filename
    
    def getPath(self):
        return self._path
    
    def getName(self):
        return self._Name
    
    def getPriority(self):
        return self._Priority
    
    def getSection(self):
        return self._Section
    
    def getVersion(self):
        return self._Version
    
    def getArch(self):
        return self._Architecture
    
    def getMaintainer(self):
        return self._Maintainer
        
    def getSDescription(self):
        return self._ShortDescription
    
    def getLDescription(self):
        return self._LongDescription
    
    def getDescription(self):
        return self._Description
    
    def getDepends(self):
        return self._Depends
    
    
    #sets
    def setFilename(self,mtpkgval):
        self._filename = mtpkgval
        
    def setName(self,mtpkgval):
        self._Name = mtpkgval
    
    def setPriority(self,mtpkgval):
        self._Priority = mtpkgval    
        
    def setSection(self,mtpkgval):
        self._Section = mtpkgval
        
    def setVersion(self,mtpkgval):
        self._Version = mtpkgval
        
    def setArch(self,mtpkgval):
        self._Architecture = mtpkgval
        
    def setMaintainer(self,mtpkgval):
        self._Maintainer = mtpkgval
        
    def setSDescription(self,mtpkgval):
        self._ShortDescription = mtpkgval
    
    def setLDescription(self,mtpkgval):
        self._LongDescription = mtpkgval
    
    def setDescription(self,mtpkgSD, mtpkgLD):
        self._Description = mtpkgSD + mtpkgLD
    
    def setDepends(self, mtpkgval):
        self._Depends = mtpkgval
    
    def setPostinst(self, mtpkgval):
        self._postinst = mtpkgval
    
    def appendPkg(self, mtpkgval):
        self._Depends += (", " + mtpkgval)
        
           
    def createBaseFiles(self, tmpDir):
        """
        Creates the control and postinstall in order to build the metapackage.
        """
        
        try:
            #define e cria a dir temporaria pq do metapackage
            #tmpmtpkgDir = tmpDir + "/metapackage"
            util.mkdir(tmpDir)
            util.mkdir(tmpDir + '/DEBIAN')
        
            #escreve o control file
            controlFile = tmpDir + '/DEBIAN/control'
            cFile = open(controlFile, "a")
            cFile.write ("Package: " + self._Name \
            + "\nPriority: " + self._Priority \
            + "\nSection: " + self._Section \
            + "\nVersion: " + self._Version \
            + "\nArchitecture: " + self._Architecture \
            + "\nMaintainer: " + self._Maintainer \
            + "\nDepends: " + self._Depends \
            + "\nDescription: " + self._Description + "\n")
            
            #escrever o postinst caso haja algo para escrever
            if self._postinst != "":
                postinstFile = tmpDir + '/DEBIAN/postinst'
                pFile = open(postinstFile, "a")
                pFile.write(self._postinst + "\n")
            
                result = os.system('chmod 755 ' + postinstFile + ' > /dev/null 2> /dev/null')
                if result != 0:
                    return False
            
            return True
        except IOError:
            print "createBaseFiles: error\n"
            return False
        
    def generateMetapackage(self, tmpDirRoot, tmpDir):
        """
        Generates (builds) the metapackage.
        """
        
        try:
            #ok, so falta criar o metapackage
            #mudar para o os.popen(...).read()
            result = os.system('dpkg-deb -b ' + tmpDir.replace(' ','\ ') + ' ' + self._path.replace(' ','\ ')  + self._filename + ' > /dev/null 2> /dev/null')
            
            #limpa a tmpdir
            if os.path.isfile(tmpDir + '/DEBIAN/control'):
                os.remove(tmpDir + '/DEBIAN/control')
            if os.path.isfile(tmpDir + '/DEBIAN/postinst'):
                os.remove(tmpDir + '/DEBIAN/postinst')
            # pode ser preciso fazer uma funcao à parte para tratar esta linha (try: ... except: pass)
            util.rmdir(tmpDirRoot)
            
            if result != 0:
                return False
            else:
                return True
        except IOError:
            print "generateMetapackage: error\n"
            return False