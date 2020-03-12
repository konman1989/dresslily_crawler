import scrapy
from ..items import DresslilyScrapyProduct, DresslilyScrapyReview


class ProductsSpider(scrapy.Spider):
    name = "products_spider"
    start_urls = [
        "https://www.dresslily.com/hoodies-c-181.html"
    ]
    custom_settings = {
        # specifies exported fields and order
        'FEED_EXPORT_FIELDS': [
            "product_id",
            "product_url",
            "product_name",
            "discount",
            "discount_price",
            "original_price",
            "rating",
            "product_info"
        ]
    }

    def parse(self, response):
        for item in response.css('.js-good'):
            url = item.css('.category-good-name a::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.parse_product)

        next_page = response.css(
            'div[class="site-pager-pad-pc site-pager"] a::attr(href)')[-1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_product(self, response):
        items = DresslilyScrapyProduct()
        product_id = response.css('.sku-show::text').get()
        product_url = response.url
        product_name = response.css('.goodtitle::text').get()
        original_price = response.css(
            'span[class="js-dl-marketPrice marketPrice my-shop-price dl-has-rrp-tag"]::attr(data-orgp)').get()
        rating = response.css('.review-avg-rate::text').get()
        try:
            discount = response.css('title::text').re(r'\[(\d+%)')[0]
        except IndexError:
            discount = 0

        if discount == 0:
            discount_price = 0
        else:
            discount_price = response.css(
                'span[class="curPrice my-shop-price js-dl-curPrice"]::attr(data-orgp)').get()

        # joining product info string
        keys = response.css('.xxkkk20 strong::text').getall()
        values = response.css('.xxkkk20').re('</strong> ([a-zA-Z0-9., ]+)')
        product_info = ""
        for i in range(len(keys)):
            product_info += f"{keys[i]}{values[i].strip()};"

        items["product_id"] = product_id
        items["product_url"] = product_url
        items["product_name"] = product_name
        items["discount"] = discount
        items["discount_price"] = discount_price or 0
        items["original_price"] = original_price
        items["rating"] = rating or "undefined"
        items["product_info"] = product_info

        yield items


class ReviewsSpider(scrapy.Spider):
    name = "reviews_spider"
    start_urls = [
        'https://www.dresslily.com/hoodies-c-181.html'
    ]
    custom_settings = {
        # specifies exported fields and order
        'FEED_EXPORT_FIELDS': [
            "product_id",
            "rating",
            "timestamp",
            "text",
            "size",
            "color"
        ]
    }

    def parse(self, response):
        for item in response.css('.js-good'):
            url = item.css('.category-good-name a::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.check_review)

        next_page = response.css(
            'div[class="site-pager-pad-pc site-pager"] a::attr(href)')[-1].get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)

    def check_review(self, response):
        # checking if reviews exist
        if response.css(
                "div[class='good-hgap review_con']").get() is not None:
            id_ = response.css(
                "div[class='good-hgap review_con'] a::attr(href)").re(r'-(\d+).htm')[0]
            url = f"https://www.dresslily.com/m-review-a-view_review-goods_id-{id_}.html"
            yield scrapy.Request(url=url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        items = DresslilyScrapyReview()
        for item in response.css('div[class="reviewlist clearfix"]'):
            product_id = response.css('.curPrice span::attr(data-sku)').get()
            rating_list = item.css('p[class="starscon_b dib"]').re(r'icon-star-(\w+)')
            rating = len([i for i in rating_list if i == "black"])
            timestamp = item.css('.reviewtime::text').get()
            text = item.css('.reviewcon::text').get()
            try:
                size = item.css('.color-size span::text')[0].get()
            except IndexError:
                size = "undefined"
            try:
                color = item.css('.color-size span::text')[1].get()
            except IndexError:
                color = "undefined"

            items["product_id"] = product_id
            items["rating"] = rating
            items["timestamp"] = timestamp
            items["text"] = text
            items["size"] = size
            items["color"] = color

            yield items

        try:
            next_page = response.css(
                'div[class="site-pager review-pager"] a::attr(href)')[
                -1].get()
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_reviews)
        except IndexError:
            pass


class ReviewsSpiderLinks(scrapy.Spider):

    """This class is worth it to work with when products list is already
    fetched and stored into csv(or json) file. It checks if the product has
    reviews, fetches its link and parses all the information from there"""

    name = "reviews_spider_links"
    file_path = ""

    # with open(file_path) as file:
    #     data = csv.DictReader(file)
    #     start_urls = [i['product_url'] for i in data if i['rating'] != 'undefined']

    def parse(self, response):
        # checking if reviews exist
        if response.css("div[class='good-hgap review_con']").get() is not None:
            id_ = response.css("div[class='good-hgap review_con'] a::attr(href)").re(r'-(\d+).htm')[0]
            url = f"https://www.dresslily.com/m-review-a-view_review-goods_id-{id_}.html"
            yield scrapy.Request(url=url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        items = DresslilyScrapyReview()
        for item in response.css('div[class="reviewlist clearfix"]'):
            product_id = response.css('.curPrice span::attr(data-sku)').get()
            rating_list = item.css('p[class="starscon_b dib"]').re(
                r'icon-star-(\w+)')
            rating = len([i for i in rating_list if i == "black"])
            timestamp = item.css('.reviewtime::text').get()
            text = item.css('.reviewcon::text').get()
            try:
                size = item.css('.color-size span::text')[0].get()
            except IndexError:
                size = "undefined"
            try:
                color = item.css('.color-size span::text')[1].get()
            except IndexError:
                color = "undefined"

            items["product_id"] = product_id
            items["rating"] = rating
            items["timestamp"] = timestamp
            items["text"] = text
            items["size"] = size
            items["color"] = color

            yield items

        try:
            next_page = response.css('div[class="site-pager review-pager"] a::attr(href)')[-1].get()
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse_reviews)
        except IndexError:
            pass
