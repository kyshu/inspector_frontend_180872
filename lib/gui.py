#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import browser

class ContainerWidget:
    def __init__(self):
        pass
        #self._container.show()

    def setContainer(self, container):
        self._container = container

    def container(self):
        return self._container

class BoxContainerWidget(ContainerWidget):
    C_DIR_HOR = 0
    C_DIR_VER = 1
    def __init__(self, dir):
        if (dir == self.C_DIR_HOR):
            self.setContainer(gtk.HBox(False, 5))
        elif (dir == self.C_DIR_VER):
            self.setContainer(gtk.VBox(False, 5))
        else:
            print "dir = ", dir, "not expected"

class FrameContainerWidget(ContainerWidget):
    def __init__(self, label=""):
        self.setContainer(gtk.Frame(label))

class DeviceRow(FrameContainerWidget):
    def __init__(self):
        FrameContainerWidget.__init__(self, "device")
        self._box = gtk.HBox(False, 5)
        self._box.show()
        self.container().add(self._box)

        self._deviceLabel = gtk.Label("device")
        self._box.pack_start(self._deviceLabel)
        self._deviceLabel.show()
        self._refreshButton = gtk.Button("Refresh", gtk.STOCK_REFRESH)
        self._box.pack_start(self._refreshButton)
        self._refreshButton.show()

        self.container().show()

    def setRefreshCb(self, callback):
        self._refreshButton.connect("clicked", callback)

    def setDevice(self, name):
        self._deviceLabel.set_text(name)

class ServiceRow(FrameContainerWidget):
    def __init__(self):
        FrameContainerWidget.__init__(self, "HTTP Service")
        self._box = gtk.HBox(False, 5)
        self._box.show()
        self.container().add(self._box)

        self._rootLabel = gtk.Label("HTTP root")
        self._box.pack_start(self._rootLabel)
        self._rootLabel.show()
        self._textEntry = gtk.Entry()
        self._textEntry.set_text("inspector_root")
        self._box.pack_start(self._textEntry)
        self._textEntry.show()
        #self._startButton = gtk.Button("Start")
        #self._box.pack_start(self._startButton)
        #self._startButton.show()

        self.container().show()

    def getRootDir(self):
        return self._textEntry.get_text()


class PageRow(BoxContainerWidget):
    page_item_key = "page"
    def __init__(self, browserChangedCb, pageInspectedCb):
        BoxContainerWidget.__init__(self, BoxContainerWidget.C_DIR_VER)
        self._pkgCombo = gtk.combo_box_new_text()
        self._pkgCombo.set_title("packages")
        self._pkgCombo.show()
        self._pkgCombo.connect("changed", self._browserSelected)
        self.container().pack_start(self._pkgCombo)

        self._scrolledWindow = gtk.ScrolledWindow()
        self._scrolledWindow.set_usize(250, 150)
        self._scrolledWindow.show()
        #self._pageList = gtk.List()
        self._pageModel = gtk.ListStore(str, int)
        self._pageList = gtk.TreeView(self._pageModel)
        col = gtk.TreeViewColumn("title")
        self._pageList.append_column(col)
        renderer = gtk.CellRendererText()
        col.pack_start(renderer)
        col.add_attribute(renderer, "text", 0)
        self._scrolledWindow.add_with_viewport(self._pageList)
        self._pageList.show()
        #self._pageList.connect("selection_changed", self._pageSelected)
        self._pageList.get_selection().connect("changed", self._pageSelected)
        self.container().pack_start(self._scrolledWindow)

        self._inspectorButton = gtk.Button("Inspect")
        self._inspectorButton.show()
        self._inspectorButton.set_sensitive(False)
        self.container().pack_start(self._inspectorButton)

        self.container().show()

        self._notifyBrowserSelected = browserChangedCb
        self._notifyBeginInspect = pageInspectedCb
        self._inspectHandler = None

        #self.addPackages("pkg1")
        #self.addPage("title2")
        #self.addPage("title2")
        #self.addPage("title2")
        #self._resetAll()

    def setPackages(self, packages):
        self._remote_browsers = packages
        self._update()

    def _update(self):
        self._resetAll()
        for browser in self._remote_browsers:
            self._addBrowser(browser.getName())
        self._pkgCombo.set_active(0)
        self._browserSelected()

    def _browserSelected(self, data=None):
        active_index = self._pkgCombo.get_active()
        #self._pageList.clear_items(0, -1)
        self._pageModel.clear()
        if active_index == -1:
            return
        pages = self._remote_browsers[active_index].getPages()
        self._notifyBrowserSelected(self._remote_browsers[active_index])
        for i, page in enumerate(pages):
            self._addPage(page, i)

    def _pageSelected(self, selection):
        model, iter = selection.get_selected()
        page = None
        if iter!=None:
            active_index = self._pkgCombo.get_active()
            pages = self._remote_browsers[active_index].getPages()
            page = pages[self._pageModel[iter][1]]
        if self._inspectHandler != None:
            self._inspectorButton.disconnect(self._inspectHandler)
            self._inspectHandler = None
        if not iter:
            self._inspectorButton.set_sensitive(False)
        else:
            self._inspectorButton.set_sensitive(True)
            self._inspectHandler = self._inspectorButton.connect("clicked", self._inspectPage, page)
            
        #dlist = self._pageList.get_selection()
        #if self._inspectHandler != None:
        #    self._inspectorButton.disconnect(self._inspectHandler)
        #    self._inspectHandler = None
        #if not dlist:
        #    self._inspectorButton.set_sensitive(False)
        #elif len(dlist) == 1:
        #    self._inspectorButton.set_sensitive(True)
        #    page = dlist[0].get_data(self.page_item_key)
        #    self._inspectHandler = self._inspectorButton.connect("clicked", self._inspectPage, page)
        return

    def _inspectPage(self, button, page):
        self._notifyBeginInspect(page)

    def _resetAll(self):
        self._pkgCombo.get_model().clear()
        #self._pageList.clear_items(0, -1)
        self._pageModel.clear()

    def _addPage(self, page, index):
        #label = gtk.Label(page.getTitle())
        #label.show()
        #list_item = gtk.ListItem()
        #list_item.add(label)
        #list_item.show()
        #list_item.set_data(self.page_item_key, page)
        #self._pageList.add(list_item)
        #self._pageList.add_attribute()
        self._pageModel.append([page.getTitle(), index])

    def _addBrowser(self, name):
        self._pkgCombo.append_text(name)
        if (self._pkgCombo.get_active() == -1):
            self._pkgCombo.set_active(0)
