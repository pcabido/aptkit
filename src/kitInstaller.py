# -*- coding: utf-8 -*-
from repositoryhandler import repHandler

import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

import os
import sys
import gobject
import copy
import gettext

from util import util, aptutil
from util import SearchWidget
from data import sections
from PackageWorker import PackageWorker

from gettext import textdomain, gettext as _

__title__ = _("Kits Installer")
__version__ = "0.1b"
__comments__ = _("GTK frontend for Kits Installer.")
__authors__= ["Paulo Cabido <paulo.cabido@gmail.com>"]
__copyright__ = "Paulo Cabido"
__license__ = _("GNU GPL v3")
__appname__ = "kitinstaller"


class kitInstallerGTK:
    
    def delete(self, widget, event, data=None):
        """
        Exits gtk.
        """
        gtk.main_quit()
        return False
    
    def errorDialog(self, header, msg):
         """
         Shows a error message.
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
        Shows a sucess/info message.
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
    
    def choiceDialog(self, header, msg):
        """
        Shows a choice dialog (yes/no) message.
        """
        dialog = gtk.MessageDialog(parent=self.window,
                               flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_QUESTION,
                               buttons=gtk.BUTTONS_YES_NO)
        dialog.set_title("")
        dialog.set_icon(self.icon)
        dialog.set_markup("<big><b>%s</b></big>\n\n%s" % (header, msg))
        dialog.window.set_functions(gtk.gdk.FUNC_MOVE)
        response = dialog.run()
    
        if response == gtk.RESPONSE_YES:
            dialog.destroy()
            return True
        else:
            dialog.destroy()
            return False
            
        
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
         
        self.aboutDialog = self.wTree.get_widget("aboutdialogKitInstaller")
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
    #views
    #
    def rowCickedPackages(self, treeview):
        """
        Shows the kits info
        """
        
        path = treeview.get_cursor()[0]
        iter = treeview.get_model().get_iter(path)

        (mark, name, version, sdesc) = treeview.get_model()[iter]
        sdesc = aptutil.shortDescFromDic(self.packageList, name, version)
        ldesc = aptutil.longDescFromDic(self.packageList, name, version).replace(".\n","\n")
        self.textPackagesLDesc.get_buffer().set_text(sdesc + "\n" + ldesc )
        return
    
    def rowSection(self, treeview):
        """
        Shows the kits that are in the selected (row) section
        """
        
        path = treeview.get_cursor()[0]
        if path:
            model = treeview.get_model()
            iter = treeview.get_model().get_iter(path)
            section = model.get_value(iter,0)
        else:
            section = _("All kits")
        
        self.textPackagesLDesc.get_buffer().set_text("")
        self.storePackages.clear()
        if section != _("All kits"):
            if self.setSearch:
                #stn = util.dicKey(self.sections, section)
                stn = ""
                for key, value in self.sections.items():
                    if _(self.sections[key]) == section:
                        stn = key
                        break
                self.sectionPackageList = aptutil.getSectionPackages(stn, self.searchPackageList)
            else:
                #stn = util.dicKey(self.sections, section)
                stn = ""
                for key, value in self.sections.items():
                    if _(self.sections[key]) == section:
                        stn = key
                        break
                self.sectionPackageList = aptutil.getSectionPackages(stn, self.packageList)
            
            for pkg in self.sectionPackageList:
                self.storePackages.append([pkg['Installed'], pkg['Package'], pkg['Version'], pkg['ShortDesc']])
            self.treeviewPackages.set_model(self.storePackages)
            self.treeviewPackages.set_search_column(1)
        else:
            if self.setSearch:
                pkgList = self.searchPackageList
            else:
                pkgList = self.packageList
                
            for pkg in pkgList:
                self.storePackages.append([pkg['Installed'], pkg['Package'], pkg['Version'], pkg['ShortDesc']])
            self.treeviewPackages.set_model(self.storePackages)
            self.treeviewPackages.set_search_column(1)
        
        return
    
    def searchPackagesList(self, widget, query):
        """
        Searches the packages lists and sets the Treeviews with the results.
        """
        
        if query:
            self.searchPackageList = []
            self.setSearch = True
            for val in self.packageList:
                if (query in val['Package']) or (query in val['Version']) or (query in val['ShortDesc']) \
                or (query in val['LongDesc']) or (query in val['Maintainer']):
                    self.searchPackageList.append(val)
            self.rowSection(self.treeviewSections)   
        else:
            self.setSearch = False
            self.rowSection(self.treeviewSections) 
            
        return True
         
    def colToggledClicked( self, cell, path, model ):
        """
        Changes the toggle value in the treeview
        """
        
        model[path][0] = not model[path][0]
        
        for pkg in self.packageList:
            if pkg['Package'] == model[path][1] and pkg['Version'] == model[path][2]:
                pkg['Installed'] = model[path][0]
    
    def setupPackagesView(self):
        """
        Defines the columns in the treeview
        """
        
        self.rendererToggle = gtk.CellRendererToggle()
        self.rendererToggle.set_property('activatable', True)
        self.rendererToggle.connect('toggled', self.colToggledClicked, self.storePackages)
        
        self.colToggle = gtk.TreeViewColumn("", self.rendererToggle )
        self.colToggle.add_attribute(self.rendererToggle, "active", 0)
        
        self.colPacote = gtk.TreeViewColumn(_("Kit"), self.rendererText, text=1)
        self.colPacote.set_resizable(True)
        self.colPacote.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.colPacote.set_fixed_width( 160 )
        self.colPacote.set_sort_column_id(1)
        
        self.colVersion = gtk.TreeViewColumn(_("Version"), self.rendererText, text=2)
        self.colVersion.set_resizable(True)
        self.colVersion.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.colVersion.set_fixed_width( 150 )
        #self.colVersion.set_sort_column_id(2)
        
        self.colDesc = gtk.TreeViewColumn(_("Description"), self.rendererText, text=3)
        self.colDesc.set_resizable(True)
        self.colDesc.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.colDesc.set_fixed_width( 350 )
        #self.colDesc.set_sort_column_id(3)
        
        self.treeviewPackages.append_column(self.colToggle)
        self.treeviewPackages.append_column(self.colPacote)
        self.treeviewPackages.append_column(self.colVersion)
        self.treeviewPackages.append_column(self.colDesc)
        return
        
    def setupPackageList(self, deleteFiles=False):
        """
        Builds the package list
        """
        
        self.dialogProgress.realize()
        self.dialogProgress.set_transient_for(self.window)
        self.pbar.set_fraction(0)
        self.dialogProgress.window.set_functions(gtk.gdk.FUNC_MOVE)
        self.dialogProgress.set_icon(self.icon)
        self.dialogProgress.show()
        
        self.window.set_sensitive(False)
        
        self.pbar.set_fraction(0.1)
        while gtk.events_pending():
                    gtk.main_iteration()
        
        if deleteFiles:
            result = self.rep.update(True)
        else:
            result = self.rep.update()
        
        if not result:
            self.errorDialog(_("Error"),
                             _("The package list download failed."))
            self.dialogProgress.hide()
            self.window.set_sensitive(True)
            return False
        
        self.pbar.set_fraction(0.5)
        while gtk.events_pending():
                    gtk.main_iteration()
        result = self.rep.loadPackages()
                    
        if not result:
            self.dialogProgress.hide()
            self.window.set_sensitive(True)
            return False
        
        self.pbar.set_fraction(0.7)
        while gtk.events_pending():
                    gtk.main_iteration()
                    
        self.rep.checkInstalled()
        
        while gtk.events_pending():
                    gtk.main_iteration()
        self.pbar.set_fraction(0.8)
        self.packageList = self.rep.getPackages()   
        self.storePackages.clear()  
        for pkg in self.packageList:
            self.storePackages.append([pkg['Installed'], pkg['Package'], pkg['Version'], pkg['ShortDesc']])
            
                    
        self.treeviewPackages.set_model(self.storePackages)
        self.treeviewPackages.set_search_column(1)        
        
        while gtk.events_pending():
                    gtk.main_iteration()
        self.pbar.set_fraction(0.95)
        
        self.repSections = self.rep.getSections()
        self.storeSections.clear()
        for stn in self.repSections:
            if stn == "all":
                self.storeSections.append([_("All kits")])
            else:
                self.storeSections.append([_(self.sections[stn])])
            
        self.treeviewSections.set_model(self.storeSections)
        self.treeviewSections.set_search_column(0)

        self.origPkgList = copy.deepcopy(self.packageList)
            
        self.dialogProgress.hide()
        self.window.set_sensitive(True)
        return True
    
    def updateRepository(self, widget, data=None):
        """
        Forces a repository update and deletes the existing files
        """
        
        self.rep.clean()
        self.setupPackageList()
        
    
    def doInstallRemove(self, widget, data=None):
        """
        Installs or removes the selected packages
        """
        
        pkgs_add = []
        pkgs_rm = []
        cache = ""
        
        for pkg in self.packageList:
            for opkg in self.origPkgList:
                if pkg['Package'] == opkg['Package'] and pkg['Version'] == opkg['Version'] and pkg['Installed'] != opkg['Installed']:
                    if pkg["Installed"]:
                         pkgs_add.append(pkg['Package'])
                    else:
                        pkgs_rm.append(pkg['Package'])
        
        result = self.packageWorker.perform_action(self.window, 
                                                   cache,
                                                   None,
                                                   None,
                                                   1)
        
        result = self.packageWorker.perform_action(self.window,
                                                   cache,
                                                   pkgs_add,
                                                   pkgs_rm)
        
        erroInst = ""
        for pkg in pkgs_add:
            if not aptutil.isInstalled(pkg, False):
                if not erroInst:
                    erroInst += pkg
                else:
                    erroInst += ", " + pkg
                    
                for val in self.packageList:
                    if val['Package'] == pkg:
                        val['Installed'] = False
                        break
                    
                item = self.storePackages.get_iter_first()
                while ( item != None ):
                    if self.storePackages.get_value(item, 1,) == pkg:
                        self.storePackages.set_value(item, 0, False)
                        break
                    item = self.storePackages.iter_next(item)
            else:
                for val in self.origPkgList:
                    if val['Package'] == pkg:
                        val['Installed'] = True
                        break
        
        
        erroRm = ""
        for pkg in pkgs_rm:
            if aptutil.isInstalled(pkg, False):
                if not erroRm:
                    erroRm += pkg
                else:
                    erroRm += ", " + pkg
                
                for val in self.packageList:
                    if val['Package'] == pkg:
                        val['Installed'] = True
                        break
                    
                item = self.storePackages.get_iter_first()
                while ( item != None ):
                    if self.storePackages.get_value(item, 1,) == pkg:
                        self.storePackages.set_value(item, 0, True)
                        break
                    item = self.storePackages.iter_next(item)
            else:
                for val in self.origPkgList:
                    if val['Package'] == pkg:
                        val['Installed'] = False
                        break
                
                
        if erroInst and erroRm:
            self.errorDialog(_("Error"), 
                             (_("Error while installing the following kits <b>%s</b> and while removing <b>%s</b>.") % (erroInst, erroRm)))
        elif erroInst:
            self.errorDialog(_("Error"),
                             _("Error while installing the following kits <b>%s</b>.") % erroInst)
        elif erroRm:
            self.errorDialog(_("Error"),
                             _("Error while removing the following kits <b>%s</b>.") % erroRm)
        else:
            self.sucessDialog(_("Success"),
                              _("All kits where installed/removed with success."))
        
        return True  
        
        
    def openKit(self, widget, data=None):
        pkgs_add = []
        pkgs_rm = []
        dialog = gtk.FileChooserDialog(_("Open Kit"),
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("Kits")
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
                else:
                    print "error"
        else:
            dialog.destroy()
            return
        
        dialog.destroy()
        
        filename = (tmpKitFile[0] +  tmpKitFile[1])
        
        if aptutil.isInstalled(filename):
            if aptutil.upgradable(filename):
                upgrade = self.choiceDialog(_("Update Kit"),
                                            _("<b>%s</b> is already installed, but this version is newer.\nDo you wish to update?") 
                                            % aptutil.pkgInfo(filename, "Package"))
                
                if upgrade:
                    result = aptutil.install(filename)
                
                    if result:
                        self.sucessDialog(_("Update Kit"),
                                          _("<b>%s</b> was successfully updated.") % aptutil.pkgInfo(filename, "Package"))
                        return True
                    else:
                        self.errorDialog(_("Error"),
                                         _("Error while updating <b>%s</b>.") % aptutil.pkgInfo(filename, "Package"))
                        return False
            else:
                self.sucessDialog(_("Update Kit"),
                                  _("The <b>%s</b> Kit is already updated.") % aptutil.pkgInfo(filename, "Package"))
                return True
        else:
            install = self.choiceDialog(_("Install Kit"),
                                        _("Do you wish to install <b>%s</b>?") % aptutil.pkgInfo(filename, "Package"))
            if install:
                result = aptutil.install(filename)
                if result:
                    self.sucessDialog(_("Kit installed"),
                                      _("Kit <b>%s</b> was installed with success.") % aptutil.pkgInfo(filename, "Package"))
                    return True
                else:
                    self.errorDialog(_("Error"),
                                     _("Error while installing <b>%s</b>.") % aptutil.pkgInfo(filename, "Package"))
                    return False
    #
    # __init__
    #
    
    def __init__(self):
        self.localPath = os.path.realpath(os.path.dirname(sys.argv[0]))
        
        self.icon = gtk.gdk.pixbuf_new_from_file(self.localPath +"/data/icons/scalable/kitinstaller.svg")
        #try:
        #    gtk.window_set_default_icon(self.icons.load_icon("synaptic", 32, 0))
        #except gobject.GError:
        #    pass

        gtk.glade.bindtextdomain(__appname__, self.localPath + '/locale/' + __appname__)
        gtk.glade.textdomain(__appname__)
        gettext.bindtextdomain(__appname__, self.localPath + '/locale/' + __appname__)
        gettext.textdomain(__appname__)
        
        self.tmpDir = "/tmp/kitsalinex/sourcelist"
        self.localDir = os.getenv('HOME')
        self.sourcelist = self.localPath + "/data/sources.list"
        
        self.packageList = []
        
        self.sectionPackageList = []
        self.sections = sections.getSections()
        self.selectedSection = "all"
        
        self.setSearch = False
        self.searchPackageList = []
        
        self.rep = repHandler.rephandle(self.sourcelist, self.tmpDir)
        
        self.gladefile = self.localPath + "/data/kitInstaller.glade"
        self.wTree = gtk.glade.XML(self.gladefile)
        
        self.notebook = self.wTree.get_widget("notebook")
        
        self.quitMenu = self.wTree.get_widget("quitMenu")
        self.aboutMenu = self.wTree.get_widget("aboutMenu")
        self.openMenu = self.wTree.get_widget("openMenu")
        self.updateRepMenu = self.wTree.get_widget("updateRepMenu")
        
        self.buttonAplicar = self.wTree.get_widget("buttonAplicar")
        
        self.vboxSearch = self.wTree.get_widget("vboxSearch")
        self.entrySearchbox = SearchWidget.SearchEntry(gtk.icon_theme_get_default())
        self.vboxSearch.add(self.entrySearchbox)
        self.entrySearchbox.connect("terms-changed", self.searchPackagesList)
        self.entrySearchbox.show()
        
        self.treeviewSections = self.wTree.get_widget("treeviewSection")
        self.treeviewPackages = self.wTree.get_widget("treeviewPackages")
        self.textPackagesLDesc = self.wTree.get_widget("textPackagesLDesc")
        
        self.storeSections = gtk.ListStore(str)
        self.storePackages = gtk.ListStore(gobject.TYPE_BOOLEAN, str, str, str)
        
        #renderer's
        self.rendererText = gtk.CellRendererText()
        
        #sections
        self.colSection = gtk.TreeViewColumn(_("Section"), self.rendererText, text=0)
        self.colSection.set_resizable(True)
        self.colSection.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.colSection.set_fixed_width( 210 )
        self.treeviewSections.append_column(self.colSection)
        
        #package lists
        self.setupPackagesView()
        
        #Progress dialog    
        self.dialogProgress = self.wTree.get_widget("dialogProgress")
        self.pbar = self.wTree.get_widget("pbarCache")
        
        self.window = self.wTree.get_widget("window_installkits")
        if (self.window):
            self.window.set_title(_(__title__))
            self.window.set_icon(self.icon)
            self.window.connect("destroy", gtk.main_quit)
            self.window.connect("delete_event", self.delete)
            
            self.buttonAplicar.connect('clicked', self.doInstallRemove, None)
                
            #menubar
            self.quitMenu.connect('activate', gtk.main_quit)
            self.aboutMenu.connect('activate', self.showAbout)
            self.openMenu.connect('activate', self.openKit)
            self.updateRepMenu.connect('activate', self.updateRepository)
            
            self.treeviewPackages.connect("cursor-changed", self.rowCickedPackages)
            self.treeviewSections.connect("cursor-changed", self.rowSection)
            
            self.setupPackageList()
            self.packageWorker = PackageWorker()
            
            
def main():
    hwg = kitInstallerGTK()
    gtk.main()
    return 0