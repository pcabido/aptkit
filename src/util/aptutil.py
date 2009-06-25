# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)

import apt_inst
import apt_pkg
import commands
import sys
from progress import TextProgress

#ver mais tarde
apt_pkg.init()

#le a cache e ve quais os pacotes que estão instalados
def readAptInstalled():
    """
    Returns a string with all the packages installed in the system.
    """
    progress = TextProgress()
    cache = apt_pkg.GetCache(progress)
    packages = cache.Packages
    
    systemDepends= ""
    for package in packages:
            if  package.CurrentVer != None:
                    systemDepends += package.Name + ", "
    
    if len(systemDepends) > 2:
        return systemDepends[:-2]
    else:
        return ""
    
def readAptInstalled2List():
    """
    Returns a list with all the packages installed in the system.
    """
    progress = TextProgress()
    cache = apt_pkg.GetCache(progress)
    packages = cache.Packages
    
    systemDepends= []
    for package in packages:
            if  package.CurrentVer != None:
                    systemDepends.append(package.Name)
    
    return systemDepends

#obtem todos os pacotes disponiveis
def getCachePackages(ignore=True):
    """
    Returns all packages available in the cache.
    """
    progress = TextProgress()
    cache = apt_pkg.GetCache(progress)
    records = apt_pkg.GetPkgRecords(cache)
    packages = cache.Packages
        
    pkgList = []
    
    for pkg in packages:
        for pkgInfo in pkg.VersionList:
            for packFile, index in pkgInfo.FileList:
                records.Lookup((packFile,index))
                if packFile.IndexType != 'Debian Package Index' and ignore:
                    continue
                pkgList.append([None, pkg.Name, pkgInfo.VerStr, records.ShortDesc])
    
    pkgList.sort()
    return pkgList

#problemas ao ler um ficheiro q tem espaços no path
def pkgInfo(package, info):
    """
    Returns the info for a certain package section.
    """
    try:
        controlFile = apt_inst.debExtractControl(open(package))
        sections = apt_pkg.ParseSection(controlFile)
        
        if info == "Depends":
            return  apt_pkg.ParseDepends(sections["Depends"])
        else:
            return sections[info]
    except:
        return ""

def isInstalled(package, file=True):
    """
    Checks if the package is installed.
    """
    try:
        if file:
            pkg = pkgInfo(package, 'Package')
        else:
            pkg = package

        dpkg_query  = commands.getoutput('dpkg-query --show ' + pkg)
        
        if (dpkg_query[0:len(pkg)] == pkg):
            versionInstalled = dpkg_query.split('\t')[1]
            if not versionInstalled: return False
            return True
        else:
            return False
    except:
        return False
        
def equalVersion(package):
    """
    Compares the version between two packages, the new and the installed.
    """
    try:
        pkg = pkgInfo(package, 'Package')
        installed = isInstalled(pkg)
        if not installed: return False
    
        dpkg_query = commands.getoutput('dpkg-query --show ' + pkg)
     
        versionInstalled = dpkg_query.split('\t')[1]
        versionInPackage = pkgInfo(package, 'Version')
        if versionInPackage == versionInstalled:
            return True
        return False
    except:
        return False
            
def upgradable(package):
    """
    Checks if the package is upgradable.
    """
    try:
        pkg = pkgInfo(package, 'Package')
        if  (not isInstalled(pkg)) or equalVersion(pkg): return False
        
        dpkg_query = commands.getoutput('dpkg-query --show ' + pkg)
        versionInstalled = dpkg_query.split('\t')[1]
        versionInPackage = pkgInfo(package, 'Version')
        
        ltC ='if dpkg --compare-versions "'+ versionInstalled  + '" lt "' + \
        versionInPackage + '";then echo yes; fi '
        if commands.getoutput(ltC) == 'yes':
            return True
        return False
    except:
        return False

def install(package):
    """
    Installs a package.
    """
    #dpkg_install = commands.getoutput("gksu 'gdebi -n -q %s'" %(package.replace(" ", "\ ")))
    dpkg_install = commands.getoutput("gksu 'dpkg -i %s' " %(package.replace(" ", "\ ")))
    if len(dpkg_install.split("\n")) > 1:
        isSuccess = isInstalled(package)
        if isSuccess:
            return True
        else:
            return False
    else:
        return False

#o apt_pkg.ParseDepends devolve uma lista, de listas, com tuplos
#ex:  [[('dep1', '', '')], [('dep2', '', '')], [('dep3', '', '')]]
def stripDepends(depList):
    """
    Converts from a list of lists of tuples to a string.
    """
    depResult = ""
    for L in depList:
        for tuplo in L:
                if tuplo[0] != "" and tuplo[1] == "":
                    depResult += tuplo[0] + ", "
                elif tuplo[0] != "" and tuplo[1] != "":
                    depResult += tuplo[0] + " (" + tuplo[2] + " " + tuplo[1] + "), "
    
    if len(depResult) > 2:
        return depResult[:-2]
    else:
        return ""

#define a descrição para o control file
def setDescription(SDesc, LDesc):
    """
    Sets the description for the control file.
    """
    Desc = SDesc + "\n .\n"
    tmpLDesc = LDesc.split("\n")
    for e in tmpLDesc:
        if e == "":
            Desc += " .\n"
        else:
            Desc += " " + e + "\n"
    
    return Desc

def getDependsFromDic(Dic):
    """
    Sets the short (synopsis) description for the control file.
    """
    
    depends = ""
    for key, value in Dic.items():
        depends += key + ", "
        
    if len(depends) > 2:
        return depends[:-2]
    else:
        return ""
    
def getDependsFromList(list):
    """
    Converts the dependency list to a string
    """
    depends = ""
    for l in list:
        depends += l + ", "
        
    if len(depends) > 2:
        return depends[:-2]
    else:
        return ""

def getShortDesc(desc):
    """
    From the description, returns the short (synopsis) description.
    """
    if desc:
        try:
            tmpDesc = desc.split("\n")
            if "Description: " in tmpDesc[0]:
                finalDesc = tmpDesc[0].split("Description: ")
            else:
                return tmpDesc[0]
            return finalDesc[1]
        except:
            return ""
    else:
        return ""
    
def getLongDesc(desc):
    """
    From the description, returns the long description.
    """
    final = ""
    if desc:
        try:
            tmpDesc = desc.split("\n")
            if len(tmpDesc) > 1:
                for i in range(len(tmpDesc) - 1):
                    final += tmpDesc[i+1] + "\n"
            return final
        except:
            return ""
    else:
        return ""
    
def getLongDescFromKit(desc):
    """
    Gets the long description from a kit.
    """
    final = ""
    if desc:
        try:
            tmpDesc = desc.split("\n")
            i=0
            for line in tmpDesc:
                if i == 0 or i == 1:
                    pass
                else:
                    if line[0] == " ":
                        final += line[1:]
                    else:
                        final += line
                    
                    if i < len(tmpDesc)-1:
                        final += "\n"
                i += 1
                
            return final
        except:
            return ""
    else:
        return ""

def shortDescFromDic(list, pkg, ver):
    """
    Gets the short description from a dictionary.
    """
    for dic in list:
        if dic['Package'] == pkg and dic['Version'] == ver:
            return dic['ShortDesc']
        
    return ""

def longDescFromDic(list, pkg, ver):
    """
    Gets the long description from a dictionary.
    """
    for dic in list:
        if dic['Package'] == pkg and dic['Version'] == ver:
            return dic['LongDesc']
    
    return ""

def getSectionPackages(section, list):
    """
    Returns all sections that are in the package (dictionary) list.
    """
    Packages = []
    for dic in list:
        if dic['Section'] == section:
            Packages.append(dic)
    return Packages