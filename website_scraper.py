import requests
from bs4 import BeautifulSoup as bs
import os
import csv
import json

class WebsiteScraper:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def scrape_website(self):
        category = self.config.get('category', 'yoga')
        save_dir = self.config.get('save_dir', './')
        start_page = self.config.get('start_page', 1)
        end_page = self.config.get('end_page', 3)

        # Create the save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        try:
            # Initialize an empty list to store all metadata
            all_metadata = []

            # Loop through pages from start_page to end_page
            for page_num in range(start_page, end_page + 1):
                # URL of the website to scrape for each page
                url = f"https://create.vista.com/photos/{category}/?page={page_num}"

                # Make HTTP request
                response = requests.get(url)
                soup = bs(response.content, "html.parser")

                # Find all image containers
                image_containers = soup.find_all("div", {"class": "controlButtonWrapper-2fYDN assetWrapper-2LqKz descriptionWrapper-2-U-4 assetWrapper-O9SHq"})
                
                # All image URLs & descriptions storing
                image_urls = [i.img["src"] for i in image_containers]
                descriptions = [i.p.text for i in image_containers]

                # Store metadata for the current page in a list of dictionaries
                metadata = []
                for url, desc in zip(image_urls, descriptions):
                    image_name = f"{desc}.jpg"  # Use description as the image name
                    image_path = os.path.join(save_dir, image_name)

                    # Attempt to download the image
                    try:
                        image_data = requests.get(url).content
                        with open(image_path, "wb") as f:
                            f.write(image_data)

                        # If image downloaded successfully, add metadata
                        metadata.append({"image_url": url, "local_image_path": image_path, "description": desc})
                    except Exception as e:
                        print(f"Failed to save image {image_name}:", e)

                # Extend the list of all metadata with the metadata of the current page
                all_metadata.extend(metadata)

            # Write all metadata to a single CSV file
            csv_file_path = f"{category}_metadata.csv"
            with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["image_url", "local_image_path", "description"])
                writer.writeheader()
                writer.writerows(all_metadata)
            print("Data successfully saved to CSV file")

        except Exception as e:
            print("Failed to scrape the website:", e)

# Usage:
config_file = 'config.json'
scraper = WebsiteScraper(config_file)
scraper.scrape_website()
