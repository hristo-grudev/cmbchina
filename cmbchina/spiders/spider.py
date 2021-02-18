import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CmbchinaItem
from itemloaders.processors import TakeFirst


class CmbchinaSpider(scrapy.Spider):
	name = 'cmbchina'
	start_urls = ['https://www.cmbchina.com/cmbinfo/news/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="c_list"]/ul/li')
		for post in post_links:
			url = post.xpath('./span[@class="c_title"]/a/@href').get()
			date = post.xpath('./span[@class="c_date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//div[@class="pager_right"]/a[contains(text(),"下一页")]/@href').getall()
		yield from response.follow_all(next_page, self.parse)


	def parse_post(self, response, date):
		title = response.xpath('//div[@class="c_header"]/span/text()').get()
		description = response.xpath('//div[@class="c_content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		if date:
			date = re.findall(r'\d+-\d+-\d+', date)[0]

		item = ItemLoader(item=CmbchinaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()