import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def extract_urls(url, filter_artists=False):
    urls = set();  # Use a set to avoid duplicates
    
    response = requests.get(url) # Sends an HTTP GET request to the provided URL and stores the response.
    if response.status_code == 200: # If the response status code is 200 (indicating success), it creates a BeautifulSoup object to parse the HTML content.
        soup = BeautifulSoup(response.content, 'html.parser');
        
        for a_tag in soup.find_all('a', href=True): # Iterates through all `a` tags with an `href` attribute, extracting the `href` values.
            href = a_tag['href'];
            full_url = urljoin(url, href); # Join the URL if it's a relative link
            
            if filter_artists:
                # Regex pattern for artist pages URLs only
                pattern = r"http://mp3-2003\.computer-legacy\.com/artists/\d+/.+\.html"
                
                if re.match(pattern, full_url): # Checks if the URL matches the specified pattern using regex.
                    urls.add(full_url);
            else:
                urls.add(full_url);
    return list(urls);

#if __name__ == "__main__":
    # Replace this with the URL of the website you want to scrape
    #website_url = "http://mp3-2003.computer-legacy.com/artists/browse-09.html"
    #extracted_urls = extract_urls(website_url, True);
    #print("Extracted URLs:");
    #for url in extracted_urls:
    #    print(url);