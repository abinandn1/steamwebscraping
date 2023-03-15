# Import modules needed for program
import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st
from PIL import Image #needed to display images

def image_creation():
    image = Image.open('steam_picture.jpg')
    st.image(image) # Display image

def scrape_genres():
    # Scrape all genres from Steam, so user can choose between genres
    tags_url = 'https://store.steampowered.com/tag/browse/#global_492'
    tags_response = requests.get(tags_url)
    genre_soup = BeautifulSoup(tags_response.content, 'html.parser') 

    genres = []
    genre_list = genre_soup.find_all('div', {'class': 'tag_browse_tag'})  # get all steam genre tags
    for genre in genre_list:
        genres.append(genre.text.strip()) # remove whitespace 

    return genres
    

def scrape_top_sellers(selected_genre):
    # Scrape the top selling Steam Games page 
    topsellers_url = 'https://store.steampowered.com/search/?filter=topsellers'
    topsellers_response = requests.get(topsellers_url)
    topsellers_soup = BeautifulSoup(topsellers_response.content, 'html.parser')
    # Find genre tags from all games on top selling page
    game_links = topsellers_soup.find_all("a", {"class": "search_result_row"}) # fully expands all games, all games have the search_result_row class 
    game_data = []
    for game in game_links:
        game_url = game["href"] # get the game URL link (game store page)
        game_response = requests.get(game_url) # use the store page to access the tags of each game, since tags are not viewable on top sellers page 
        game_soup = BeautifulSoup(game_response.content, "html.parser")
        
        # get all genre tags from the game's store page
        genre_tags = game_soup.find_all("a", {"class": "app_tag"})
        # strip extra space away from all tags, and seperate them 
        genre_list = [genre_tag.text.strip() for genre_tag in genre_tags]
        
        # check if the user selected genre matches any of the game's genres
        if selected_genre in genre_list: # if matches, add to list to be displayed 
            title = game.find('span', {'class': 'title'}).text # convert to readable text
            price = game.find('div', {'class': 'col search_price_discount_combined responsive_secondrow'}).text.strip()
            game_data.append({'Title': title, 'Price': price, 'Link': game_url})
    return game_data

def main():
    # Create header image, and get data needed for program
    image_creation()
    genres = scrape_genres()
     # Allow for user input/scrolling to find specific genre they are looking for
    selected_genre = st.selectbox("Select (or type) a genre", genres) ## Bug: Starts and loads data on Indie by default
    game_data = scrape_top_sellers(selected_genre) 
    # Use pandas and Streamlit to display the dictionaries as a table/rows, displaying the game name, price, url
    table = pd.DataFrame(game_data)
    st.title(f'Top Selling {selected_genre.capitalize()} Games')
    st.table(table[['Title', 'Price', 'Link']])

main()