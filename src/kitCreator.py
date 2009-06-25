# -*- coding: utf-8 -*-
from metapackagehandler import mtpkgHandler

import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import os
import sys
import gobject
import gettext

import apt
import apt_pkg

from time import strftime
from util import util, aptutil, xmlutil
from util import SearchWidget
from data import sections
from gettext import textdomain, gettext as _

__title__ = _("Kits Creator")
__version__ = "0.1b"
__comments__ = _("GTK frontend for Kits Creator.")
__authors__= ["Paulo Cabido <paulo.cabido@gmail.com>"]
__copyright__ = "Paulo Cabido"
__license__ = _("GNU GPL v3")
__appname__ = "kitcreator"


#main function
class kitCreatorGTK:
    
    def delete(self, widget, event, data=None):
        """
        Exits gtk.
        """
        
        gtk.main_quit()
        return False
    
    def loadImage(self, image, path):
        """
        Sets a image.
        """
        
        try:
            image.set_from_file(path)
            return True
        except:
            pass
            return False
    
    def errorDialog(self, header, msg):
         """
         Show an error message.
         """

         dialog = gtk.MessageDialog(parent=self.window,
                               flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_ERROR,
                               buttons=gtk.BUTTONS_CLOSE)
         dialog.set_title("")
         dialog.set_icon(self.icon)
         dialog.set_markup("<big><b>%s</b></big>\n\n%s" % (header, msg))
         dialog.realize()
         #dialog.window.set_functions(gtk.gdk.FUNC_MOVE)
         dialog.run()
         dialog.destroy()
    
    def sucessDialog(self, header, msg):
        """
        Show an sucess message.
        """

        dialog = gtk.MessageDialog(parent=self.window,
                               flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_INFO,
                               buttons=gtk.BUTTONS_CLOSE)
        dialog.set_title("")
        dialog.set_icon(self.icon)
        dialog.set_markup("<big><b>%s</b></big>\n\n%s" % (header, msg))
        dialog.realize()
        #dialog.window.set_functions(gtk.gdk.FUNC_MOVE)
        dialog.run()
        dialog.destroy()
        
    def initProgressDialog(self, msg):
        self.dialogProgress.realize()
        self.dialogProgress.set_transient_for(self.window)
        self.pbar.set_fraction(0)
        self.lblMessage.set_label(msg)
        self.dialogProgress.window.set_functions(gtk.gdk.FUNC_MOVE)
        self.dialogProgress.set_icon(self.icon)
        self.dialogProgress.show()
#
# Package list
#        
    def setupPackageList(self, ignore=True):
        """
        Creates the package list from the current system cache.
        """
        
        self.initProgressDialog(_("<big><b>Generating the package list.</b></big>"))
        self.window.set_sensitive(False)
        while gtk.events_pending():
                    gtk.main_iteration()
        
        self.pkgCache = aptutil.getCachePackages()        
        
        self.pkgCache.sort()
        self.pkgCache = util.removeDuplicates(self.pkgCache)
        
        fraction = (1.0/len(self.pkgCache))
        progress=0
        setFraction = 0
        for elm in self.pkgCache:
            self.listStore.append(elm)
            while gtk.events_pending():
                    gtk.main_iteration()
            if (progress + fraction) <= 1:
                progress += fraction
                if setFraction != util.pbarValue(progress):
                    setFraction = util.pbarValue(progress)
                    self.pbar.set_fraction(setFraction)
        
        self.rendererText = gtk.CellRendererText()
        
        self.rendererToggle = gtk.CellRendererToggle()
        self.rendererToggle.set_property('activatable', True)
        self.rendererToggle.connect('toggled', self.colToggledClicked, self.listStore)
        
        self.colToggle = gtk.TreeViewColumn("", self.rendererToggle )
        self.colToggle.add_attribute( self.rendererToggle, "active", 0)
        
        self.treeview.append_column(self.colToggle)
        
        colPacote = gtk.TreeViewColumn(_("Package"), self.rendererText, text=1)
        colPacote.set_resizable(True)
        colPacote.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        colPacote.set_fixed_width( 125 )
        #colPacote.set_sort_column_id(1)
        
        colVersion = gtk.TreeViewColumn(_("Version"), self.rendererText, text=2)
        colVersion.set_resizable(True)
        colVersion.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        colVersion.set_fixed_width( 125 )
        #colVersion.set_sort_column_id(2)
        
        colDesc = gtk.TreeViewColumn(_("Description"), self.rendererText, text=3)
        colDesc.set_resizable(True)
        colDesc.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        colDesc.set_fixed_width( 350 )
        #colDesc.set_sort_column_id(3)
        
        self.treeview.append_column(colPacote)
        self.treeview.append_column(colVersion)
        self.treeview.append_column(colDesc)
        
        self.treeview.set_model(self.listStore)
        self.treeview.set_search_column(1)
        
        self.dialogProgress.hide()
        self.window.set_sensitive(True)
        return True
        
    def colToggledClicked( self, cell, path, model ):
        """
        Sets the toggled state on the toggle button to true or false.
        """

        if self.setListStoreSearch:
                model = self.listStoreSearch
         
        model[path][0] = not model[path][0]
        if model[path][0]:
            #add version here
            self.packageList[model[path][1]] = model[path][2]
    
            util.changePackageListValue(self.pkgCache,
                                        1, model[path][1],
                                        2, model[path][2], 
                                        0, model[path][0])
        else:
            del self.packageList[model[path][1]]
            util.changePackageListValue(self.pkgCache,
                                        1, model[path][1],
                                        2, model[path][2],
                                        0, model[path][0])
            
        return
    
    def searchPackageList(self, widget, query):
        """
        Searches the packages list and sets the Treeview with the results.
        """
        self.listStoreSearch = gtk.ListStore(gobject.TYPE_BOOLEAN, str, str, str)
        
        if query:
            for elm in self.pkgCache:
                if (query in elm[1]) or (query in elm[2]) or (query in elm[3]):
                    self.listStoreSearch.append(elm)
                    
            self.treeview.set_model(self.listStoreSearch)
            self.treeview.set_search_column(1)
            self.setListStoreSearch = True
        else:
            self.listStore.clear()
            for elm in self.pkgCache:
                if (query in elm[1]) or (query in elm[2]) or (query in elm[3]):
                    self.listStore.append(elm)
                    
            self.treeview.set_model(self.listStore)
            self.treeview.set_search_column(1)
            self.setListStoreSearch = False
            
        return True
#
# aboutdialog
#
    def closeAbout(self, widget, data=None):
        """
        Closes the about dialog.
        """
        self.aboutDialog.hide()
        return True
    
    def showAbout(self, widget, data=None):
        """
        Create the about dialog.
        @param widget: Current widget
        @type widget: gtk widget
        """
        
        self.aboutDialog = self.wTree.get_widget("aboutdialogCriarkits")
        self.aboutDialog.set_name(_(__title__))
        self.aboutDialog.set_version(__version__)
        self.aboutDialog.set_comments(_(__comments__))
        self.aboutDialog.set_copyright(__copyright__)
        self.aboutDialog.set_authors(__authors__)
        self.aboutDialog.set_license(_(__license__))
        self.aboutDialog.set_logo(self.icon)
        self.aboutDialog.set_icon(self.icon)
        self.aboutDialog.set_transient_for(self.window)
        
        self.aboutDialog.connect("destroy", self.closeAbout)
        self.aboutDialog.connect("delete_event", self.closeAbout)
        self.aboutDialog.connect("response", self.closeAbout)
        self.aboutDialog.show()
        return True
    
#
#funcoes relacionadas com os metapacotes
#
    def resetFields(self, widget, data=None):
        """
        Resets all fields 
        """
        self.entryFilename.set_text("")
        self.entryName.set_text("")
        self.cmbPriority.set_active(0)
        self.cmbSection.set_active(0)
        self.entryVersion.set_text("")
        self.cmbArch.set_active(0)
        self.entryMaintainer.set_text("")
        self.entrySDesc.set_text("")
        self.textviewLDesc.get_buffer().set_text("")
        self.textPostinst.get_buffer().set_text("")
        
        self.packageList = {}
        self.listStore.clear()
        for val in self.pkgCache:
                if val[0]:
                    val[0] = False
                self.listStore.append(val)
                    
        self.treeview.set_model(self.listStore)
        self.treeview.set_search_column(1)
        return True
    
    def createSystemKit(self, widget, data=None):
        """
        Fills the data with the packages installed in the current system
        """
        
        self.initProgressDialog(_("<big><b>Checking the system for installed packages.</b></big>"))
        self.window.set_sensitive(False)
        
        installedPackages = aptutil.readAptInstalled2List()
        item = self.listStore.get_iter_first()
        fraction = (1.0/len(self.pkgCache))
        progress = 0
        setFraction = 0
        while ( item != None ):
            for pkg in installedPackages:
                if self.listStore.get_value(item, 1) == pkg:
                    self.listStore.set_value(item, 0, True)
                    util.changePackageListValue(self.pkgCache, 
                                        1, self.listStore.get_value(item, 1),
                                        2, self.listStore.get_value(item, 2),
                                        0, self.listStore.get_value(item, 0))
                    break
            item = self.listStore.iter_next(item)
            while gtk.events_pending():
                    gtk.main_iteration()
            if (progress + fraction) <= 1:
                progress += fraction
                if setFraction != util.pbarValue(progress, 10):
                    setFraction = util.pbarValue(progress, 10)
                    self.pbar.set_fraction(setFraction)
        
        timestamp = strftime("%Y%m%d%H%M")
        if not self.entryFilename.get_text():
            self.entryFilename.set_text("Kit-SystemBackup_" + timestamp + ".deb")
        
        if not self.entryName.get_text():
            self.entryName.set_text("Kit-SystemBackup")
        #self.cmbPriority.set_active(3)
        if not self.entrySDesc.get_text():
            self.entrySDesc.set_text(_("System/backup Kit"))
        
        start = self.textviewLDesc.get_buffer().get_start_iter()
        end = self.textviewLDesc.get_buffer().get_end_iter()
        if not self.textviewLDesc.get_buffer().get_text(start, end, True):
            stime = strftime("%d-%m-%Y")
            self.textviewLDesc.get_buffer().set_text(_("System state (backup) %s.\n"
                                                       "This Kit restores or duplicates the system state.") % stime)
        
        self.dialogProgress.hide()
        self.window.set_sensitive(True)
        
        return True
    
    def openKit(self, widget, data=None):
        """
        Opens a saved kit (xml or deb)
        """
        
        dialog = gtk.FileChooserDialog(_("Open Kit"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("Kits")
        filter.add_pattern("*.kit")
        filter.add_pattern("*.deb")
        dialog.add_filter(filter)
        
        response = dialog.run()
        kitType = ""
        if response == gtk.RESPONSE_OK:
            kitFile = dialog.get_filename()
            tmpKitFile = os.path.splitext(kitFile)
            
            if tmpKitFile[1] != "":
                if tmpKitFile[1] == ".deb":
                    kitType = "deb"
                elif tmpKitFile[1] == ".kit":
                    kitType = "xml"
                else:
                    print "error"
        elif response == gtk.RESPONSE_CANCEL:
            dialog.destroy()
            return
        else:
            dialog.destroy()
            return
        
        dialog.destroy()
    
        if kitType == "deb":
            #####
            self.initProgressDialog(_("<big><b>Checking Kit packages.</b></big>"))
            self.window.set_sensitive(False)
            
            while gtk.events_pending():
                gtk.main_iteration()
            self.resetFields(None)
            
            kitDic = mtpkgHandler.readMetapackageFile(kitFile)
            #preencher os campos
            self.entryName.set_text(kitDic['Package'])
            
            while gtk.events_pending():
                gtk.main_iteration()
            tmpModel = self.cmbPriority.get_model()
            item = tmpModel.get_iter_first()
            i=-1
            self.cmbPriority.set_active(i)
            while ( item != None ):
                i += 1
                if tmpModel.get_value (item, 0) == kitDic['Priority']:
                    self.cmbPriority.set_active(i)
                    break
                item = tmpModel.iter_next(item)
            
            tmpModel = self.cmbSection.get_model()
            item = tmpModel.get_iter_first()
            i=-1
            self.cmbSection.set_active(i)
            while ( item != None ):
                i += 1
                if tmpModel.get_value (item, 0) == _(self.sections[kitDic['Section']]):
                    self.cmbSection.set_active(i)
                    break
                item = tmpModel.iter_next(item)
            
            self.entryVersion.set_text(kitDic['Version'])
            
            tmpModel = self.cmbArch.get_model()
            item = tmpModel.get_iter_first()
            i=-1
            self.cmbArch.set_active(i)
            while ( item != None ):
                i += 1
                if tmpModel.get_value (item, 0) == kitDic['Architecture']:
                    self.cmbArch.set_active(i)
                    break
                item = tmpModel.iter_next(item)
            
            self.entryMaintainer.set_text(kitDic['Maintainer'])
            self.entrySDesc.set_text( aptutil.getShortDesc(kitDic['Description']) )
            
            try:
                ldesc = aptutil.getLongDescFromKit(kitDic['Description']).replace(".\n", "\n")
                self.textviewLDesc.get_buffer().set_text(ldesc)
            except:
                pass
            
            self.entryFilename.set_text(kitFile.split("/")[len(kitFile.split("/"))-1])
            
            installedPackages = aptutil.readAptInstalled2List()
            item = self.listStore.get_iter_first()
            fraction = (1.0/len(self.pkgCache))
            progress = 0
            setFraction = 0
            while ( item != None ):
                for pkg in kitDic['Depends']:
                    if self.listStore.get_value(item, 1) == pkg:
                        self.listStore.set_value(item, 0, True)
                        util.changePackageListValue(self.pkgCache, 
                                        1, self.listStore.get_value(item, 1),
                                        2, self.listStore.get_value(item, 2),
                                        0, self.listStore.get_value(item, 0))
                item = self.listStore.iter_next(item)
                while gtk.events_pending():
                        gtk.main_iteration()
                if (progress + fraction) <= 1:
                    progress += fraction
                    if setFraction != util.pbarValue(progress):
                        setFraction = util.pbarValue(progress)
                        self.pbar.set_fraction(setFraction)
                        
            self.dialogProgress.hide()
            self.window.set_sensitive(True)
            #####
        elif kitType == "xml":
            #####
            self.initProgressDialog(_("<big><b>Checking Kit packages.</b></big>"))
            self.window.set_sensitive(False)
            
            while gtk.events_pending():
                gtk.main_iteration()
            self.resetFields(None)
            
            xmlKit = xmlutil.parseKit(kitFile)
            kitDic = xmlKit.getKit()
            
            print kitDic['section']
            
            self.entryFilename.set_text(kitDic['kitFilename'])
            self.entryName.set_text(kitDic['kitName'])
            
            while gtk.events_pending():
                gtk.main_iteration()
            tmpModel = self.cmbPriority.get_model()
            item = tmpModel.get_iter_first()
            i=-1
            self.cmbPriority.set_active(i)
            while ( item != None ):
                i += 1
                if tmpModel.get_value (item, 0) == kitDic['priority']:
                    self.cmbPriority.set_active(i)
                    break
                item = tmpModel.iter_next(item)
            
            tmpModel = self.cmbSection.get_model()
            item = tmpModel.get_iter_first()
            i=-1
            self.cmbSection.set_active(i)
            while ( item != None ):
                i += 1
                if tmpModel.get_value (item, 0) == kitDic['section']:
                    self.cmbSection.set_active(i)
                    break
                item = tmpModel.iter_next(item)
            
            self.entryVersion.set_text(kitDic['version'])
            
            tmpModel = self.cmbArch.get_model()
            item = tmpModel.get_iter_first()
            i=-1
            self.cmbArch.set_active(i)
            while ( item != None ):
                i += 1
                if tmpModel.get_value (item, 0) == kitDic['arch']:
                    self.cmbArch.set_active(i)
                    break
                item = tmpModel.iter_next(item)
            
            self.entryMaintainer.set_text(kitDic['kitMaintainer'])
            self.entrySDesc.set_text(kitDic['kitSDesc'])
            self.textviewLDesc.get_buffer().set_text(kitDic['kitLDesc'])
            self.textPostinst.get_buffer().set_text(kitDic['kitPostinst'])
            
            installedPackages = aptutil.readAptInstalled2List()
            item = self.listStore.get_iter_first()
            fraction = (1.0/len(self.pkgCache))
            progress = 0
            setFraction = 0
            while ( item != None ):
                for pkg in kitDic['Depends']:
                    if self.listStore.get_value(item, 1) == pkg:
                        self.listStore.set_value(item, 0, True)
                        util.changePackageListValue(self.pkgCache, 
                                        1, self.listStore.get_value(item, 1),
                                        2, self.listStore.get_value(item, 2),
                                        0, self.listStore.get_value(item, 0))
                item = self.listStore.iter_next(item)
                while gtk.events_pending():
                        gtk.main_iteration()
                if (progress + fraction) <= 1:
                    progress += fraction
                    if setFraction != util.pbarValue(progress):
                        setFraction = util.pbarValue(progress)
                        self.pbar.set_fraction(setFraction)
                        
            self.dialogProgress.hide()
            self.window.set_sensitive(True)
            #####
        else:
            pass
        
        return True
        
    def saveKit(self, widget, data=None):
        """
        Saves the current work to a xml file
        """
        
        dialog = gtk.FileChooserDialog(_("Save Kit"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("Kits")
        filter.add_pattern("*.kit")
        filter.add_pattern("*.deb")
        dialog.add_filter(filter)
        
        response = dialog.run()
        
        if response == gtk.RESPONSE_OK:
            kitFile = os.path.splitext(dialog.get_filename())
            if kitFile[1] == ".kit":
                tmpKitFile = kitFile[0] + kitFile[1]
            else:
                tmpKitFile = kitFile[0] + ".kit"
        elif response == gtk.RESPONSE_CANCEL:
            dialog.destroy()
            return
        else:
            dialog.destroy()
            return
        
        dialog.destroy()
        
        xmlKit = xmlutil.parseKit(tmpKitFile.replace(" ", "-"))
        
        start = self.textviewLDesc.get_buffer().get_start_iter()
        end = self.textviewLDesc.get_buffer().get_end_iter()
        ldesc = self.textviewLDesc.get_buffer().get_text(start,end, True)
        
        start = self.textPostinst.get_buffer().get_start_iter()
        end = self.textPostinst.get_buffer().get_end_iter()
        postinst = self.textPostinst.get_buffer().get_text(start,end, True)
        
        #####
        depends = []
        self.initProgressDialog(_("<big><b>Checking selected packages.</b></big>"))
        self.window.set_sensitive(False)
        
        installedPackages = aptutil.readAptInstalled2List()
        item = self.listStore.get_iter_first()
        fraction = (1.0/len(self.pkgCache))
        progress = 0
        setFraction = 0
        while ( item != None ):
            if self.listStore.get_value(item, 0):
                depends.append(self.listStore.get_value(item, 1))
            item = self.listStore.iter_next(item)
            while gtk.events_pending():
                    gtk.main_iteration()
            if (progress + fraction) <= 1:
                progress += fraction
                if setFraction != util.pbarValue(progress):
                    setFraction = util.pbarValue(progress)
                    self.pbar.set_fraction(setFraction)
                    
        self.dialogProgress.hide()
        self.window.set_sensitive(True)
        #####
        
        result = xmlKit.writeKit(self.entryName.get_text(),
                                 self.entryMaintainer.get_text(),
                                 self.entryVersion.get_text(),
                                 self.cmbArch.get_active_text(),
                                 self.cmbSection.get_active_text(),
                                 self.cmbPriority.get_active_text(),
                                 self.entrySDesc.get_text(),
                                 ldesc,
                                 postinst,
                                 self.entryFilename.get_text(),
                                 self.buttonPath.get_filename(),
                                 depends)
        if not result:
            #TODO: error dialog 
            print "saveKit: erro"
            return False
        
        return True
  
    def generateMetapackage(self, widget, data=None):
        """
        Generates the kit
        """
        
        self.entrySearchbox.set_text("")
        
        tmpFilename = os.path.splitext(self.entryFilename.get_text())
        self._filename = tmpFilename[0]
        if not self._filename:
            self.errorDialog(_("File name"), 
                             _("The file name must be defined."))
            self.entryFilename.grab_focus()
            return False
        else:
            if tmpFilename[1] != "":
                if tmpFilename[1] == ".deb":
                    self._filename.replace(' ','-')
                    self._filename += tmpFilename[1]
                else:
                    self._filename.replace(' ','-')
                    self._filename += tmpFilename[1] + ".deb"
            else:
                self._filename.replace(' ','-')
                self._filename += ".deb"
            self.entryFilename.set_text(self._filename)
        
        self._path = self.buttonPath.get_filename()
        if not self._path:
            self.errorDialog(_("Location"), 
                             _("The location where to save the Kit must be defined."))
            self.buttonPath.grab_focus()
            return False
        else:
            self._path.replace(' ','\ ')
        
        self._name = self.entryName.get_text().lower()
        if not self._name:
            self.errorDialog(_("Kit Name"), 
                             _("The Kit name must be defined."))
            self.notebook.set_current_page(0)
            self.entryName.grab_focus()
            return False
        elif util.iligalChars(self._name):
            self.errorDialog(_("Kit Name"), 
                             _("The Kit name has illegal characters."))
            self.notebook.set_current_page(0)
            self.entryName.grab_focus()
            return False
        else:
            self._name.replace(' ','-')
        
        self._priority = self.cmbPriority.get_active_text()
        if not self._priority:
            self.errorDialog(_("Kit Priority"), 
                             _("The Kit priority must be defined."))
            self.notebook.set_current_page(0)
            self.cmbPriority.grab_focus()
            return False
        
        self._section = ""
        for key, value in self.sections.items():
            if _(self.sections[key]) == self.cmbSection.get_active_text():
                self._section = key
                break
                
        if not self._section:
            self.errorDialog(_("Kit Section"), 
                             _("The Kit section must be defined."))
            self.notebook.set_current_page(0)
            self.cmbSection.grab_focus()
            return False
        
        self._version = self.entryVersion.get_text()
        if not self._version:
            self.errorDialog(_("Kit Version"), 
                             _("The Kit version must be defined."))
            self.notebook.set_current_page(0)
            self.entryVersion.grab_focus()
            return False
        elif util.iligalChars(self._version):
            self.errorDialog(_("Kit Version"), 
                             _("The Kit version has illegal characters."))
            self.notebook.set_current_page(0)
            self.entryVersion.grab_focus()
            return False
        
        self._arch = self.cmbArch.get_active_text()
        if not self._arch:
            self.errorDialog(_("Kit Architecture"), 
                             _("The Kit architecture must be defined."))
            self.notebook.set_current_page(0)
            self.cmbArch.grab_focus()
            return False
        
        self._maintainer = self.entryMaintainer.get_text()
        if not self._maintainer:
            self.errorDialog(_("Kit Maintainer"), 
                             _("The Kit maintainer must be defined."))
            self.notebook.set_current_page(0)
            self.entryMaintainer.grab_focus()
            return False
        elif util.iligalChars(self._maintainer, [':']):
            self.errorDialog(_("Kit Maintainer"), 
                             _("The Kit maintainer has illegal characters."))
            self.notebook.set_current_page(0)
            self.entryMaintainer.grab_focus()
            return False
            
        start = self.textviewLDesc.get_buffer().get_start_iter()
        end = self.textviewLDesc.get_buffer().get_end_iter()
        sdesc = self.entrySDesc.get_text()
        ldesc = self.textviewLDesc.get_buffer().get_text(start,end, True)
        if not sdesc:
            self.errorDialog(_("Kit Synopsis"), 
                             _("The Kit synopsis must be defined."))
            self.notebook.set_current_page(1)
            self.entrySDesc.grab_focus()
            return False
        elif util.iligalChars(sdesc, [':']):
            self.errorDialog(_("Kit Synopsis"), 
                             _("The Kit synopsis has illegal characters."))
            self.notebook.set_current_page(1)
            self.entrySDesc.grab_focus()
            return False
        
        if not ldesc:
            self.errorDialog(_("Kit Description"), 
                             _("The Kit description must be defined."))
            self.notebook.set_current_page(1)
            self.textviewLDesc.grab_focus()
            return False
        self._desc = aptutil.setDescription(sdesc, ldesc)
        
        self._depends = []
        #####
        self.initProgressDialog(_("<big><b>Checking selected packages.</b></big>"))
        self.window.set_sensitive(False)
        
        installedPackages = aptutil.readAptInstalled2List()
        item = self.listStore.get_iter_first()
        fraction = (1.0/len(self.pkgCache))
        progress = 0
        setFraction = 0
        while ( item != None ):
            if self.listStore.get_value(item, 0):
                self._depends.append(self.listStore.get_value(item, 1))
            item = self.listStore.iter_next(item)
            while gtk.events_pending():
                    gtk.main_iteration()
            if (progress + fraction) <= 1:
                progress += fraction
                if setFraction != util.pbarValue(progress):
                    setFraction = util.pbarValue(progress)
                    self.pbar.set_fraction(setFraction)
        
        self._depends = util.removeDuplicates(self._depends)
        self.dialogProgress.hide()
        self.window.set_sensitive(True)
        #####
        
        if not self._depends:
            self.errorDialog(_("Kit Packages"), 
                             _("At least one package has to be selected."))
            self.notebook.set_current_page(2)
            return False 
        
        start = self.textPostinst.get_buffer().get_start_iter()
        end = self.textPostinst.get_buffer().get_end_iter()
        self._postinst = self.textPostinst.get_buffer().get_text(start,end, True)
        
        mtpkg = mtpkgHandler.metapackage('/' + self._filename, 
                                         self._path, 
                                         self._name, 
                                         self._priority, 
                                         self._section, 
                                         self._version, 
                                         self._arch, 
                                         self._maintainer, 
                                         "", 
                                         "", 
                                         self._desc, 
                                         aptutil.getDependsFromList(self._depends),
                                         self._postinst)
        
        result = mtpkg.createBaseFiles(self.tmpDirRoot + "/metapackage")
        if result == 0:
            self.errorDialog(_("Error"), 
                             _("An error occurred during the Kit creation."))
            return False
        
        result = mtpkg.generateMetapackage(self.tmpDirRoot, 
                                           self.tmpDirRoot + "/metapackage")
        if result == 0:
            self.errorDialog(_("Error"), 
                             _("An error occurred during the Kit creation."))
            return False
        
        self.sucessDialog(_("Kit created successfully!"), 
                          (_("Kit <b>%s</b> was created with success and saved at <b>%s/%s</b>.") % (self._name, self._path, self._filename)))
        
        return True       

#
# __init__
#
    def __init__(self):     
        self.localPath = os.path.realpath(os.path.dirname(sys.argv[0]))
        
        self.icon = gtk.gdk.pixbuf_new_from_file(self.localPath +"/data/icons/scalable/kitcreator.svg")
        #self.icons = gtk.icon_theme_get_default()
        #try:
        #    gtk.window_set_default_icon(self.icons.load_icon("synaptic", 32, 0))
        #except gobject.GError:
        #    pass
        
        gtk.glade.bindtextdomain(__appname__, self.localPath + '/locale/' + __appname__)
        gtk.glade.textdomain(__appname__)
        gettext.bindtextdomain(__appname__, self.localPath + '/locale/' + __appname__)
        gettext.textdomain(__appname__)
        
        self.tmpDirRoot = "/tmp/kitsalinex"
        self.sectionsFile = self.localPath + "/data/sections.xml"
        
        self.gladefile = self.localPath + "/data/kitCreator.glade"
        self.wTree = gtk.glade.XML(self.gladefile)
        
        #menu
        self.aboutMenu = self.wTree.get_widget("aboutMenu")
        self.quitMenu = self.wTree.get_widget("quitMenu")
        self.systemkitMenu = self.wTree.get_widget("systemkitMenu")
        self.newMenu = self.wTree.get_widget("newMenu")
        self.openMenu = self.wTree.get_widget("openMenu")
        self.saveMenu = self.wTree.get_widget("saveMenu")
        
        #botoes do notebook
        self.buttonNext = self.wTree.get_widget("buttonNext")
        self.buttonNext2 = self.wTree.get_widget("buttonNext2")
        self.buttonNext3 = self.wTree.get_widget("buttonNext3")
        self.buttonNext4 = self.wTree.get_widget("buttonNext4")
        self.buttonBack = self.wTree.get_widget("buttonBack")
        self.buttonBack2 = self.wTree.get_widget("buttonBack2")
        self.buttonBack3 = self.wTree.get_widget("buttonBack3")
        self.buttonBack4 = self.wTree.get_widget("buttonBack4")
        
        self.notebook = self.wTree.get_widget("notebook")
        self.imageDadosGerais = self.wTree.get_widget("imageDadosGerais")
        self.imageDesc = self.wTree.get_widget("imageDesc")
        self.imagePackages = self.wTree.get_widget("imagePackages")
        self.imagePostInst = self.wTree.get_widget("imagePostInst")
        self.imageGenerate = self.wTree.get_widget("imageGenerate")
        
        self.treeview = self.wTree.get_widget("treeviewPackages")
        self.listStore = gtk.ListStore(gobject.TYPE_BOOLEAN, str, str, str)
        self.sectionStore = gtk.ListStore(str)
        
        self.vboxSectioncmb = self.wTree.get_widget("vboxSectioncmb")
        self.cmbSection = gtk.combo_box_new_text()
        self.vboxSectioncmb.add(self.cmbSection)
        self.cmbSection.show()
        
        self.packageList = {}
        self.setListStoreSearch = False
        
        #entry's (textboxes)
        self.entryName = self.wTree.get_widget("entryName")
        self.entryMaintainer = self.wTree.get_widget("entryMaintainer")
        self.entryVersion = self.wTree.get_widget("entryVersion")
        
        #combo boxes
        self.cmbArch = self.wTree.get_widget("cmbArch")
        #self.cmbSection = self.wTree.get_widget("cmbSection")
        self.cmbPriority = self.wTree.get_widget("cmbPriority")
        
        #desc
        self.entrySDesc = self.wTree.get_widget("entrySDesc")
        self.textviewLDesc = self.wTree.get_widget("textviewLDesc")
        
        #postinst
        self.textPostinst = self.wTree.get_widget("textPostinst")
        
        self.entryFilename = self.wTree.get_widget("entryFilename")
        self.buttonPath = self.wTree.get_widget("buttonPath")
        self.buttonGenerateKit = self.wTree.get_widget("buttonGenerateKit")
        
        #Progress dialog    
        self.dialogProgress = self.wTree.get_widget("dialogProgress")
        self.pbar = self.wTree.get_widget("pbarCache")
        self.lblMessage = self.wTree.get_widget("lblMessage")
        
        self.window = self.wTree.get_widget("window_criarkit")
        if (self.window):
            self.window.set_title(_(__title__))
            self.window.set_icon(self.icon)
            self.window.connect("destroy", gtk.main_quit)
            self.window.connect("delete_event", self.delete)
            #self.buttonQuit.connect("clicked", gtk.main_quit)
              
            #define as imagens dos tabs
            self.loadImage(self.imageDadosGerais, self.localPath + "/data/icons/scalable/package_development.png")
            self.loadImage(self.imageDesc, self.localPath + "/data/icons/scalable/emblem-documents.png")
            self.loadImage(self.imagePackages, self.localPath + "/data/icons/scalable/file-roller.png")
            self.loadImage(self.imagePostInst, self.localPath + "/data/icons/scalable/emblem-package.png")
            self.loadImage(self.imageGenerate, self.localPath + "/data/icons/scalable/application-x-deb.png")
            
            #searchbox
            self.hboxSearch = self.wTree.get_widget("hboxSearch")
            self.entrySearchbox = SearchWidget.SearchEntry(gtk.icon_theme_get_default())
            self.hboxSearch.add(self.entrySearchbox)
            self.entrySearchbox.connect("terms-changed", self.searchPackageList)
            self.entrySearchbox.show()
            
            #notebook navigation
            self.buttonNext.connect("clicked", lambda w: self.notebook.next_page())
            self.buttonNext2.connect("clicked", lambda w: self.notebook.next_page())
            self.buttonNext3.connect("clicked", lambda w: self.notebook.next_page())
            self.buttonNext4.connect("clicked", lambda w: self.notebook.next_page())
            self.buttonBack.connect("clicked", lambda w: self.notebook.prev_page())
            self.buttonBack2.connect("clicked", lambda w: self.notebook.prev_page())
            self.buttonBack3.connect("clicked", lambda w: self.notebook.prev_page())
            self.buttonBack4.connect("clicked", lambda w: self.notebook.prev_page())
            #o glade poe o expand False, e preciso mudar manualmente
            for n in range(self.notebook.get_n_pages()):
                self.notebook.set_tab_label_packing(self.notebook.get_nth_page(n), 
                                                    True, True, gtk.PACK_START)
                
            #menubar
            self.quitMenu.connect('activate', gtk.main_quit)
            self.aboutMenu.connect('activate', self.showAbout)
            self.systemkitMenu.connect('activate', self.createSystemKit)
            self.newMenu.connect('activate', self.resetFields)
            self.openMenu.connect('activate', self.openKit)
            self.saveMenu.connect('activate', self.saveKit)
            
            #sections
            self.sections = sections.getSections()
            items = self.sections.items()
            items.sort()

            self.cmbSection.append_text("")
            for key, value in items:
                self.cmbSection.append_text(_(value))
                
            self.cmbSection.set_active(0)
            self.cmbSection.set_wrap_width(1)
            
            #other buttons
            self.buttonPath.set_filename(os.getenv('HOME'))
            self.buttonGenerateKit.connect('clicked', self.generateMetapackage)
            
            self.setupPackageList()
            
def main():
    hwg = kitCreatorGTK()
    gtk.main()
    return 0