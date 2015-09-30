from bs4 import BeautifulSoup
import datetime
import requests
import re
from Book import Book
import csv
from multiprocessing import Pool

all_books = {}
def parse_book_row(top_book, seen, category):
    info = top_book.find("td", {"class" : "summary"})
    title = info.find("span", {"class": "bookName"}).get_text().rstrip(", ").lower()
    try:
        author = re.search("(?<=by ).*(?=. \()", info.get_text()).group(0)
    except AttributeError:
        author = "UNPARSEABLE"
    ranking = top_book.find("span", {"class": "ranking"}).get_text()
    if title in all_books.keys():
        all_books[title].update(seen, ranking)
    else:
        all_books[title] = Book(title, author, seen, ranking, category )

def crawl_category_for_date(category, date):
    try:
        response = requests.get("http://www.nytimes.com/best-sellers-books/{}/{}/list.html".format(date, category))
        if response.status_code == 200:
            raw_html = response.content
            soup_html = BeautifulSoup(raw_html, "html.parser")
            for top_book in soup_html.find_all("tr", {"class": "bookDetails"}):
                parse_book_row(top_book, date, category)
    except Exception as e:
        print("ERROR FETCHING FROM {} on {}:{}".format(category, date, e))


def crawl_category(category):
    dates = [(today - datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0,730)]
    dates.reverse()
    for date in dates:
        print("Crawling category:  {} on date:{}".format(category, date))
        crawl_category_for_date(category, date)

if __name__=="__main__":
    today = datetime.datetime.now()
    categories = ["hardcover-fiction", "hardcover-nonfiction", "mass-market-paperback", "paperback-nonfiction", "young-adult", "series-books", "e-book-fiction", "e-book-nonfiction"]

    taskPool = Pool(8)
    taskPool.map(crawl_category, categories)
    taskPool.join()


    with open("top_books.csv", "w", ) as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(["Category", "Title", "Author", "Highest Rank Achieved", "First Appearance", "Last appearance"])
        for book in all_books.values():
            print("title: {}\tauthor: {}\thighest rank: {}\t first seen: {}\tlast seen: {}".format(book.name, book.author, book.highest_rank, book.first_seen, book.last_seen))
            writer.writerow([book.category, book.name, book.author, book.highest_rank, book.first_seen, book.last_seen])

