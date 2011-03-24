import re

from datetime import date
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from market_rent.items import MarketRentItem

class DbhSpider(CrawlSpider):
    name = 'dbh'
    allowed_domains = ['dbh.govt.nz']
    start_urls = ['http://www.dbh.govt.nz/market-rent']
    base_url = 'http://www.dbh.govt.nz'

    # rules = (
    #     Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_region', follow=True),
    # )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        url = self.base_url + "/" + hxs.select('/html/body/form[@id="Form1"]/@action').extract()[0]
        viewstate = hxs.select('//input[@id="__VIEWSTATE"]/@value').extract()[0]
        
        for tr in hxs.select('//div[@id="MarketRent1_pnlRegion"]/div/table/tr[position() > 1 and position() < last()]'):
        # for tr in hxs.select('//div[@id="MarketRent1_pnlRegion"]/div/table/tr[position() > 1 and position() < 4]'):
            formdata = {}
            formdata['__VIEWSTATE'] = viewstate
            formdata['__EVENTTARGET'] = ''
            formdata['__EVENTARGUMENT'] = ''
            formdata['__VIEWSTATEENCRYPTED'] = ''
            formdata[tr.select('td/input/@name').extract()[0]] = tr.select('td/input/@value').extract()[0]
            region = tr.select('td/input/@title').extract()[0]
            yield FormRequest(url,
                formdata=formdata,
                callback=lambda r, region=region:self.parse_district(r, region))

    def parse_district(self, response, region):
        # self.log("Parsing Region: " + region + "...")
        hxs = HtmlXPathSelector(response)
        url = self.base_url + "/Utilities/marketrent/" + hxs.select('/html/body/form[@id="Form1"]/@action').extract()[0]
        viewstate = hxs.select('//input[@id="__VIEWSTATE"]/@value').extract()[0]
        
        for tr in hxs.select('//div[@id="MarketRent1_pnlLocation"]/div/table/tr[position() > 1]'):
        # for tr in hxs.select('//div[@id="MarketRent1_pnlLocation"]/div/table/tr[position() > 1 and position() < 4]'):
            formdata = {}
            formdata['__VIEWSTATE'] = viewstate
            formdata['__EVENTTARGET'] = ''
            formdata['__EVENTARGUMENT'] = ''
            formdata['__VIEWSTATEENCRYPTED'] = ''
            formdata[tr.select('td/input/@name').extract()[0]] = tr.select('td/input/@value').extract()[0]
            (district, area) = tr.select('td/input/@title').extract()[0].split(' - ')
            yield FormRequest(url,
                formdata=formdata,
                callback=lambda r, region=region, district=district, area=area:self.parse_area(r, region, district, area))

    def parse_area(self, response, region, district, area):
        # self.log("Parsing Area: " + region + " > " + district + " > " + area + "...")
        hxs = HtmlXPathSelector(response)
        items = []
        
        for tr in hxs.select('//div[@id="MarketRent1_pnlMarketRent"]/div/table/tr[position() > 1]'):
            i = MarketRentItem();
            i['date_type'] = 'range'
            i['start_date'] = date(2010, 9, 1)
            i['end_date'] = date(2011, 2, 28)
            i['region'] = region
            i['district'] = district
            i['area'] = area
            i['bedrooms'] = tr.select('td[1]/text()').extract()[0]
            i['dwelling'] = tr.select('td[2]/text()').extract()[0]
            i['bonds_received'] = tr.select('td[3]/text()').extract()[0]
            i['average_rent'] = tr.select('td[4]/text()').extract()[0][1:]
            i['std'] = tr.select('td[5]/text()').extract()[0]
            i['lower_quartile'] = tr.select('td[6]/text()').extract()[0][1:]
            i['median_rent'] = tr.select('td[7]/text()').extract()[0][1:]
            i['upper_quartile'] = tr.select('td[8]/text()').extract()[0][1:]
            items.append(i)
        return items
