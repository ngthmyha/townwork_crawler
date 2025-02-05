from multiprocessing import Pool
import subprocess

def run_spider(index):
    subprocess.run(["poetry", "run", "scrapy", "crawl", "detail"])

if __name__ == '__main__':
    pool = Pool(processes=4)
    pool.map(run_spider, range(4))