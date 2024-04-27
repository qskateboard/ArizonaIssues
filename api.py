#
# Created by pSkateboard (Lee_Dohyeon)
#

import re
import requests
import bs4
import lxml

headers = {}
session = requests.session()


def setup(user_agent, cookie):
    global headers
    headers = {
        "user-agent": user_agent,
        "cookie": cookie
    }
    session.headers = headers


def get_categories(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    result = []
    for category in soup.find_all('div', re.compile('.*node--depth2 node--forum.*')):
        result.append({
            "name": category.find("a").text,
            "link": "https://forum.arizona-rp.com" + category.find("a")['href'],
        })
    return result


def get_category(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    return soup.find("h1", re.compile("p-title-value")).text


def get_threads(url, page=1):
    if page > 1:
        if url[-1] == "/":
            url = url + "page-" + str(page)
        else:
            url = url + "/page-" + str(page)
    r = session.get(url)

    soup = bs4.BeautifulSoup(r.text, "lxml")
    result = []
    for thread in soup.find_all('div', re.compile('structItem structItem--thread.*')):
        link = object
        unread = False
        closed = False
        pinned = False
        title_element = thread.find_all('div', "structItem-title")[0]
        for el in title_element.find_all("a"):
            if "threads" in el['href']:
                link = el

        if "structItem-status structItem-status--locked" in str(thread):
            closed = True
        if "structItem-status structItem-status--sticky" in str(thread):
            pinned = True
        if "unread" in link['href']:
            unread = True

        creator = thread.find('a').text
        try:
            creator = thread.find('img')['alt']
        except:
            pass
        try:
            creator = creator.replace("\n", "")
            if len(creator) < 2:
                creator = thread.find_all("a", {"data-xf-init": "member-tooltip"})[1].text
        except:
            pass

        seo = thread.find_all("div", {"class": "structItem-cell structItem-cell--meta"})

        result.append({
            "title": link.text,
            "link": "https://forum.arizona-rp.com" + link['href'].replace("unread", ""),
            "creator": creator,
            "latest": thread.find('div', re.compile('structItem-cell structItem-cell--latest')).find_all("a")[
                1].text,
            "closed_date": thread.find('time', re.compile('structItem-latestDate u-dt'))['data-time'],
            "unread": unread,
            "pinned": pinned,
            "closed": closed,
            "views": seo[1].text,
            "replies": seo[0].text
        })
    return result


def get_post(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    post_id = str(int(url.split("post-")[1]))

    message = soup.find_all("article", {"id": "js-post-" + post_id})[0]

    q = session.get(f"https://forum.arizona-rp.com/posts/{post_id}/edit")
    soup2 = bs4.BeautifulSoup(q.text, "lxml")
    result = {
        "post_id": post_id,
        "author": message['data-author'],
        "timestamp": message.find("time", "u-dt")['data-time'],
        "content": soup2.find("textarea", {"name": "message"}).text,
        "content_html": soup2.find("textarea", {"name": "message_html"}).text,
    }
    return result


def edit_post(uid, html):
    r = session.get(f"https://forum.arizona-rp.com/posts/{uid}/edit")
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[0]
    body = {
        "message_html": html,
        "message": html,
        "_xfToken": token,
    }
    session.post(f"https://forum.arizona-rp.com/posts/{uid}/edit", body)


def get_thread(url):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")

    title = soup.find("h1", re.compile("p-title-value"))
    for span in title.findAll('span'):
        span.replace_with('')

    post = soup.find_all('article', re.compile('message message--post.*is-first'))[0]
    post_id = post['data-content']
    return [title.text, post.find("div", "bbWrapper").text, post_id]


def edit_thread(uid, prefix, opn=1, sticky=1):
    title = get_thread(uid)[0]
    uid = uid.split("https://forum.arizona-rp.com/threads/")[1].replace("/", "")
    r = session.get(f"https://forum.arizona-rp.com/threads/{uid}/edit")
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[0]
    body = {
        "prefix_id": prefix,
        "discussion_open": opn,
        "_xfSet[discussion_open]": opn,
        "_xfSet[sticky]": sticky,
        "sticky": sticky,
        "_xfToken": token,
        "_xfRequestUri": f"/threads/{uid}/edit",
        "_xfResponseType": "json",
        "_xfWithData": "1",
        "title": title
    }
    r = session.post(f"https://forum.arizona-rp.com/threads/{uid}/edit", data=body)


def warn_post(uid, warn_id):
    uid = uid.split("post-")[1].replace("/", "")
    r = session.get(f"https://forum.arizona-rp.com/posts/{uid}/warn")
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[0]
    body = {
        "warning_definition_id": warn_id,
        "note": "",
        "content_action": "",
        "filled_warning_definition_id": warn_id,
        "_xfToken": token,
        "_xfRequestUri": f"/threads/{uid}/edit",
        "_xfResponseType": "json",
        "_xfWithData": "1",
    }
    r = session.post(f"https://forum.arizona-rp.com/posts/{uid}/warn", data=body)


def set_unread(url):
    form = session.get(url)
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(form.text)[0]
    session.post(url, data={"_xfToken": token})


def send_message(url, message):
    r = session.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    form = soup.find_all("form")[6]

    action = "https://forum.arizona-rp.com" + form['action']
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[0]
    json = {
        "message": message,
        "_xfToken": token,
        "last_date": form.find_all("input", {"name": "last_date"})[0]['value'],
        "last_known_date": form.find_all("input", {"name": "last_known_date"})[0]['value'],
    }
    session.post(action, data=json)


def close_thread(url):
    form = session.get(url)
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(form.text)[1]
    query = {
        "_xfRequestUri": str(url).replace("https://forum.arizona-rp.com", ""),
        "_xfWithData": 1,
        "_xfToken": token,
        "_xfResponseType": "json",
    }
    r = session.post(url + "quick-close", data=query)


def pin_thread(url):
    form = session.get(url)
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(form.text)[1]
    query = {
        "_xfRequestUri": str(url).replace("https://forum.arizona-rp.com", ""),
        "_xfWithData": 1,
        "_xfToken": token,
        "_xfResponseType": "json",
    }
    r = session.post(url + "quick-stick", data=query)


def make_reaction(link, uid):
    reacted = False
    if "post-" in link:
        link = link.split("post-")[1].replace("/", "")
        try:
            uri = "https://forum.arizona-rp.com/posts/{}/react".format(link)
            q = session.get("https://forum.arizona-rp.com/posts/" + link + "/react?reaction_id=" + str(uid))
            if "Вы действительно хотите оставить эту реакцию?" in q.text:
                token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(q.text)[0]
                session.post(uri, data={"reaction_id": uid, "_xfToken": token})
                reacted = True
        except:
            print("[-] Произошла ошибка при установке реакции")
    else:
        if "https://forum.arizona-rp.com/threads/" in link:
            try:
                q = session.get(link)
                soup = bs4.BeautifulSoup(q.text, "lxml")
                for post in soup.findAll('article', {'class': 'message'}):
                    hrefs = post.findAll('a')
                    for a in hrefs:
                        if "/post-" in a['href']:
                            number = a['href'].split("post-")[1].replace("/", "")
                            uri = "https://forum.arizona-rp.com/posts/{}/react".format(str(number))
                            q = session.get(
                                "https://forum.arizona-rp.com/posts/" + number + "/react?reaction_id=" + str(uid))
                            if "Вы действительно хотите оставить эту реакцию?" in q.text:
                                token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(q.text)[0]
                                session.post(uri, data={"reaction_id": uid, "_xfToken": token})
                                reacted = True
                            break
                        if reacted:
                            break
                    if reacted:
                        break
            except:
                print("[-] Произошла ошибка при установке реакции")
    return reacted


def delete_post(uid):
    r = session.get(f"https://forum.arizona-rp.com/posts/{uid}/delete")
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[0]
    body = {
        "reason": "",
        "hard_delete": 0,
        "_xfToken": token,
    }
    session.post(f"https://forum.arizona-rp.com/posts/{uid}/delete", body)


def search_posts(keyword, pages=1):
    r = session.get(f"https://forum.arizona-rp.com/search/")
    token = re.compile("name=\"_xfToken\" value=\"(.*)\" />").findall(r.text)[0]
    body = {
        "keywords": keyword,
        "order": "date",
        "_xfRequestUri": "/search/",
        "_xfWithData": "1",
        "_xfResponseType": "json",
        "_xfToken": token,
    }
    r = session.post(f"https://forum.arizona-rp.com/search/search", body)
    r = session.get(r.json()['redirect'])
    soup = bs4.BeautifulSoup(r.text, "lxml")

    posts = []
    for post in soup.find_all("li", "block-row block-row--separated js-inlineModContainer"):
        post = {
            "title": post.find("h3", "contentRow-title").text.replace("\n", ""),
            "link": "https://forum.arizona-rp.com" + post.find("h3", "contentRow-title").a['href'],
            "when": post.find("ul", "listInline listInline--bullet").find_all("li")[2].text.replace("\n", ""),
            "author": post.find("ul", "listInline listInline--bullet").find_all("li")[0].text.replace("\n", ""),
            "category": post.find("ul", "listInline listInline--bullet").find_all("li")[3].text.replace("\n", ""),
        }
        posts.append(post)
    return posts
