import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def debug_html(soup):
    """Debug HTML structure"""
    print("\n=== HTML Structure ===")
    print(soup.prettify())
    print("\n=== Available Classes ===")
    for element in soup.find_all(class_=True):
        print(f"Element: {element.name}, Classes: {element.get('class')}")

def scrape_jobs():
    try:
        url = 'https://vacancymail.co.zw/jobs/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Send HTTP request
        response = requests.get(url, headers=headers)

        # Debug response
        print(f"\n=== Response Status ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Optional: debug HTML structure
            # debug_html(soup)

            job_listings = soup.find_all('a', class_='job-listing')
            print(f"\n=== Found {len(job_listings)} job listings ===")

            jobs_data = []
            for i, job in enumerate(job_listings[:10], 1):
                try:
                    print(f"\n=== Processing Job {i} ===")
                    
                    title_element = job.find('h3', class_='job-listing-title')
                    print(f"Title element found: {title_element is not None}")
                    
                    title = title_element.text.strip() if title_element else "No title found"
                    company = job.find('h4', class_='job-listing-company').text.strip() if job.find('h4', class_='job-listing-company') else "No company found"
                    description = job.find('p', class_='job-listing-text').text.strip() if job.find('p', class_='job-listing-text') else "No description found"

                    footer_div = job.find('div', class_='job-listing-footer')
                    print(f"Footer div found: {footer_div is not None}")

                    if footer_div:
                        footer_items = footer_div.find_all('li')
                        print(f"Footer items count: {len(footer_items)}")
                        if len(footer_items) >= 2:
                            location = footer_items[0].text.strip()
                            expiry = footer_items[1].text.replace("Expires", "").strip()
                        else:
                            location = "Unknown location"
                            expiry = "Unknown expiry"
                    else:
                        location = "Unknown location"
                        expiry = "Unknown expiry"

                    jobs_data.append({
                        'Job Title': title,
                        'Company': company,
                        'Location': location,
                        'Expiry Date': expiry,
                        'Job Description': description
                    })

                    logging.info(f"Successfully scraped job: {title}")
                except Exception as e:
                    logging.error(f"Error scraping job: {str(e)}")
                    continue

            # Save to CSV
            df = pd.DataFrame(jobs_data)
            df.to_csv('scraped_jobs.csv', index=False, encoding='utf-8')
            logging.info("✅ scraped_jobs.csv has been created!")
        else:
            logging.error(f"❌ Failed to fetch the page. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")

# Schedule the job to run every hour
schedule.every(1).hours.do(scrape_jobs)

# Initial run before scheduling
scrape_jobs()

# Run indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)
