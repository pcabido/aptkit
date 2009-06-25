import os, sys, string
from xml.dom import minidom, Node
    
class parseKit:
    def __init__(self, filename):
        """
        Initializes the kit xml class.
        """
        self._filename = filename
        self._Kit = {}
        self._kitPackages = []

    def writeKit(self, kitName, kitMaintainer, kitVersion, kitArch, kitSection, kitPriority, kitSDesc, kitLDesc, kitPostinst, kitFilename, kitPath, kitPackages):
        """
        Writes the data to a xml file.
        """
        doc = minidom.Document()
        
        kit = doc.createElement("kit")
        doc.appendChild(kit)
        
        control = doc.createElement("control")
        control.setAttribute("version", kitVersion)
        control.setAttribute("arch", kitArch)
        control.setAttribute("section", kitSection)
        control.setAttribute("priority", kitPriority)
        kit.appendChild(control)
        
        name = doc.createElement("kitName")
        control.appendChild(name)
        nameText = doc.createTextNode(kitName)
        name.appendChild(nameText)
        
        maintainer = doc.createElement("kitMaintainer")
        control.appendChild(maintainer)
        maintainerText = doc.createTextNode(kitMaintainer)
        maintainer.appendChild(maintainerText)
        
        sdesc = doc.createElement("kitSDesc")
        control.appendChild(sdesc)
        sdescText = doc.createTextNode(kitSDesc)
        sdesc.appendChild(sdescText)
        
        ldesc = doc.createElement("kitLDesc")
        control.appendChild(ldesc)
        ldescText = doc.createTextNode(kitLDesc)
        ldesc.appendChild(ldescText)
        
        postinst = doc.createElement("kitPostinst")
        control.appendChild(postinst)
        postinstText = doc.createTextNode(kitPostinst)
        postinst.appendChild(postinstText)
        
        filename = doc.createElement("kitFilename")
        control.appendChild(filename)
        filenameText = doc.createTextNode(kitFilename)
        filename.appendChild(filenameText)
        
        path = doc.createElement("kitPath")
        control.appendChild(path)
        pathText = doc.createTextNode(kitPath)
        path.appendChild(pathText)
        
        for pkg in kitPackages:
            package = doc.createElement("kitPackage")
            control.appendChild(package)
            packageText = doc.createTextNode(pkg)
            package.appendChild(packageText)
        
        try:
            if os.path.isfile(self._filename):
                os.remove(self._filename)
                
            fileKit = open(self._filename, "a")
            fileKit.write( doc.toprettyxml(indent="  ") )
        except IOError:
            return False
        
        return True
    
    def readKit(self, parent):
        """
        Reads the data from a xml file (auxiliar recursive function).
        """                             
        for node in parent.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                
                attrs = node.attributes                             
                for attrName in attrs.keys():
                    attrNode = attrs.get(attrName)
                    attrValue = attrNode.nodeValue
                    self._Kit[attrName] = attrValue
                
                content = []                                        
                for child in node.childNodes:
                    if child.nodeType == Node.TEXT_NODE:
                        content.append(child.nodeValue)
                        if content and (node.nodeName != "control" and node.nodeName != "kitPackage"):
                            strContent = string.join(content)
                            tmpContent = strContent.replace("\n      ", "")
                            self._Kit[node.nodeName] = tmpContent.replace("\n    ", "")
                        if content and node.nodeName == "kitPackage":
                            strContent = string.join(content)
                            tmpContent = strContent.replace("\n      ", "")
                            self._kitPackages.append(tmpContent.replace("\n    ", ""))
                            
                self.readKit(node)

    def getKit(self):
        """
        Reads the data from a xml file.
        """ 
        try:                                             
            doc = minidom.parse(self._filename)
            rootNode = doc.documentElement
            self.readKit(rootNode)
            
            self._Kit['Depends'] = self._kitPackages
            
            return self._Kit
        except:
            return False

             