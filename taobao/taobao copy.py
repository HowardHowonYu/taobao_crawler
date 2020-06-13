import sys

class ProductCrawler():

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
        options = webdriver.ChromeOptions()
        options.add_argument(userAgent)
        
        driver = webdriver.Chrome('./chromedriver', options=options)

        driver.get("https://item.taobao.com/item.htm?id={}".format(itemid))

        # control alert window 
        try:
            alert = driver.switch_to_alert()
            alert.accept()
            current_url = driver.current_url
        except:
            current_url = driver.current_url

        print("사이트 체크 완료")
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

        # driver = webdriver.Chrome('./chromedriver')
        # driver.get("https://www.taobao.com")

        # # load cookies to get information about 'Promotion Price'
        # # have to find better approach

        # f = open('cookie_taobao.dat', 'rb')
        # cookies = pickle.load(f)
        # for cookie in cookies:
        #     driver.add_cookie(cookie)

        driver = self.set_cookies()

        driver.get("https://item.taobao.com/item.htm?id={}".format(itemid))

        result = {}

        # item id
        result['item_id'] = itemid

        # Tmall has two options of 'Promotion Price'
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
        # requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'

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

        # driver = webdriver.Chrome('./chromedriver')
        # driver.get("https://www.taobao.com")

        # f = open('cookie_taobao.dat', 'rb')
        # cookies = pickle.load(f)
        # for cookie in cookies:
        #     driver.add_cookie(cookie)
        # driver.get("https://item.taobao.com/item.htm?id={}".format(itemid))

        driver = self.set_cookies()

        result = {}
        result['item_id'] = itemid

        # 할인 가격
        try:
            result['promo_price'] = driver.find_element_by_css_selector(
                '#J_PromoPriceNum').text
        except:
            result['promo_price'] = '할인 가격 없음'

        driver.quit()

        # Use 'requests' to get rest of information
        ua = UserAgent(verify_ssl=False)
        userAgent = ua.random

        headers = {
            'User-Agent': userAgent
        }

        url = "https://item.taobao.com/item.htm?id={}".format(itemid)

        # https://stackoverflow.com/questions/32910093/python-requests-gets-tlsv1-alert-internal-err
        # requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'

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

    def set_cookies(self):
        from selenium import webdriver
        import pickle

        driver = webdriver.Chrome('./chromedriver')
        driver.get("https://www.taobao.com")

        # load cookies to get information about 'Promotion Price'
        # have to find better approach
        f = open('cookie_taobao.dat', 'rb')
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

        return driver
        # if __name__ == "__main__":
        #     crawler(sys.argv[1])
