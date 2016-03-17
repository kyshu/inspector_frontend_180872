from connection import Connection
import json
import logger

class Page:
    def __init__(self, title, url, id, is_chrome=False):
        self._title = title
        self._url = url
        self._id = id
        self._is_chrome = is_chrome

    def _is_attached(self):
        return self._id == ""

    def getDebugFrontendUrl(self):
        return "/devtools/page/" + self._id

    def getTitle(self):
        if self._title != None and self._title != "":
            return self._title
        else:
            return self._url

    def can_inspected(self):
        return (not self._is_attached()) and (not self._is_chrome)

    def dump(self, logger, indent):
        logger.i(" " * indent + "title: " + self._title + " url: " + self._url + " id: " + self._id)

#   def getDevToolsURL(page):
#       if (isPageAttached(page)):
#           return ""
#   
#       url_str = page["devtoolsFrontendUrl"]
#       url = urlparse(url_str)
#       _REMOTE_DOMAIN = "chrome-devtools-frontend.appspot.com"
#       if url_str.find(_REMOTE_DOMAIN) == -1:
#           log.e("invalid frontend url: " + url_str)
#           return ""
#   
#       _CHROME_DEVTOOLS_SCHEME = "chrome-devtools"
#       _CHROME_UI_DEVTOOLS_HOST = "devtools"
#       _CHROME_UI_DEVTOOLS_REMOTE_PATH = "remote"
#       proxy_url = _CHROME_DEVTOOLS_SCHEME + "://" + \
#           _CHROME_UI_DEVTOOLS_HOST + "/" + \
#           _CHROME_UI_DEVTOOLS_REMOTE_PATH + "/" + \
#           url.path
#       if proxy_url.find("?") == -1:
#          return proxy_url + "?&remoteFrontend=true&dockSide=undocked" 
#       else:
#          return proxy_url + "&&remoteFrontend=true&dockSide=undocked" 

#   def request_activate_page(browser, page):
#       sock = connect_to_adb_server()
#       def nope(sock):
#           pass
#   
#       def do_active_page(sock):
#           cmd = "/json/activate/"+ page["id"]
#           return send_get_http_request(sock, cmd, nope)
#       return forward_to_local_abstract(sock, serial, browser["usock"], do_active_page)


class Browser:
    def __init__(self, pid, pkg, usock, is_chrome=False):
        self._pid = pid
        self._pkg = pkg
        self._usock = usock
        self._is_chrome = is_chrome
        self._pages = []

    def query_pages(self, serial_num, conn):
        conn.query_pages(serial_num, self._usock, self._onReceivePages)

    def inspect(self, ith_page):
        if len(self._pages) <= ith_page:
            return
        return self._pages[ith_page].getDebugFrontendUrl()

    def getName(self):
        return self._pkg

    def getPages(self):
        return self._pages

    def getUsock(self):
        return self._usock

    def _onReceivePages(self, pages):
        pages = json.loads(pages)
        self._pages = []
        for page in pages:
            self._pages.append(Page(page["title"], page["url"], page["id"], self._is_chrome))
        return

    def dump(self, logger):
        logger.i("pid: " + repr(self._pid) + " pkg: " + self._pkg + " num_pages: " + repr(len(self._pages)))
        for page in self._pages:
            page.dump(logger, 4)
        return
