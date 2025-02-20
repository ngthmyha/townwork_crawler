import scrapy
import datetime
import csv
import os

class DetailSpider(scrapy.Spider):
    name = "detail"

    @staticmethod
    def get_existing_urls(filenames):
        urls = set()
        for filename in filenames:
            if os.path.exists(filename):
                with open(filename, newline="", encoding="utf-8") as csvfile:
                    urls.update(row["url"].strip() for row in csv.DictReader(csvfile) if row.get("url"))
        return urls

    def start_requests(self):
        existing_urls = self.get_existing_urls(["job_data.csv", "error.csv"])
        
        with open("job_urls.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)

            for row in reader:
                url = row[0].strip()
                if url and url not in existing_urls:
                    yield scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={"handle_httpstatus_all": True})

    def parse(self, response):
        if response.status != 200:
            self.log_error(response.url, response.status)
            return
        
        job_details = {
            "url": response.url,
            "corporate_number": None, 
            "corporate_name": self.extract_field(response, "社名"),
            "address": self.extract_field(response, "会社住所"),
            "tel": self.extract_field(response, "代表電話番号"),
            "fax": None, 
            "company_url": self.extract_field(response, "ホームページリンク"),
            "email": None, 
            "capital": None, 
            "employee": None, 
            "established": None, 
            "crowl_at": datetime.datetime.now(),
            "site_id": 6,
        }
        
        self.save_to_csv(job_details)
        yield job_details

    def extract_field(self, response, field_name):
        return response.xpath(
            f'//dl[@class="job-ditail-tbl-inner"][dt[contains(text(),"{field_name}")]]/dd'
        ).xpath('string(.)').get(default="").strip()

    def save_to_csv(self, data, filename="job_data.csv"):
        file_exists = os.path.exists(filename)
        
        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def log_error(self, url, status, filename="error.csv"):
        file_exists = os.path.exists(filename)
        
        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["url", "status"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({"url": url, "status": status})