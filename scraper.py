import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome WebDriver
options = Options()
options.add_argument("--headless")  # Optional: Run in headless mode (no UI)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Main URL
main_url = "https://www.tradingview.com/markets/futures/quotes-all/"

def click_load_more_until_complete():
    """Click on the 'Load More' button until it is no longer visible."""
    driver.get(main_url)
    time.sleep(5)  # Wait for the page to load initially
    
    while True:
        try:
            # Wait for the 'Load More' button to be clickable
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='content-D4RPB3ZC' and contains(text(), 'Load More')]"))
            )
            
            # Scroll the page to ensure the button is in view
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            time.sleep(2)  # Wait a little bit for smooth scrolling
            
            # Use JavaScript to click the 'Load More' button
            driver.execute_script("arguments[0].click();", load_more_button)
            print("Clicked 'Load More' button.")
            
            # Wait for the page to load (adjust the sleep time as needed)
            time.sleep(5)

            # Check if the 'Load More' button is still visible
            try:
                load_more_button = driver.find_element(By.XPATH, "//span[@class='content-D4RPB3ZC' and contains(text(), 'Load More')]")
                print("'Load More' button is still visible, continuing to click...")
            except Exception:
                # If the 'Load More' button is no longer visible, break the loop (task is complete)
                print("No more 'Load More' button found. All data loaded.")
                break
        except Exception as e:
            print(f"Error occurred while clicking 'Load More': {e}")
            break

def fetch_currency_and_price():
    """Fetch currency name and current price."""
    rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'row-RdUXZpkv listRow')]")
    data = []
    for row in rows:
        try:
            currency_name_element = row.find_element(By.XPATH, ".//sup[@class='apply-common-tooltip tickerDescription-GrtoTeat']")
            price_element = row.find_element(By.XPATH, ".//td[contains(@class, 'cell-RLhfr_y4 right-RLhfr_y4')]")
            currency_name = currency_name_element.text
            price = price_element.text.replace(",", "")  # Remove commas for consistency
            data.append((currency_name, price))
        except Exception as e:
            print(f"Error extracting data from row: {e}")
    return data

def save_prices_to_file(data):
    """
    Save the extracted currency names and prices to a text file, 
    clearing the old data and replacing it with new data.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open("futures_prices.txt", "w", encoding="utf-8") as file:
            # Write the header
            file.write(f"Updated at: {timestamp}\n")
            file.write("Currency | Current Price\n")
            file.write("-" * 40 + "\n")
            
            # Write the data
            for currency, price in data:
                file.write(f"{currency} | {price}\n")
            
            # Add a newline for readability
            file.write("\n")
        print(f"Data successfully written to 'futures_prices.txt' at {timestamp}.")
    except Exception as e:
        print(f"Error writing to file: {e}")


def update_prices():
    """Update and save the live currency prices every minute with a countdown."""
    while True:
        print("Fetching currency names and current prices...")
        currency_data = fetch_currency_and_price()
        
        # Save the data to a file (will overwrite the file each time)
        save_prices_to_file(currency_data)
        
        # Show the number of data items extracted
        print(f"{len(currency_data)} currencies extracted and saved.")
        
        # Countdown for 60 seconds
        print("Starting 60-second countdown before the next update...")
        for remaining in range(60, 0, -1):
            print(f"Next update in: {remaining} seconds", end="\r")
            time.sleep(1)
        print()  # Move to the next line after the countdown


def main():
    try:
        print("Starting to load all data (clicking 'Load More' until complete)...")
        click_load_more_until_complete()
        
        print("Starting to fetch and update prices every minute...")
        update_prices()

    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
