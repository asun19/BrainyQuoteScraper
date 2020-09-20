import requests
import bs4
import re
import pprint
import csv
from multiprocessing import Pool
from time import sleep


def scrape(main_url):
    '''
    Goes through every page of a topic and extract quotes one by one.
    Return:list of tuples: (quote: str, author: str, keywords: list[str])
    '''
    # START READING FROM HERE
    response = requests.get(main_url + '/topics')
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Finds category list from https://www.brainyquote.com/topics
    # and accesses them one by one
    category_elem = soup.find_all('a', href=re.compile('topics/'))
    topic_links = [main_url + elem.get('href') for elem in category_elem]
    assert len(topic_links) == 125

    p = Pool(12)
    p.map(topic_page_scrape, topic_links)
    p.terminate()
    p.join()


def topic_page_scrape(topic_url):
    while True:
        while True:
            topic_response = requests.get(topic_url)
            print(f'Scraping from {topic_url}...')
            status = topic_response.raise_for_status()
            if status is not None:
                sleep(5)
                print('Error while getting topic page, retrying...')
            else:
                break
        '''
        topic_response = requests.get(topic_url)
        print(f'Scraping from {topic_url}...')
        try:
            topic_response.raise_for_status()
        except requests.exceptions.HTTPError:
            sleep(5)
            topic_response = requests.get(topic_url)
            print('HTTPError, retrying...')
            print(f'Scraping from {topic_url}...')
            topic_response.raise_for_status()
        '''
        topic_soup = bs4.BeautifulSoup(topic_response.text, 'html.parser')

        # quotes: list[str]
        quote_elem = topic_soup.find_all('a', href=re.compile('/quotes'))
        quotes = [elem.string for elem in quote_elem]

        # authors: list[str]
        author_elem = topic_soup.find_all('a',
                                          href=re.compile('/authors'),
                                          title='view author')
        authors = [elem.string for elem in author_elem]

        # keywords: list[list[str]]
        keyword_box_elem = topic_soup.find_all('div', class_='kw-box')
        keywords = [[elem.string for elem in keyword_box.find_all('a')]
                    for keyword_box in keyword_box_elem]
        # pprint.pprint(keywords)
        with open('BrainyQuotes.csv', 'a', newline='', encoding='utf-8') as output:
            output_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for line in list(zip(quotes, authors, keywords)):
                output_writer.writerow(line)

        next_tag = topic_soup.find_all('a', string='Next', class_=None)
        # next page in topic...
        if len(next_tag) == 1:
            topic_url = main_url + next_tag[0].get('href')
        else:
            break
    return None


main_url = 'https://www.brainyquote.com'
if __name__ == '__main__':
    scrape(main_url)
'''
    1 Process: 2140.391s
    4 processes: 467.444s
    8 processes: 259.568s
    16 processes:
'''
