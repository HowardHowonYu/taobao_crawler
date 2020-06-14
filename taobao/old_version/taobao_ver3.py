from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import sys

class ProductCrawler():
 
    def __mall_login__(self, itemid, user_id, user_pw):
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
        chrome_options.add_argument(PROXIES[1])
        driver = webdriver.Chrome(
            './chromedriver', options=chrome_options)
        
        # login
        driver.get("https://item.taobao.com/item.htm?id={}".format(itemid))

        # control alert window
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            time.sleep(1)

        # log_in
        try:
            driver.switch_to_frame("sufei-dialog-content")
        except:
            driver.switch_to_frame('baxia-dialog-content')
        id_box = driver.find_element_by_id('fm-login-id')
        pw_box = driver.find_element_by_id('fm-login-password')
        swipe_btn = driver.find_element_by_id('nc_1_n1z')

        webdriver.ActionChains(driver).send_keys_to_element(
            id_box, user_id).send_keys_to_element(pw_box, user_pw).perform()
        time.sleep(1)

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "nc_1_n1z"))
            )

        finally:
            webdriver.ActionChains(driver).click_and_hold(
                swipe_btn).move_to_element_with_offset(swipe_btn, 400, 30).release().perform()
        time.sleep(1)

        login_btn = driver.find_element_by_class_name(
            'fm-btn').find_element_by_tag_name('button')
        webdriver.ActionChains(driver).click(login_btn).perform()


        driver.switch_to.default_content()
        print('로그인 완료')
        return driver


    def product_crawler(self, itemid):
        """        
        we check the url for confirm the mall first - taobao or tmall
        if you have information of mall, you can select one method directly.
          - taobao : taobao_crawler()
          - tmall : tmall_crawler()
        """

        from selenium import webdriver
        from fake_useragent import UserAgent

        # make userAgent randomly
        ua = UserAgent(verify_ssl=False)
        userAgent = ua.random
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(userAgent)

        driver = webdriver.Chrome('./chromedriver', options=chrome_options)

        driver.get("https://item.taobao.com/item.htm?id={}".format(itemid))

        # control alert window 
        try:
            alert = driver.switch_to_alert()
            time.sleep(1)
            alert.accept()
            current_url = driver.current_url
        except:
            current_url = driver.current_url

        print("사이트 체크 완료", current_url)

        driver.quit()

        
        if "tmall" in current_url:
            return self.tmall_crawler(itemid)
        else:
            return self.taobao_crawler(itemid)


    def tmall_crawler(self, itemid):
        from selenium import webdriver
        from scrapy.http import TextResponse
        from fake_useragent import UserAgent

        import requests

        driver = self.__mall_login__(itemid, user_id, user_pw)

        result = {}

        # item id
        result['item_id'] = itemid


        #Tmall has three options of 'Promotion Price'
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "J_PromoPrice"))
            )

        finally:
            try:
                result['og_price'] = driver.find_element_by_xpath(
                    '//*[@id="J_StrPriceModBox"]/dd/span').text
            except:
                result['og_price'] = "가격 정보 없음"

            try:
                result['promo_price_cuxiao'] = driver.find_element_by_xpath(
                '//*[@id="J_PromoPrice"]/dd/div/span').text
            except:
                result['promo_price_cuxiao'] = "가격 정보 없음"

            try:
                result['promo_price_kuang'] = driver.find_element_by_xpath('// *[@id="J_DetailMeta"]/div[1]/div[1]/div/div[2]/dl[3]/dd/span').text
            except:
                result['promo_price_kuang'] = "가격 정보 없음"

        driver.quit()

        # Use 'requests' to get rest of information
        url = "https://item.taobao.com/item.htm?id={}".format(itemid)

        ua = UserAgent(verify_ssl=False)
        userAgent = ua.random

        headers = {
            'User-Agent': userAgent
        }

        # https://stackoverflow.com/questions/32910093/python-requests-gets-tlsv1-alert-internal-err
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'

        response = requests.get(url=url, headers=headers)
        req = TextResponse(response.url, body=response.text, encoding="utf-8")

        # item_title
        result['item_title'] = req.xpath(
            '//*[@id="J_DetailMeta"]/div[@class="tm-clear"]/div[@class="tb-property"]/div/div[@class="tb-detail-hd"]/h1/text()').extract_first().strip()

        # options
        # [contains(@class, "tm-sale-prop") and contains(@class, "tb-prop") and contains(@class, "tm-clear")]
        option_path = req.xpath(
            '//*[@id="J_DetailMeta"]/div/div/div/div[@class="tb-key"]/div[@class="tb-skin"]/div[@class="tb-sku"]/dl')
        option_ls = []
        for path in option_path:
            option = {}
            option['option_title'] = path.xpath('dt/text()').extract_first()
            option['option_details'] = path.xpath('dd/ul/li/a/span/text()').extract()
            image_elements = path.xpath('dd/ul[contains(@class, "tb-img")]/li/a')
            option['option_image_urls'] = [element.xpath('@style').extract_first()[19:-40] for element in image_elements]
            option_ls.append(option)
            result['options'] = option_ls

        return result

    def taobao_crawler(self, itemid):
        from selenium import webdriver
        from scrapy.http import TextResponse
        from fake_useragent import UserAgent
        
        import pickle
        import requests
        
        driver = self.__mall_login__(itemid, user_id, user_pw)

        result = {}
        result['item_id'] = itemid
        result['title'] = driver.find_element_by_xpath('//*[@id="J_Title"]/h3').text

        # 할인 가격


        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "J_PromoPriceNum"))
            )

        finally:
            try:
                result['og_price'] = driver.find_element_by_xpath(
                    '//*[@id="J_StrPrice"]').text
                result['promo_price'] = driver.find_element_by_xpath(
                    '//*[@id="J_PromoPriceNum"]').text
            except:
                result['og_price'] = driver.find_element_by_xpath(
                    '//*[@id="J_StrPrice"]').text
                result['promo_price'] = "할인 가격 정보 없음"


        print("가격 정보 가져옴")
        driver.quit()

        # Use 'requests' to get rest of information
        ua = UserAgent(verify_ssl=False)
        userAgent = ua.random

        headers = {
            'User-Agent': userAgent
        }

        url = "https://item.taobao.com/item.htm?id={}".format(itemid)

        # https://stackoverflow.com/questions/32910093/python-requests-gets-tlsv1-alert-internal-err
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'

        response = requests.get(url=url, headers=headers)
        req = TextResponse(response.url, body=response.text, encoding="utf-8")
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

        return result


if __name__ == "__main__":
    crawler = ProductCrawler()
    print(crawler.product_crawler(sys.argv[1]))
    
