import requests
from lxml import html, etree


def get_seller(url):
    item_tree = html.fromstring(requests.get(url).content)
    return item_tree.xpath("//a[contains(@href, 'https://allegro.pl/uzytkownik/')]")[0].text_content()


def search(item):
    user_data = {}
    r = requests.get(get_search_url(item))
    tree = html.fromstring(r.content)
    for el in tree.xpath('//article'):
        a_el = el.xpath('.//a')
        if len(a_el) == 2:
            title = a_el[1].text_content()
            link = a_el[1].get('href')
            image = a_el[0].xpath('.//img')[0].get('data-src')
            seller = get_seller(link)
            if seller in user_data:
                if item in user_data[seller]:
                    user_data[seller][item].append(get_item_dict(title, link, image))
                else:
                    user_data[seller][item] = [get_item_dict(title, link, image)]
            else:
                user_data[seller] = { item: [get_item_dict(title, link, image)]}
    return user_data


            # req = requests.get(get_seller_search_url(get_seller(link), "kabel 3"))
            # tree = html.fromstring(req.content)
            # for el in tree.xpath('//article'):
            #     a_el = el.xpath('.//a')
            #     if len(a_el) == 2:
            #         title = a_el[1].text_content()
            #         link = a_el[1].get('href')
            #         image = a_el[0].xpath('.//img')[0].get('data-src')
            #         print("    %s" % title)

def get_item_dict(title, link, image):
    return {
        "title": title,
        "link": link,
        "image": image
    }


def get_search_url(item):
    return replace_url_spaces('https://allegro.pl/listing?string=%s' % item)


def get_seller_search_url(seller, item):
    return replace_url_spaces('https://allegro.pl/uzytkownik/%s?string=%s' % (seller, item))


def replace_url_spaces(url):
    return url.replace(" ", "%20")

print(search("gniazdo szyna din"))
# r = requests.get(get_seller_search_url("enedtil", "kabel"))
# tree = html.fromstring(r.content)
# for el in tree.xpath('//article'):
#     a_el = el.xpath('.//a')
#     if len(a_el) == 2:
#         title = a_el[1].text_content()
#         link = a_el[1].get('href')
#         image = a_el[0].xpath('.//img')[0].get('data-src')
#         print("%s" % title)