import webbrowser
from selenium.webdriver.remote.webdriver import WebDriver as wd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import selenium
from bs4 import BeautifulSoup as BS
import json
import lxml

class WebVPN:
    def __init__(self, opt: dict, headless=False):
        self.root_handle = None
        self.driver: wd = None
        self.passwd = opt["password"]
        self.userid = opt["username"]
        self.headless = headless

    def login_webvpn(self):
        """
        Log in to WebVPN with the account specified in `self.userid` and `self.passwd`

        :return:
        """
        d = self.driver
        if d is not None:
            d.close()
        d = selenium.webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        d.get("https://webvpn.tsinghua.edu.cn/login")
        username = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item"]//input'
                                   )[0]
        password = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item password-field" and not(@id="captcha-wrap")]//input'
                                   )[0]
        #找到学号和密码框
        username.send_keys(str(self.userid))
        password.send_keys(self.passwd)
        #输入
        d.find_element(By.ID, "login").click()
        #点击登录
        self.root_handle = d.current_window_handle
        self.driver = d
        return d
        #？？？

    def access(self, url_input):
        """
        Jump to the target URL in WebVPN

        :param url_input: target URL
        :return:
        """
        d = self.driver
        url = By.ID, "quick-access-input"
        #输入网址
        btn = By.ID, "go"
        #跳转按钮
        wdw(d, 5).until(EC.visibility_of_element_located(url))
        actions = AC(d)
        actions.move_to_element(d.find_element(*url))
        actions.click()
        actions.\
            key_down(Keys.CONTROL).\
            send_keys("A").\
            key_up(Keys.CONTROL).\
            send_keys(Keys.DELETE).\
            perform()

        d.find_element(*url)
        d.find_element(*url).send_keys(url_input)
        d.find_element(*btn)
        d.find_element(*btn).click()

    def switch_another(self):
        """
        If there are only 2 windows handles, switch to the other one

        :return:
        """
        d = self.driver
        assert len(d.window_handles) == 2
        wdw(d, 5).until(EC.number_of_windows_to_be(2))
        for window_handle in d.window_handles:
            if window_handle != d.current_window_handle:
                d.switch_to.window(window_handle)
                return d

    def to_root(self):
        """
        Switch to the home page of WebVPN

        :return:
        """
        self.driver.switch_to.window(self.root_handle)

    def close_all(self):
        """
        Close all window handles

        :return:
        """
        while True:
            try:
                l = len(self.driver.window_handles)
                if l == 0:
                    break
            except selenium.common.exceptions.InvalidSessionIdException:
                return
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()

    def login_info(self):
        """
        TODO: After successfully logged into WebVPN, login to info.tsinghua.edu.cn

        :return:
        """
        d = self.driver
        usr = By.ID, "userName"
        psw = By.NAME, "password"
        btn = By.XPATH, '//td[@class="but"]//input'
                                   
        wdw(d, 5).until(EC.visibility_of_element_located(usr))
        actions = AC(d)
        actions.move_to_element(d.find_element(*usr))
        actions.click()
        actions.\
            key_down(Keys.CONTROL).\
            send_keys("A").\
            key_up(Keys.CONTROL).\
            send_keys(Keys.DELETE).\
            perform()

        d.find_element(*usr)
        d.find_element(*usr).send_keys(self.userid)
        
        actions.move_to_element(d.find_element(*psw))
        actions.click()
        actions.\
            key_down(Keys.CONTROL).\
            send_keys("A").\
            key_up(Keys.CONTROL).\
            send_keys(Keys.DELETE).\
            perform()

        d.find_element(*psw)
        d.find_element(*psw).send_keys(self.passwd)
        

        d.find_element(*btn)
        d.find_element(*btn).click()

        trigger = By.XPATH, '//li[@class="search"]'
        #等一个搜索键
        wdw(d, 5).until(EC.visibility_of_element_located(trigger))
        self.driver.close()
        return
        # Hint: - Use `access` method to jump to info.tsinghua.edu.cn
        #       - Use `switch_another` method to change the window handle
        #       - Wait until the elements are ready, then preform your actions
        #       - Before return, make sure that you have logged in successfully

    def get_grades(self):
        """
        TODO: Get and calculate the GPA for each semester.

        Example return / print:
            2020-秋: *.**
            2021-春: *.**
            2021-夏: *.**
            2021-秋: *.**
            2022-春: *.**

        :return:
        """
        d = self.driver
        d.implicitly_wait(3)
        #摆烂了，直接等个3s
        html = d.find_elements(By.ID, "table1")[0].get_attribute("innerHTML")
        soup = BS(html,"lxml")
        #print(soup)
        gpa_by_term = dict()
        course_list = soup.find_all('tr')
        #print(len(course_list))
        for each_course in course_list[1:]:  #第一个爬出来的居然不是一门课...
            contents = each_course.find_all('td')
            #contents[0]:课程编号
            #[1]:名称
            #[2]:学分
            #[3]:等级
            #[4]:绩点
            #[5]:学期
            term = str(contents[-1].get_text().strip())
            #if gpa_by_term.has_key(term):  error
            if term not in gpa_by_term:
                gpa_by_term[term] = [0.0,0.0]
            credit = float(contents[2].get_text().strip())
            point = str(contents[4].get_text().strip())
            if point != "N/A":
                point = float(point)
                gpa_by_term[term][0] = gpa_by_term[term][0] + credit
                gpa_by_term[term][1] = gpa_by_term[term][1] + point*credit
                #print(point,credit,gpa_by_term[term][0],gpa_by_term[term][1])
                
            
        total_credit = 0.0
        total_point = 0.0
        for key, value in gpa_by_term.items():
            print(key,": ",end="")
            if value[0]!= 0.0:
                print(value[1]/value[0],end=" ")
                print("学分：", value[0],end=" ")
                print("总学分积", value[1])
                total_credit = total_credit + value[0]
                total_point = total_point + value[1]
            else:
                print("N/A")
        print("总GPA：",total_point/total_credit,
                "总学分：",total_credit,
                "总学分积：",total_point)
        

        
        # Hint: - You can directly switch into
        #         `zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw`
        #https://webvpn.tsinghua.edu.cn/http/77726476706e69737468656265737421eaff4b8b69336153301c9aa596522b20bc86e6e559a9b290/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw&flag=di1
        #         after logged in
        #       - You can use Beautiful Soup to parse the HTML content or use
        #         XPath directly to get the contents
        #       - You can use `element.get_attribute("innerHTML")` to get its
        #         HTML code

        #raise NotImplementedError

if __name__ == "__main__":
    # TODO: Write your own query process
    with open("./settings.json") as f:
        json_dict = json.load(f)
    w = WebVPN(json_dict) 
    w.login_webvpn()
    w.access("info.tsinghua.edu.cn")
    w.switch_another()
    w.login_info()
    w.to_root()
    w.access("zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw")
    w.switch_another()
    w.get_grades()
    w.close_all()