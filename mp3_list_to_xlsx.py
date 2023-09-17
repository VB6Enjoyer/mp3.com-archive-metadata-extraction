from extract_urls import extract_urls
import requests, re, xlsxwriter
from bs4 import BeautifulSoup

def extract_metadata(url, genre_filter=""):
    response = requests.get(url); # Send a GET request to the URL
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}");
        return None;
    
    soup = BeautifulSoup(response.content, 'html.parser'); # Parse the HTML content using BeautifulSoup

    # Regex patterns to find metadata stored in strings
    pattern_genre = re.compile(r"^More featured tracks in .*");
    pattern_location = re.compile(r"^Find more artists in .*");

    name_td = soup.find('td', class_='ttlbarttl');  # Find the artist's name
    location_td = soup.find('a', string=pattern_location); # Find the artist's location
    genre_td = soup.find('a', string=pattern_genre); # Find the artist's main genre
    trackgenres_td = soup.find_all('td', class_='small'); # Find the genre for each track
    
    genre_strings = [];
    
    # Obtain the genre for each track and put it in a list
    for td in trackgenres_td:
        a_tags = td.find_all('a');
        
        for a_tag in a_tags:
            genre_strings.append(a_tag.string);
            
    name = ' '.join(name_td.stripped_strings) if name_td else None; # Extract the artist's name, ignoring all other info stored within the <td> tag
    location = location_td.string[21:len(location_td.string)] if location_td else None; # Extract the artist's location
    genre = genre_td.string[24:len(genre_td.string)] if genre_td else None; # Extract the genre
    artist_url = url;
    
    # Only save artists that 
    if((genre_filter.lower() in genre.lower()) or
       (genre_filter.lower() in genre_strings[0].lower() if len(genre_strings) > 0 else False) or 
       (genre_filter.lower() in genre_strings[1].lower() if len(genre_strings) > 1 else False) or
       (genre_filter.lower() in genre_strings[2].lower() if len(genre_strings) > 2 else False)):
        
        # Separate the city and the country of the artist into two different variables
        parts = location.split(" - ");
        
        if len(parts) == 2: # Normally, parts should have two elements
            city = parts[0].strip();
            country = parts[1].strip();
            
            if city[-1] == ",":
                city = city[:-1];
        else: # However, some locations such as "Canada - Israel - Sweden" are different
            city, country = "N/A", location;    

        return [name, country, city, genre, genre_strings, artist_url];
    
def data_to_xlsx():
    # Create an Excel workbook, and within it, a worksheet.
    workbook = xlsxwriter.Workbook("artists.xlsx");
    worksheet = workbook.add_worksheet();
    i = 1;
    
    url = input("Input the URL: ");
    genre = input("Input a genre (leave blank to parse artists of all genres): ");
    
    print("Extracting URLs...");
    urls = extract_urls(url, True);
    print(str(len(urls)) + " URLs successfully extracted and parsed!");
    print("Parsing and saving metadata to xlsx...");
    
    for artist in urls:
        metadata = extract_metadata(artist, genre);
        
        if metadata:
            worksheet.write("A" + str(i), metadata[0].strip()); # Write the name
            worksheet.write("B" + str(i), metadata[1].strip()); # Write the country
            worksheet.write("C" + str(i), metadata[2].strip()); # Write the city
            worksheet.write("D" + str(i), metadata[3].strip()); # Write main genre
            worksheet.write("E" + str(i), metadata[4][0].strip()) if len(metadata[4]) > 0 else "N/A"; # Write the first track's genre
            worksheet.write("F" + str(i), metadata[4][1].strip()) if len(metadata[4]) > 1 else "N/A"; # Write the second track's genre
            worksheet.write("G" + str(i), metadata[4][2].strip()) if len(metadata[4]) > 2 else "N/A"; # Write thes third track's genre
            worksheet.write("H" + str(i), metadata[5].strip()); # Write the URL
            
            print("Artist '" + metadata[0].strip() + "' parsed and saved.");
            i += 1;

    print("Created a file with", i, "entries");
    workbook.close();
            
if __name__ == "__main__":
    data_to_xlsx();
