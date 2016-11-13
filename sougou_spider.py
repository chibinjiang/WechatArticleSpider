#coding=utf-8
import sys, time, re
import requests, urllib, traceback
import json, traceback, bs4
from datetime import datetime as dt
from urlparse import urlparse, parse_qs
from bs4 import BeautifulSoup as bs
from requests.exceptions import (
    ProxyError,
    Timeout,
    ConnectionError,
    ConnectTimeout,
)
from abuyun_proxy import gen_abuyun_proxy
reload(sys)
sys.setdefaultencoding('utf-8')

SUCCESSED = 1
FAILED = -1
PARSE_ERROR = -2
ACCESS_URL_ERROR = -3
WRITE_DB_ERROR = -4
SYNTAX_ERROR = -5
IGNORE_RECORD = -6

QUERY_URL = """http://weixin.sogou.com/weixin?oq=&query={kw}&_sug_type_=&tsn=2&sut=331&sourceid=inttime_week&ri=0&_sug_=n&type=2&interation=&ie=utf8&sst0=1478500034818&interV=kKIOkrELjboJmLkElbYTkKIKmbELjbkRmLkElbk%3D_1893302304"""

def handle_sleep(seconds):
    print "Sleeping %d seconds " % seconds, 'zZ'*10
    time.sleep(seconds)

def parse_sougou_results(keyword, num_tries=3, wait_time=10):
    """
    Given keyword, form the Sougou search url and parse the search results page
    param keywords:list of keywords
    return : {err_no: , err_msg: , data: 
        { uri: , createdate:, search_url:, }}
    """
    print "Sougou searching for ", keyword
    wx_article_urls = []
    proxy = gen_abuyun_proxy()
    err_no = SUCCESSED; err_msg = "Successed"; data = {}
    for attempt in range(1, num_tries):
        try:
            # url = QUERY_URL.format(kw=urllib.quote(keyword))
            url = QUERY_URL.format(kw=keyword)
            r =requests.get(url, proxies=proxy, timeout=wait_time)
            parser = bs(r.text, "html.parser")
            # import ipdb; ipdb.set_trace()
            for a_tag in parser.find_all("a", {
                "id": re.compile(r"sogou.*title"), 
                "href": re.compile("http://mp.weixin.qq.com*")
            }):
                # the keyword was embeded in text in red color
                wx_article_urls.append(a_tag.get("href", ""))
            data = { "createdate": dt.now().strftime("%Y-%m-%d %H:%M:%S"), 
                      "uri": url, "search_url": url, 
                      "search_keyword": keyword, "urls": wx_article_urls}
            if not wx_article_urls:
                print url, "has really no urls? Need to read it again ..."
                handle_sleep(3*attempt)
                continue
            break # success and jump out of loop
        except Timeout as e:
            # traceback.print_exc()
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), 
            handle_sleep(5*attempt)
        except ConnectionError as e:
            # traceback.print_exc()
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), 
            handle_sleep(5*attempt)
        except ProxyError as e:
            # traceback.print_exc()
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), 
            handle_proxy_error(5*attempt)
        except Exception as e:
            traceback.print_exc()
            err_no = FAILED
            err_msg = e.message
            print dt.now().strftime("%Y-%m-%d %H:%M:%S"), "Parsed topic %s Failed..." % keyword
            break  # unkown error should interrupt loop
    return {"err_no": err_no, "err_msg": err_msg, "data": data}


def test_parse_sougou_results():
    abuyun_proxy = gen_abuyun_proxy()
    list_of_kw = ["特朗普", "45任总统", "暴走大事件", "王尼玛", "阴阳师"]
    for kw in list_of_kw:
        print parse_sougou_results(kw, abuyun_proxy)
