import scrapy, csv, os
from urllib.parse import urljoin

class JobSpider(scrapy.Spider):
    name = "job"
    start_urls = ["https://townwork.net/?arc=1"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def parse(self, response):
        area_links = response.css("nav.area-sch-box a::attr(href)").getall()
        print(area_links)
        for link in area_links:
            area_name = link.strip("/").replace("/", "_")
            file_name = f"job_urls_{area_name}.csv"

            full_link = urljoin(response.url, link)
            yield scrapy.Request(full_link, callback=self.parse_category, headers=self.headers, meta={"file_name": file_name})
    
    def parse_category(self, response):
        category_links = response.css("div.jsc-small-area-wrapper a::attr(href)").getall()
        
        for link in category_links:
            full_link = urljoin(response.url, link)
            yield scrapy.Request(full_link, callback=self.parse_jobs, headers=self.headers, meta={"file_name": response.meta["file_name"]})
    
    def parse_jobs(self, response):
        file_name = "job_urls.csv"
        if not os.path.exists(file_name):
            with open(file_name, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Job URL"])
        file = open(file_name, "a", newline="", encoding="utf-8")
        writer = csv.writer(file)
        for job in response.css(".job-lst-main-cassette-wrap"):
            first_link = job.css("a::attr(href)").get()  

            if first_link:
                full_link = urljoin(response.url, first_link)
                writer.writerow([full_link])
                yield {"job_url": full_link}
        
        # Kiểm tra và xử lý phân trang
        next_page = response.css("div.pager-next-btn a::attr(href)").get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(next_page_url, callback=self.parse_jobs, headers=self.headers, meta={"file_name": file_name})