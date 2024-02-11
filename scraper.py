import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from crawler.info import Info as info

def scraper(url, resp):

    links = extract_next_links(url, resp)

    if links:
        return [link for link in links if is_valid(link)]
    else:
        return []
def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that ds used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # initializing instance of info class to keep track of data (only does this once)
    info_collection = info()
    #initializing empty list for found links
    links = []

    #if page content does not exist, return empty list
    if not resp.raw_response:
        return []

    #checks for 204 (no-content success), error codes, if url is blacklisted or already scraped -> doesn't scrape this page
    if (resp.status == 204 or resp.status >= 400) or (url in info_collection.scraped_urls) or (url in info_collection.blacklisted_urls):
        info_collection.blacklisted_urls.add(url)
        return []

    #getting links from url content
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    link_elems = soup.select("a[href]")

    for link_elem in link_elems:
        href = link_elem.get("href")
        if href:
            #converting to abs urls
            abs_url = urljoin(url, href)

            if abs_url not in info_collection.seen_urls:
                links.append(abs_url)
                info_collection.seen_urls.add(abs_url)


    #url has been fully scraped
    info_collection.scraped_urls.add(url)
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # initializing instance of info class to keep track of data (only does this once)
    info_collection = info()

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        #domain check
        if not re.match(
            r'^(\w*.)(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu)$',
            parsed.netloc):
            return False

        if "pdf" in url:
            return False

        if "#comment" in url or "#comments" in url:
            return False

        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib)$", parsed.path.lower()):
            return False

        info_collection.unique_urls.add(parsed.netloc)
        return True


    except TypeError:
        print ("TypeError for ", parsed)
        raise
