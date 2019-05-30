import requests
from threading import Thread
from lxml import html


def get_seller(url):
    item_tree = html.fromstring(requests.get(url).content)
    return item_tree.xpath("//a[contains(@href, 'https://allegro.pl/uzytkownik/')]")[0].text_content()


def search(item):
    r = requests.get(get_search_url(item))
    tree = html.fromstring(r.content)

    pages = int(get_max_pages(tree))
    results = get_result_count(tree)

    print("Scrapping search: %s. Found %s results, %s pages..." % (item, results, pages))

    result_data = []
    threads = []
    for page in range(1, pages + 1):
        process = Thread(target=fetch_page, args=[item, result_data, page])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()
    print(result_data)
    return result_data


def parse_results(results_data):
    data = {}
    for result in results_data:

        if result["seller"] not in data:
            data[result["seller"]] = {}
        if result["search"] not in data[result["seller"]]:
            data[result["seller"]][result["search"]] = []
        data[result["seller"]][result["search"]].append({
            "title": result["title"],
            "link": result["link"],
            "image": result["image"]})
    return data

def fetch_page(item, result_data, page):
    r = requests.get(get_search_url(item, page))
    tree = html.fromstring(r.content)
    for el in tree.xpath('//article'):
        a_el = el.xpath('.//a')
        if len(a_el) == 2:
            title = a_el[1].text_content()
            link = a_el[1].get('href')
            image = a_el[0].xpath('.//img')[0].get('src')
            price = el.xpath('.//div[1]/div[1]/div[2]/div[2]/div[1]') #TODO price
            #print(price)
            if image is None:
                continue
            seller = get_seller(link)
            result_data.append(get_item_dict(item, seller, title, price, link, image))


def get_result_count(tree):
    return tree.xpath("//span[contains(@class,'listing-title__counter-value')]")[0].text_content()


def get_max_pages(tree):
    return tree.xpath('//input[@data-maxpage]')[0].get('data-maxpage')


def get_item_dict(search, seller, title, price, link, image):
    return {
        "search": search,
        "seller": seller,
        "title": title,
        "price": price,
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


s1 = search("klamka kanapy")
s2 = search("zestaw naprawczy bagaznika")
s1.extend(s2)

res = parse_results(s1)

out = dict(res)

for s in res:
    if len(res[s]) < 2:
        out.pop(s)

print(out)

#fetch_page("klamka kanapy", result, 3)


