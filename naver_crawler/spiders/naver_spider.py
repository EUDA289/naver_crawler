import scrapy
import re
from naver_crawler.items import NaverCrawlerItem
from datetime import datetime, timedelta

class NaverSpider(scrapy.Spider):
    name = "naver"

    def start_requests(self):
        date1 = 0
        date2 = 0
        #네이버 뉴스 페이지가 400이 한계-> 일주일별로 나눠서 검색하여 파싱한다
        while True: # 19년도 까지만 크롤링 할 예정

            time_start = datetime(2017,1,1) # 크롤링할 시작 날짜
            if date1 != 0:
                date1 = date1 + timedelta(days=2)
                date2 = date1 + timedelta(days=1)
                #날짜 format바꿈
                ds = datetime.strftime(date1,'%Y.%m.%d')
                de = datetime.strftime(date2,'%Y.%m.%d')
                
                #2018년 넘어가면 작업 중지
                if date1.day == 3:
                    break
            else : 
                date1 = time_start
                date2 = date1 + timedelta(days=1)
                ds = datetime.strftime(date1,'%Y.%m.%d')
                de = datetime.strftime(date2,'%Y.%m.%d')


            url_org = 'https://search.naver.com/search.naver?where=news&query=%EA%B8%88%EB%A6%AC&sm=tab_opt&sort=2&pd=3&ds={}&de={}'.format(ds, de)
            yield scrapy.Request(url=url_org, callback=self.parse_url_num)

        # data = json.loads('items.json')
        # for 
            # item = NaverCrawlerItem()
            # yield scrapy.Request(url=item['url'], callback=self.parse_body)
    def parse_url_num(self, response):

        article_num=re.findall('\d+',response.xpath('//*[@id="main_pack"]/div[2]/div[1]/div[1]/span/text()').extract()[0].split(' ')[-1].replace(',',''))[0]
        print(article_num,'------------'*3)

        #마지막 페이지넘버계산
        max_page = (int(article_num)//10 +1)*10+1
        # print(max_page,'-----------------')
        for i in range(1,max_page,10):
            
            url=response.url+'&start={}'.format(i)

            yield scrapy.Request(url=url, callback=self.parse_url)
            
    def parse_url(self, response):

        for sel in response.xpath('//*[@id="main_pack"]/div/ul/li'):
            
            med = sel.xpath('dl/dd/span[1]/text()').extract()[0]
            if med=='연합뉴스'or med =='이데일리':               
                url=sel.xpath('dl/dd/a/@href').extract()[0]
                yield scrapy.Request(url=url, callback=self.parse_body, meta={'med':med})
            if med=='연합인포맥스':pass

    def parse_body(self, response):
        item = NaverCrawlerItem()
        #//*[@id="main_content"]/div[1]/div[3]/div/span[2]
        item['time'] = response.xpath('//*[@id="main_content"]/div[1]/div[3]/div/span/text()').getall()
        item['body'] = response.xpath('//*[@id="articleBodyContents"]/text()').getall()
        item['media'] = response.meta['med']
        yield item
    # def parse_body(self, response):
        
    #     item = NaverCrawlerItem()
    #     item['body'] = response.xpath('//*[@id="articleBodyContents"]/text()[1]').extract()[0]
    #     item['time'] = response.xpath('//*[@id="main_content"]/div[1]/div[3]/div/span/text()').extract()[0]
    #     item['title'] = response.xpath('//*[@id="articleTitle"]/text()').extract()[0]
    #     yield item

        # page = re.findall('start=(.*)',response.url)
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
            
        #     f.write(response.xpath())
        #self.log('Saved file')

