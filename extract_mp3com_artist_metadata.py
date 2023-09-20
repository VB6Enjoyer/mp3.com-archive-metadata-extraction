from extract_urls import extract_urls
import requests, re, xlsxwriter, time
from bs4 import BeautifulSoup

# Regex patterns to find metadata stored in strings
pattern_genre = re.compile(r"^More featured tracks in .*");
pattern_location = re.compile(r"^Find more artists in .*");

def extract_metadata(url, genre_filter=""):
    # Separate multiple genres if inputted
    if genre_filter != "":
        genre_filter = genre_filter.split(",");
    
    response = requests.get(url); # Send a GET request to the URL
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}");
        if response.status_code == 429:
            print(f"You are being rate limited. Please try again later");
        return None;
    
    soup = BeautifulSoup(response.content, 'html.parser'); # Parse the HTML content using BeautifulSoup
    
    try:
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
        genre = genre_td.string[24:len(genre_td.string)] if genre_td else None; # Extract the artist's main genre
        
        genre_strings_set = set(genre_strings); # Turn the list into a set
        genre_strings_set.add(genre); # Appends the main genre to the genre set to check for matching genres
        
        # Find whether the artist has any genres that match with the inputted filters
        matching_genres = [filtered_genre.lower() for filtered_genre in genre_strings_set if any(filtered_genre.lower() in genre.lower() for genre in genre_filter)];
    except:
        if not name:
            print("PARSING ERROR: ARTIST IS NOT AVAILABLE.");
        else:
            print("PARSING ERROR ON ARTIST '" + name + "'.");
        matching_genres = None;

    if matching_genres or genre_filter == "":
        # Separate the city and the country of the artist into two different variables
        parts = location.split(" - ") if location else "";
        
        if len(parts) == 2: # Normally, parts should have two elements
            city = parts[0].strip();
            country = parts[1].strip();
            
            if city[-1] == ",":
                city = city[:-1];
        else: # However, some locations such as "Canada - Israel - Sweden" are different
            city = "N/A";
            country = location if location else "N/A";
            
        if len(genre_strings) == 0:
            genre_strings = ["N/A"];

        return [name, country, city, genre, genre_strings, url];
    
def data_to_xlsx():
    # Create an Excel workbook, and within it, a worksheet.
    workbook = xlsxwriter.Workbook("artists.xlsx");
    worksheet = workbook.add_worksheet();
    i = 1;
    j = 1;
    
    url = input("Input the URL: ");
    genre = input("Input any number of genres separated by commas (leave blank to parse artists of all genres): ").lower().strip();

    print("Extracting URLs...");
    urls = extract_urls(url, True);
    print(str(len(urls)) + " URLs successfully extracted and parsed!");
    print("Parsing and saving metadata to xlsx...");
    
    start = time.time();
    url_amount = str(len(urls));
    
    for artist in urls:
        metadata = extract_metadata(artist, genre);
        row = str(i);
        progress = str(j);
        
        if metadata:
            track_qty = len(metadata[4]);
            
            worksheet.write("A" + row, metadata[0].strip()); # Write the name
            worksheet.write("B" + row, metadata[1].strip()); # Write the country
            worksheet.write("C" + row, metadata[2].strip()); # Write the city
            worksheet.write("D" + row, metadata[3].strip()); # Write main genre
            worksheet.write("E" + row, metadata[4][0].strip()) if track_qty > 0 else "N/A"; # Write the first track's genre
            worksheet.write("F" + row, metadata[4][1].strip()) if track_qty > 1 else "N/A"; # Write the second track's genre
            worksheet.write("G" + row, metadata[4][2].strip()) if track_qty > 2 else "N/A"; # Write thes third track's genre
            worksheet.write("H" + row, metadata[5].strip()); # Write the URL
            
            print("Artist '" + metadata[0].strip() + "' parsed and saved.", progress + "/" + url_amount);
            i += 1;

        j += 1;

    end = time.time();
    print("Created a file with", i-1, "entries in", str(round(end - start)) + " seconds.");
    workbook.close();
            
if __name__ == "__main__":
    data_to_xlsx();