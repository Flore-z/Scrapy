import scrapy
from wordbook.items import WordbookItem
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait


class WordbookSpider(scrapy.Spider):
    name = "wordbook"
    allowed_domains = ["shanbay.com"]
    start_urls = [
        "https://www.shanbay.com/wordbook/180781/",
        "https://www.shanbay.com/wordbook/176890/",
        "https://www.shanbay.com/wordbook/120580/",
        "https://www.shanbay.com/wordbook/202/",
        "https://www.shanbay.com/wordbook/7/",
        "https://www.shanbay.com/wordbook/6/"
    ]

    def parse(self, response):
        units = response.xpath('//a/@href').extract()
        units = [url for url in units if url.startswith( '/wordlist/{}/'.format(response.url.split('/')[-2]))]
        book_name = response.xpath('/html/body/div[3]/div/div[1]/div/div[1]/div[2]/div[1]/a/text()').extract()[0]
        # print(book_name)
        n_unit = 0

        for url in units:
            n_unit += 1
            item = WordbookItem()
            item['word'] = []
            item['meaning'] = []

            yield scrapy.Request(url='https://www.shanbay.com/' + url,
                                 meta={'item': item, 'book': book_name, 'unit': n_unit},
                                 callback=self.parse_item)

    def parse_item(self, response):
        book_name = response.meta['book']
        # print(book_name)
        driver = webdriver.Chrome()     # use Chrome web driver
        driver.get(response.url)

        while 1:
            item_page = WordbookItem()
            item_page['word'], item_page['meaning'] = [], []

            word_elem = driver.find_elements_by_xpath('//tbody/tr[@class="row"]/td[@class="span2"]/strong')
            meaning_elem = driver.find_elements_by_xpath('//tbody/tr[@class="row"]/td[@class="span10"]')
            item_page['word'] += [w.text for w in word_elem]
            item_page['meaning'] += [m.text for m in meaning_elem]

            response.meta['item']['word'] += item_page['word']
            response.meta['item']['meaning'] += item_page['meaning']

            buttons = driver.find_elements_by_xpath('//*[@id="pagination"]/div/ul/li')
            next_page = driver.find_element_by_xpath('//*[@id="pagination"]/div/ul/li[{}]/a'.format(len(buttons)))
            sign = buttons[-1].get_attribute("class")
            if sign == "disabled":
                print("Arrive the last page.")
                break
            next_page.click()

        driver.quit()
        yield {0: book_name, 1: response.meta['unit'], 2: response.meta['item']}