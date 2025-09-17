"""This module contains url extracting functions and related utilities"""

import urllib
import re
import validators

from ptlibs import tldparser

def find_urls_in_file(file_content: str) -> list:
    """Return list of possible links in provided <file_content>."""
    re_abs_urls   = r'(http:\/\/|ftp:\/\/|https:\/\/)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])' #(https?:\/\/|ftps?:\/\/)(www\.)?([\w\.]*\.[a-zA-Z]{2,3})(([\w\.\/?=&])*?(?=http))
    re_rel_links  = r"^(?<!<)(\.{1,2}\/?|\/\/|\/)(([\w.]{2,})(\/)?)+$"
    re_html_links = r'(href=|src=)[\'\"](.*)[\'\"]'

    result  = re.findall(re_abs_urls, file_content)
    result += re.findall(re_html_links, file_content)
    result += re.findall(re_rel_links, file_content)

    return sorted(set(''.join(i) if type(i) == tuple else i for i in result))


def get_subdomains_from_list(urls: list) -> list:
    """Return unique list of subdomains from provided <urls>"""
    subdomains = set()
    for url in urls:
        if validators.url(url):
            domain = url2domain(url, with_protocol=False)
        elif validators.domain(url):
            domain = url
        else:
            continue
        subdomains.add(domain)
    return sorted(subdomains)


def find_abs_urls(string: str) -> list:
    """Returns list of absolute urls in <string>"""
    re_abs_url = r'(https?|ftps?)(://[\w\.]*\.[a-zA-Z]{2,3}[?&/#]*[^"\'><\s]*)'
    return sorted(set(''.join(url) for url in re.findall(re_abs_url, string)))


def find_urls_in_response(page_content: str, re_pattern: str, url: str, type_urls: str, without_parameters=None, abs_urls=[]) -> list:
    """Find urls in <page_content> based by applied <re_pattern>"""
    result = []
    domain = url2domain(url)
    all_urls = list({result[1] for result in re.findall(re_pattern, page_content)}) + abs_urls
    for found_url in all_urls:
        if re.match(r'\w*://', found_url) and not re.match(r'https?', found_url):
            continue
        if found_url.startswith("//"):
            all_urls.append(url.split("://")[0] + ":" + found_url)
            continue

        abs_url = rel2abs(found_url, domain)
        parsed_url = urllib.parse.urlparse(abs_url)
        if without_parameters:
            abs_url = urllib.parse.urlunsplit((parsed_url[0], parsed_url[1], parsed_url[2], "", ""))
        if type_urls == "external" and (url2domain(abs_url, False, False) != url2domain(url, False, False)):
            result.append(abs_url)
        if (type_urls == "subdomain") and (url2domain(abs_url, False, False) == url2domain(url, False, False)):
            result.append(parsed_url.netloc)
        if type_urls == "internal" and (url2domain(abs_url, True, False) == url2domain(url, True, False)):
            result.append(abs_url)
    return sorted(list(set(result)), key=str.lower)


def url2domain(url, with_subdomains=True, with_protocol=True) -> str:
    """Returns domain from provided url"""
    parsed_url = tldparser.parse(url)
    protocol = parsed_url.scheme + "://" if with_protocol else ""

    if parsed_url.subdomain:
        parsed_url.subdomain += "."

    if with_subdomains:
        if not parsed_url.suffix: # e.g. ip address
            return protocol + parsed_url.subdomain + parsed_url.domain
        else:
            return protocol + parsed_url.subdomain + parsed_url.domain + "." + parsed_url.suffix
    else:
        return protocol + parsed_url.domain + "." + parsed_url.suffix


def rel2abs(url, domain):
    if not domain.endswith("/") and not url.startswith("/"):
        domain += "/"
    if url.startswith("http://") | url.startswith("https://") | url.startswith("ftp://") | url.startswith("ftps://") | url.startswith("irc://"):
        return url
    else:
        return domain + url


def _find_internal_parameters(internal_urls, group_parameters):
    parsed_urls = []
    for url in internal_urls:
        o = urllib.parse.urlsplit(url)
        if o.query:
            query_list = o.query.split("&")
            parsed_url = urllib.parse.urlunsplit((o[0], o[1], o[2], "", ""))
            result_data = {"url": parsed_url, "parameters": query_list}
            if not group_parameters:
                parsed_urls.append(result_data)
            else:
                if not parsed_urls:
                    parsed_urls.append(result_data)
                    continue
                found = False
                for d in parsed_urls:
                    if parsed_url == d["url"]:
                        d["parameters"].extend(query_list)
                        found = True
                if not found:
                    parsed_urls.append(result_data)
    return parsed_urls