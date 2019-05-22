import requests
from threading import Thread
from lxml import html


def get_seller(url):
    item_tree = html.fromstring(requests.get(url).content)
    return item_tree.xpath("//a[contains(@href, 'https://allegro.pl/uzytkownik/')]")[0].text_content()


def search(item):
    user_data = {}
    r = requests.get(get_search_url(item))
    tree = html.fromstring(r.content)

    pages = int(get_max_pages(tree))
    results = get_result_count(tree)

    print("Scrapping search: %s. Found %s results, %s pages..." % (item, results, pages))

    result_data = [{} for x in range(pages)]
    threads = []
    for page in range(1, pages):
        process = Thread(target=fetch_page, args=[item, result_data, page])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()

    for result in result_data:
        join_results(user_data, result)
    print(user_data)

    for user in user_data:
        print(user)
        for search in user_data[user]:
            print("    %s %d" % (search, len(user_data[user][search])))
    print(len(user_data))
    return user_data

#TODO: remove duplicates
def join_results(result_one, result_two):
    for key in result_two:
        if key in result_one:
            for search_id in result_two[key]:
                if search_id in result_one[key]:
                    result_one[key][search_id] += result_one[key][search_id]
                else:
                    result_one[key][search_id] = result_two[key][search_id]
        else:
            result_one[key] = result_two[key]


def fetch_page(item, result_data, page):
    r = requests.get(get_search_url(item, page))
    tree = html.fromstring(r.content)
    single_page_data = {}
    for el in tree.xpath('//article'):
        a_el = el.xpath('.//a')
        if len(a_el) == 2:
            title = a_el[1].text_content()
            link = a_el[1].get('href')
            image = a_el[0].xpath('.//img')[0].get('data-src')
            if image is None:
                continue
            seller = get_seller(link)
            if seller in single_page_data:
                if item in single_page_data[seller]:
                    single_page_data[seller][item].append(get_item_dict(title, link, image))
                else:
                    single_page_data[seller][item] = [get_item_dict(title, link, image)]
            else:
                single_page_data[seller] = {item: [get_item_dict(title, link, image)]}
    result_data[page-1] = single_page_data


def get_result_count(tree):
    return tree.xpath("//span[contains(@class,'listing-title__counter-value')]")[0].text_content()


def get_max_pages(tree):
    return tree.xpath('//input[@data-maxpage]')[0].get('data-maxpage')


def get_item_dict(title, link, image):
    return {
        "title": title,
        "link": link,
        "image": image
    }


def get_search_url(item, page=None):
    if page:
        page = '&p=%s' % page
    else:
        page = ''
    return replace_url_spaces('https://allegro.pl/listing?string=%s%s' % (item, page))


def get_seller_search_url(seller, item):
    return replace_url_spaces('https://allegro.pl/uzytkownik/%s?string=%s' % (seller, item))


def replace_url_spaces(url):
    return url.replace(" ", "%20")

search("roborock")