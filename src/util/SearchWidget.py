import sexy
import gtk
import gobject

class SearchEntry(sexy.IconEntry, gobject.GObject):
    __gsignals__ = {'terms-changed':(gobject.SIGNAL_RUN_FIRST,
                                     gobject.TYPE_NONE,
                                     (gobject.TYPE_STRING,))}

    def __init__(self, icon_theme):
        """
        Creates an enhanced IconEntry that supports a time out when typing
        and uses a different background colour when the search is active
        """
        sexy.IconEntry.__init__(self)
        self.__gobject_init__()
        self._handler_changed = self.connect_after("changed",
                                                   self._on_changed)
        self.connect("icon-pressed", self._on_icon_pressed)
        # Does not work - known bug in libsexy
        # image = gtk.image_new_from_icon_name(gtk.STOCK_CLEAR,
        #                                      gtk.ICON_SIZE_MENU)
        image = gtk.Image()
        pixbuf = icon_theme.load_icon(gtk.STOCK_CLEAR,
                                      gtk.ICON_SIZE_MENU,
                                      0)
        image.set_from_pixbuf(pixbuf)
        self.set_icon(sexy.ICON_ENTRY_SECONDARY, image)
        self.set_icon_highlight(sexy.ICON_ENTRY_PRIMARY, True)

        # Do not draw a yellow bg if an a11y theme is used
        settings = gtk.settings_get_default()
        theme = settings.get_property("gtk-theme-name")
        self._a11y = theme.startswith("HighContrast") or\
                     theme.startswith("LowContrast")

        self._timeout_id = 0

    def _on_icon_pressed(self, widget, icon, mouse_button):
        """
        Emit the terms-changed signal without any time out when the clear
        button was clicked
        """
        if icon == sexy.ICON_ENTRY_SECONDARY:
            self.handler_block(self._handler_changed)
            self.set_text("")
            self._check_style()
            self.handler_unblock(self._handler_changed)
            self.emit("terms-changed", self.get_text())

    def _on_changed(self, widget):
        """
        Call the actual search method after a small timeout to allow the user
        to enter a longer search term
        """
        self._check_style()
        if self._timeout_id > 0:
            gobject.source_remove(self._timeout_id)
        #FIXME: Could be of use for a11y
        #timeout = self.config.get_int("/apps/gnome-app-install/search-timeout")
        timeout = 1000
        self._timeout_id = gobject.timeout_add(timeout,
                                               lambda: self.emit("terms-changed", self.get_text()))

    def _check_style(self):
        """
        Use a different background colour if a search is active
        """
        # Based on the Rhythmbox code
        yellowish = gtk.gdk.Color(63479, 63479, 48830)
        if self._a11y == True:
            return
        if self.get_text() == "":
            self.modify_base(gtk.STATE_NORMAL, None)
        else:
            self.modify_base(gtk.STATE_NORMAL, yellowish)