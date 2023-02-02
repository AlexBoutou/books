import requests
import re
import json
from bs4 import BeautifulSoup

GOODREAD_API= "https://www.goodreads.com"

def search_for_books_in_good_reads(query, page):
    print(f"Search GoodReads for {query} at page {page}")
    payload = {'q': query, "page":page}
    good_reads_search_response = requests.get(f'{GOODREAD_API}/search', params=payload)
    return good_reads_search_response

def get_number_of_books_from_soup(soup):
    h3 = soup.find("h3", class_="searchSubNavContainer")
    return int(re.search('about(.*)results', h3.string).group(1))

def return_books_links_from_single_search(query,page):
    book_list=[]
    good_reads_search_response = search_for_books_in_good_reads(query,page)
    soup = BeautifulSoup(good_reads_search_response.text, 'html.parser')
    number_of_books_to_get = get_number_of_books_from_soup(soup)
    for link in soup.find_all('a',  class_="bookTitle"):
        end_of_book_url = link.get('href').split("?")[0]
        book_list.append(f'https://www.goodreads.com/{end_of_book_url}')
    return [book_list, number_of_books_to_get]

def return_all_book_links_from_search(query):
    book_list, number_of_books_to_get=return_books_links_from_single_search(query,1)

    number_of_pages_to_parse = int(number_of_books_to_get/19+1)

    for i in range (2,number_of_pages_to_parse):
        book_list.extend(return_books_links_from_single_search(query,i)[0])

    return book_list

def return_book_info_from_link(book_link):
    book_request = requests.get(book_link)
    soup = BeautifulSoup(book_request.text, 'html.parser')
    books_infos_string = soup.find("script",type='application/ld+json').string
    json_book_string = books_infos_string.replace("'", "\"")
    book_infos_dict = json.loads(json_book_string)
    return {
        "title": book_infos_dict["name"],
        "numberOfPages":book_infos_dict["numberOfPages"],
        "author":book_infos_dict["author"][0]["name"],
        "editions_link":find_editions_in_soup(soup)
    }

def find_editions_in_soup(soup):
    work_id = 0
    for s in soup.find_all("a"):
        if ("work" in s.get('href')):
            if "quotes" in s.get('href'):
                work_id = s.get('href').split("quotes/")[1]
                return f"https://www.goodreads.com/work/editions/{work_id}"

def get_editions_for_work(edition_url, page):
    print(f"Search GoodReads Editions for {edition_url} at page {page}")
    payload = {"page":page}
    good_reads_editions = requests.get(edition_url, params=payload)
    return good_reads_editions

def return_books_editions_from_single_page(edition_url,page, check_nb_editions=False):
    french_editions=[]
    good_reads_editions = get_editions_for_work(edition_url, page)
    soup = BeautifulSoup(good_reads_editions.text, 'html.parser')
    editions_soup = soup.find_all("div",class_='elementList clearFix')
    nb_of_editions = None
    if check_nb_editions:
        nb_of_editions = get_number_of_editions_from_soup(soup)
    for edition in editions_soup:
        title = edition.find("a",class_="bookTitle").string
        for div in edition.find_all("div", string="""
                Edition language:
              """):
            language = div.find_next_sibling().string.strip()
            if language == "French":
                french_editions.append({"title":title, "language": language})
    return [french_editions, nb_of_editions]

def check_book_has_french_version(editions_link):
    french_editions, nb_of_editions=return_books_editions_from_single_page(editions_link,1, True)
    nb_of_editions_pages = int(nb_of_editions/30+1)
    if nb_of_editions_pages >1:
        for i in range (2,nb_of_editions_pages):
            french_editions.extend(return_books_editions_from_single_page(editions_link,i)[0])
    return french_editions

def get_number_of_editions_from_soup(soup):
    nb_of_editions = soup.find_all("span", class_="smallText")
    for n in nb_of_editions:
        if "Showing" in n.string:
            return int(re.search('-(.*)of', n.string).group(1))
    return None

    
