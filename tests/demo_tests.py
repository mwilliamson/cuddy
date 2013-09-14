import signal
import time
from StringIO import StringIO

import spur.local
from nose.tools import istest, assert_equal
from selenium import webdriver


@istest
class DemoTests(object):
    def setup(self):
        self.server = _start_server()
        self.browser = _create_browser(self.server.url)
        
    def teardown(self):
        self.server.close()
        self.browser.close()
        
    def test_models_are_listed_on_index_page(self):
        front_page = self.browser.open_front_page()
        assert_equal(["Author", "Blog post"], front_page.model_names())


def _start_server():
    shell = spur.local.LocalShell()
    server_stderr = StringIO()
    server_process = shell.spawn(["gunicorn", "cuddy.demo:app"], stderr=server_stderr)
    
    def is_ready():
        return "Listening at: http://127.0.0.1:8000" in server_stderr.getvalue()
    
    wait_until(
        is_ready,
        timeout=5,
        interval=0.1,
    )
    
    return CuddyServer(server_process, port=8000)


def wait_until(func, timeout, interval):
    start_time = time.time()
    while True:
        result = func()
        if result:
            return result
        elif time.time() - start_time > timeout:
            raise Exception("Timeout")
        else:
            time.sleep(interval)
        


class CuddyServer(object):
    def __init__(self, process, port):
        self._process = process
        self.url = "http://localhost:{0}".format(port)
        
    def close(self):
        self._process.send_signal(signal.SIGTERM)
    

def _create_browser(base_url):
    return CuddyBrowser(webdriver.Firefox(), base_url)


class CuddyBrowser(object):
    def __init__(self, driver, base_url):
        self._driver = driver
        self._base_url = base_url
        
    def open_front_page(self):
        self._driver.get(self._base_url)
        return FrontPage(self._driver)
        
    def close(self):
        self._driver.close()


class FrontPage(object):
    def __init__(self, driver):
        self._driver = driver

    def model_names(self):
        return [
            element.text
            for element in self._driver.find_elements_by_css_selector("h2")
        ]
