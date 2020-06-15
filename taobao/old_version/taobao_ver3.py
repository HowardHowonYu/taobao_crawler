from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random
import time
import sys

class ProductCrawler():
 
    def __mall_login__(self, itemid, user_id, user_pw, mall_name):
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
        driver.get("https://item.taobao.com/item.htm?id={}".format(itemid))

        # control alert window
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            time.sleep(1)

        # log_in, taobao or tamll
        try:
            driver.switch_to_frame("sufei-dialog-content")

        except:
            driver.switch_to_frame('baxia-dialog-content')


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
            if mall_name == "taobao":
                webdriver.ActionChains(driver).click_and_hold(
                    swipe_btn).move_to_element_with_offset(swipe_btn, 400, 10).release().perform()
                time.sleep(1)

            else:
                print('tmall')
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


    def product_crawler(self, itemids, user_id, user_pw):
        """        
        Check the url for confirm the mall first - taobao or tmall
        if you have information of mall, you can select one method directly.
          - taobao : taobao_crawler()
          - tmall : tmall_crawler()
        """

        from selenium import webdriver

        driver = webdriver.Chrome('./chromedriver')

        driver.get("https://item.taobao.com/item.htm?id={}".format(itemids[0]))

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
            return self.tmall_crawler(itemids, user_id, user_pw)
        else:
            return self.taobao_crawler(itemids, user_id, user_pw)


    def tmall_crawler(self, itemids, user_id, user_pw):
        from selenium import webdriver
        from scrapy.http import TextResponse
        from fake_useragent import UserAgent

        import requests

        driver = self.__mall_login__(
            itemids[0], user_id, user_pw, "tmall")

        # itemid를 list 형태로 받아서 for문으로 돌릴 준비
        result_ls = []
        num = 0
        cookies = driver.get_cookies()

        for cookie in cookies:
            driver.add_cookie(cookie)

        for itemid in itemids[::-1]:
            result = {}

            url = "https://detail.tmall.com/item.htm?id={}".format(itemid)
            
            driver.get(url)

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

            # make userAgent randomly
            userAgent = UserAgent(verify_ssl=False).random
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
            
            option_path = req.xpath(
                '//*[@id="J_DetailMeta"]/div/div/div/div[@class="tb-key"]/div[@class="tb-skin"]/div[@class="tb-sku"]/dl[contains(@class, "tm-sale-prop") and contains(@class, "tb-prop") and contains(@class, "tm-clear")]')
            option_ls = []
            for path in option_path:
                option = {}
                option['option_title'] = path.xpath('dt/text()').extract_first()
                option['option_details'] = path.xpath('dd/ul/li/a/span/text()').extract()
                image_elements = path.xpath('dd/ul[contains(@class, "tb-img")]/li/a')
                try:
                    option['option_image_urls'] = [element.xpath('@style').extract_first()[
                        17:-50]+".jpg" for element in image_elements]
                except:
                    option['option_image_urls'] = []

                option_ls.append(option)
                result['options'] = option_ls

            result_ls.append(result)
            print("itemid : {} 가격 정보 가져옴".format(itemid))

        driver.quit()

        return result_ls


    def taobao_crawler(self, itemids, user_id, user_pw):
        from selenium import webdriver
        from scrapy.http import TextResponse
        from fake_useragent import UserAgent
        
        import requests
        
        driver = self.__mall_login__(
            itemids[0], user_id, user_pw, "taobao")

        cookies = driver.get_cookies()

        for cookie in cookies:
            driver.add_cookie(cookie)
        
        result_ls = []
        for itemid in itemids[::-1]:
            url = "https://item.taobao.com/item.htm?id={}".format(itemid)
            driver.get(url)

            result = {}
            result['item_id'] = itemid
            result['title'] = driver.find_element_by_xpath('//*[@id="J_Title"]/h3').text

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

            # url = "https://item.taobao.com/item.htm?id={}".format(itemid)

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

            result_ls.append(result)
            print("itemid : {} 가격 정보 가져옴".format(itemid))

        driver.quit()
        return result_ls


if __name__ == "__main__":
    crawler = ProductCrawler()
    print(crawler.product_crawler(sys.argv[1], sys.argv[2], sys.argv[3]))
    
