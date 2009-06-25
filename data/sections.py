from gettext import textdomain, gettext as _

sections = {"admin":_("Administration Utilities"),
            "base":_("Base Utilities"),
            "comm":_("Communication Programs"),
            "debian-installer":_("debian-installer udeb packages"),
            "devel":_("Development"),
            "doc":_("Documentation"),
            "editors":_("Editors"),
            "electronics":_("Electronics"),
            "embedded":_("Embedded software"),
            "games":_("Games"),
            "gnome":_("Gnome"),
            "graphics":_("Graphics"),
            "hamradion":_("Ham Radio"),
            "interpreters":_("Interpreted Computer Languages"),
            "kde":_("KDE"),
            "libdevel":_("Library development"),
            "libs":_("Libraries"),
            "mail":_("Mail"),
            "math":_("Mathematics"),
            "misc":_("Miscellaneous"),
            "net":_("Network"),
            "news":_("Newsgroups"),
            "oldlibs":_("Old Libraries"),
            "otherosfs":_("Other OS's and file systems"),
            "perl":_("Perl"),
            "python":_("Python"),
            "science":_("Science"),
            "shells":_("Shells"),
            "sound":_("Sound"),
            "tex":_("TeX"),
            "text":_("Text Processing"),
            "utils":_("Utilities"),
            "virtual":_("Virtual packages"),
            "web":_("Web Software"),
            "x11":_("X Window System software")}

def getSections():
    """
    Returns the sections.
    """
        
    return sections