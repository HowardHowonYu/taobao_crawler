from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

import random
import time
import sys

class ProductCrawler():
 
    def __mall_login__(self, itemids, user_id, user_pw):
        from selenium import webdriver

        co = webdriver.ChromeOptions()
        co.add_argument("log-level=3")
        co.add_argument("--headless")
        driver = webdriver.Chrome('./chromedriver', options=co)
        driver.get("https://free-proxy-list.net/")

        PROXIES = []
        proxies = driver.find_elements_by_css_selector("tr[role='row']")
        for p in proxies:
            result = p.text.split(" ")

            if result[-1] == "yes":
                PROXIES.append(result[0]+":"+result[1])

        print('프록시 가져옴')
        driver.close()
        # set proxies to driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(PROXIES[random.randint(0, len(PROXIES)-1)])
        driver = webdriver.Chrome(
            './chromedriver', options=chrome_options)

        # login
        driver.get("https://item.taobao.com/item.htm?id={}".format(itemids[0]))

        # control alert window
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            time.sleep(1)

        # log_in, taobao or tamll
        try:
            driver.switch_to.frame("sufei-dialog-content")

        except:
            driver.switch_to.frame('baxia-dialog-content')


        id_box = driver.find_element_by_id('fm-login-id')
        pw_box = driver.find_element_by_id('fm-login-password')

        webdriver.ActionChains(driver).send_keys_to_element(
            id_box, user_id).send_keys_to_element(pw_box, user_pw).perform()
        time.sleep(1)

        swipe_btn = driver.find_element_by_id('nc_1_n1z')

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "nc_1__scale_text"))
            )

        finally:
                webdriver.ActionChains(driver).click_and_hold(
                    swipe_btn).move_to_element_with_offset(swipe_btn, 300, 0).move_to_element_with_offset(swipe_btn, 300, 0).perform()
                time.sleep(1)

        time.sleep(1)
        login_btn = driver.find_element_by_class_name(
            'fm-btn').find_element_by_tag_name('button')
        webdriver.ActionChains(driver).click(login_btn).perform()

        driver.switch_to.default_content()

        print('로그인 완료')

        return driver

    def taobao_crawler(self, itemids, user_id, user_pw):
        from selenium import webdriver
        from scrapy.http import TextResponse
        from fake_useragent import UserAgent

        import requests

        driver = self.__mall_login__(
            itemids, user_id, user_pw)

        cookies = driver.get_cookies()

        for cookie in cookies:
            driver.add_cookie(cookie)

        result_ls = []
        for itemid in itemids[::-1]:
            url = "https://item.taobao.com/item.htm?id={}".format(itemid)
            driver.get(url)

            result = {}
            result['item_id'] = itemid
            result['title'] = driver.find_element_by_xpath(
                '//*[@id="J_Title"]/h3').text

            # promo price
            # 가격 정보가 다 들어오고 나서 정보 수집 시작
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "J_PromoPriceNum"))
                )
            except:
                result['og_price'] = driver.find_element_by_xpath(
                    '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').text
                result['promo_price'] = "할인 가격 정보 없음"

            finally:
                # 다 가져온 정보에서도 할인 가격이 없을 경우
                try:
                    result['og_price'] = driver.find_element_by_xpath(
                        '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').text
                    result['promo_price'] = driver.find_element_by_xpath(
                        '//*[@id="J_PromoPriceNum"]').text
                except:
                    result['og_price'] = driver.find_element_by_xpath(
                        '//*[@id="J_StrPrice"]/em[@class="tb-rmb-num"]').text
                    result['promo_price'] = "할인 가격 정보 없음"

            userAgent = UserAgent(verify_ssl=False).random

            headers = {
                'User-Agent': userAgent
            }


            # https://stackoverflow.com/questions/32910093/python-requests-gets-tlsv1-alert-internal-err
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'

            response = requests.get(url=url, headers=headers)
            req = TextResponse(
                response.url, body=response.text, encoding="utf-8")
            result['item_title'] = req.xpath(
                '//*[@id="J_Title"]/h3/@data-title').extract_first()

            option_title = req.xpath(
                '//*[@id="J_isku"]/div/dl/dd/ul/@data-property').extract()
            r = []
            for title in option_title:
                j = {}
                j['option_title'] = title
                j['option_details'] = req.xpath(
                    '//*[@id="J_isku"]/div/dl/dd/ul[@data-property="{}"]/li/a/span/text()'.format(title)).extract()
                j['option_image_urls'] = [path[17:-29] for path in req.xpath(
                    '//*[@id="J_isku"]/div/dl/dd/ul[@data-property="{}"]/li/a/@style'.format(title)).extract()]
                r.append(j)

            result['options'] = r

            result_ls.append(result)
            print("itemid : {} 가격 정보 가져옴".format(itemid))

        driver.quit()
        return result_ls


# if __name__ == "__main__":
#     crawler = ProductCrawler()
#     print(crawler.taobao_crawler(sys.argv[1], sys.argv[2], sys.argv[3]))
    
