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
        
    def test_instances_of_model_are_listed_on_model_index_page(self):
        front_page = self.browser.open_front_page()
        post_index = front_page.open_model("Blog post")
        posts_table = post_index.instances_table()
        assert_equal(["Title", "Author", "Date"], posts_table.headings())
        assert_equal([["Apples", "Bob", "2013-09-05 00:00:00"], ["Bananas", "Bob", "2013-09-06 00:00:00"]], posts_table.rows())
        
    def test_can_visit_model_instance_page_from_index(self):
        front_page = self.browser.open_front_page()
        post_index = front_page.open_model("Blog post")
        post_page = post_index.open_instance("Apples")
        assert_equal("Apples", post_page.title())
        
    def test_fields_of_model_are_listed_on_model_instance_page(self):
        front_page = self.browser.open_front_page()
        post_index = front_page.open_model("Blog post")
        post_page = post_index.open_instance("Apples")
        assert_equal("Apples", post_page.field_value("title"))


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
        
    def open_model(self, name):
        self._driver.find_element_by_link_text(name).click()
        return ModelIndexPage(self._driver)


class ModelIndexPage(object):
    def __init__(self, driver):
        self._driver = driver
        
    def instances_table(self):
        return Table(self._driver.find_element_by_tag_name("table"))
        
    def open_instance(self, link_text):
        self._driver.find_element_by_link_text(link_text).click()
        return ModelInstancePage(self._driver)


class ModelInstancePage(object):
    def __init__(self, driver):
        self._driver = driver
        
    def title(self):
        return self._driver.find_element_by_tag_name("h2").text
        
    def field_value(self, name):
        return self._driver.find_element_by_name(name).get_attribute("value")


class Table(object):
    def __init__(self, element):
        self._element = element
        
    def headings(self):
        return [
            element.text
            for element in self._element.find_elements_by_tag_name("th")
        ]
        
    def rows(self):
        return [
            [cell.text for cell in row.find_elements_by_tag_name("td")]
            for row in self._element.find_elements_by_css_selector("tbody tr")
        ]
