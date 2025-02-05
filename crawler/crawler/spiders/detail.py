import scrapy
import datetime, csv, re
import pandas as pd
import os

class DetailSpider(scrapy.Spider):
    name = "detail"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    # start_urls = ["https://townwork.net/detail/clc_3016185005/"]

    def count_rows(self, filename):
        """Đếm số hàng trong file CSV"""
        if not os.path.exists(filename):  # Nếu file chưa tồn tại, trả về 0
            return 0
        
        with open(filename, newline="", encoding="utf-8") as csvfile:
            return sum(1 for _ in csvfile) - 1

    def start_requests(self):
        job_data_count = self.count_rows("job_data.csv")
        with open("job_urls.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader) 
            for index, row in enumerate(reader):
                if index < job_data_count:
                    continue
                
                url = row[0].strip()
                if url:
                    yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, dont_filter=True, meta={"handle_httpstatus_list": [301, 302]})
        # for url in self.start_urls:
        #     if url:
        #         yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)    

    def parse(self, response):
        now = datetime.datetime.now()

        print(response.xpath(
            '//dl[@class="job-ditail-tbl-inner"]'
            '[dt[contains(text(), "社名")]]/dd//p/text()'
        ).get(default="").strip())

        job_details = {
            "Corporate_number": None, 
            "Corporate_name": self.extract_field(response, "社名"),
            "Address": self.extract_field(response, "会社住所"),
            "Tel": self.extract_field(response, "代表電話番号"),
            "Fax": None, 
            "Company_url": self.extract_field(response, "ホームページリンク"),
            "Email": None, 
            "Capital": None, 
            "Employee": None, 
            "Established": None, 
            "Crowl_at": now,
            "Site_id": 6,
        }
        self.save_to_csv(job_details)
        yield job_details

    def extract_field(self, response, field_name):
        result = response.xpath(
            f'//dl[@class="job-ditail-tbl-inner"][dt[contains(text(),"{field_name}")]]/dd'
        ).xpath('string(.)').get(default="").strip()

        return result
    
    def save_to_csv(self, data, filename="job_data.csv"):
        file_exists = False
        try:
            with open(filename, "r", encoding="utf-8") as f:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader() 

            writer.writerow(data)