import webbrowser
import random
from tkinter import Tk, Button, Frame, Label, StringVar, Toplevel
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')

# Initialize the Chrome WebDriver with options
driver = webdriver.Chrome(options=chrome_options)

# Function to open a URL in the web browser
def open_url(url):
    webbrowser.open(url)

# Function to fetch ESPN headlines
def fetch_espn_headlines():
    driver.get('https://www.espn.com/')
    wait = WebDriverWait(driver, 10)
    headline_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-mptype="headline"]')
    visible_headlines = [(link.text.strip(), link.get_attribute('href')) 
                         for link in headline_links if link.text.strip() and link.get_attribute('href')]
    return visible_headlines[:10]  # Limit to 10 headlines

# Function to fetch specific Investing.com links
def fetch_investing_headlines():
    driver.get('https://www.investing.com/')
    wait = WebDriverWait(driver, 10)
    
    # Type 1 links (general finance headlines)
    type_1_links = driver.find_elements(By.CSS_SELECTOR, 'a.line-clamp-3.text-base.font-semibold.leading-7.hover\\:underline.sm\\:line-clamp-2.md\\:line-clamp-3.md\\:leading-6')
    
    # Type 2 links (small-cap stocks analysis)
    type_2_links = driver.find_elements(By.CSS_SELECTOR, 'a.text-inv-blue-500.hover\\:text-inv-blue-500.hover\\:underline.focus\\:text-inv-blue-500.focus\\:underline.mb-2.text-base\\/\\[28px\\].font-semibold.\\!text-warren-gray-900')

    # Collect text and limit the number of results for each type
    visible_headlines = []
    
    # Combine type 1 and type 2 links
    for link in type_1_links + type_2_links:
        if link.text.strip():
            visible_headlines.append((link.text.strip(), link.get_attribute('href')))

    return visible_headlines[:10]  # Limit to 10 combined headlines

def fetch_bbc_headlines():
    driver.get('https://www.bbc.com/')
    wait = WebDriverWait(driver, 10)
    headline_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/news/"], a[href*="bbc.com/news/"]')
    
    visible_headlines = []
    for link in headline_links:
        href = link.get_attribute('href')
        # If href starts with "https", it is already a full URL
        if href.startswith("https"):
            url = href
        else:
            url = f"https://www.bbc.com{href}"
        
        if link.text.strip() and url:
            visible_headlines.append((link.text.strip(), url))
    
    return visible_headlines[:6]  # Limit to 6 headlines for Politics


# Function to fetch Health.com headlines
def fetch_health_headlines():
    driver.get('https://www.health.com/')
    wait = WebDriverWait(driver, 10)
    headline_links = driver.find_elements(By.CSS_SELECTOR, 'a.mntl-card-list-items')  # Updated selector for health links
    visible_headlines = []
    
    for link in headline_links:
        headline_text = link.find_element(By.CSS_SELECTOR, '.card__title-text').text.strip()
        url = link.get_attribute('href')
        if headline_text and url:
            visible_headlines.append((headline_text, url))
    
    return visible_headlines[:10]  # Limit to 10 headlines


# Function to dynamically fetch headlines based on category
def fetch_and_assign_details(source):
    headlines = []
    if source == "ESPN":
        headlines = fetch_espn_headlines()
    elif source == "Investing":
        headlines = fetch_investing_headlines()
    elif source == "Politics":
        headlines = fetch_bbc_headlines()
    elif source == "Health":
        headlines = fetch_health_headlines()
    
    return assign_random_views_and_sort(headlines)

# Function to update the display of headlines
def display_headlines(headlines, root, frame, category_name):
    for widget in frame.winfo_children():
        widget.destroy()

    current_datetime = datetime.now().strftime("%m.%d.%Y %I:%M %p")
    title_label = Label(frame, text=f"Latest {category_name} Headlines - {current_datetime}", 
                        font=("Helvetica", 18, "bold"), fg="white", bg="#2C3E50")  # Dark brown background
    title_label.pack(pady=10)

    sort_by_views_button = Button(frame, text="Sort by Views", command=lambda: sort_and_display(headlines, 'views', root, frame), 
                                  bg="#1ABC9C", fg="white", font=("Arial", 10, "bold"))  # Light salmon color
    sort_by_views_button.pack(pady=5)

    sort_by_rating_button = Button(frame, text="Sort by Rating", command=lambda: sort_and_display(headlines, 'rating', root, frame), 
                                   bg="#1ABC9C", fg="white", font=("Arial", 10, "bold"))  # Light salmon color
    sort_by_rating_button.pack(pady=5)

    refresh_button = Button(frame, text="Refresh", command=lambda: refresh_headlines(root, frame), 
                            bg="#E74C3C", fg="white", font=("Arial", 10, "bold"))  # Red color
    refresh_button.pack(pady=5)

    for index, (headline, url, views, rating, stars, rng_number) in enumerate(headlines, start=1):
        formatted_views = f"{views:,}"
        headline_text = f"#{index} ({formatted_views} views, Rating: {stars} ({rng_number})): {headline}"
        headline_button = Button(frame, text=headline_text,
                                 fg="white", bg="#1ABC9C", cursor="hand2", font=("Arial", 10, "bold"),
                                 activebackground="#16A085", activeforeground="white",  # Tomato color for active button
                                 bd=0,  
                                 command=lambda url=url: open_url(url))
        headline_button.pack(anchor="w", pady=5, padx=5, fill="x")

# Function to sort headlines based on views or rating and display them
def sort_and_display(headlines, sort_by, root, frame):
    if sort_by == 'views':
        sorted_headlines = sorted(headlines, key=lambda x: x[2], reverse=True)
    elif sort_by == 'rating':
        sorted_headlines = sorted(headlines, key=lambda x: x[3], reverse=True)
    display_headlines(sorted_headlines, root, frame, selected_source.get())

# Function to convert a rating into a star representation
def generate_star_rating(rating):
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return '★' * full_stars + '½' * half_star + '☆' * empty_stars

# Function to assign random views, ratings, and sort headlines
def assign_random_views_and_sort(headlines):
    headlines_with_details = []
    for headline, url in headlines:
        views = random.randint(1000000, 10000000)
        rating = round(random.uniform(0.5, 5.0), 1)
        stars = generate_star_rating(rating)
        rng_number = random.randint(10, 10000)
        headlines_with_details.append((headline, url, views, rating, stars, rng_number))
    return headlines_with_details

# Function to refresh headlines
def refresh_headlines(root, frame):
    source = selected_source.get()
    if source:  # Ensure source is set
        headlines_with_details = fetch_and_assign_details(source)
        display_headlines(headlines_with_details, root, frame, source)

# Function to update the display based on selected category
def update_category(source):
    selected_source.set(source)  # Update the selected source
    headlines_with_details = fetch_and_assign_details(source)
    
    # Use the selected category name in the display
    category_name = "ESPN.com" if source == "ESPN" else \
                    "Investing.com" if source == "Investing" else \
                    "BBC.com" if source == "Politics" else \
                    "Health.com"
    
    display_headlines(headlines_with_details, root, frame, category_name)

# Timer logic in a separate window
def open_timer_window():
    timer_window = Toplevel(root)
    timer_window.title("Timer")
    timer_window.configure(bg="#34495E")  # Dark brown background

    running = False
    start_time = None

    def update_clock(clock_label):
        if running:
            elapsed_time = datetime.now() - start_time
            clock_label.config(text=str(elapsed_time).split(".")[0])  # Show elapsed time without microseconds
            clock_label.after(1000, update_clock, clock_label)

    def start_timer(clock_label):
        nonlocal running, start_time
        if not running:
            running = True
            start_time = datetime.now()
            update_clock(clock_label)

    def stop_timer():
        nonlocal running
        running = False

    def reset_timer(clock_label):
        nonlocal start_time
        start_time = None
        clock_label.config(text="00:00:00")

    # Timer display
    timer_label = Label(timer_window, text="00:00:00", font=("Helvetica", 48, "bold"), fg="white", bg="#34495E")
    timer_label.pack(pady=20)

    # Buttons to control the timer
    start_button = Button(timer_window, text="Start", command=lambda: start_timer(timer_label),
                          font=("Helvetica", 16), fg="white", bg="#1ABC9C")
    start_button.pack(side="left", padx=10)

    stop_button = Button(timer_window, text="Stop", command=stop_timer,
                         font=("Helvetica", 16), fg="white", bg="#E74C3C")
    stop_button.pack(side="left", padx=10)

    reset_button = Button(timer_window, text="Reset", command=lambda: reset_timer(timer_label),
                          font=("Helvetica", 16), fg="white", bg="#1ABC9C")
    reset_button.pack(side="left", padx=10)

# Create the main window
root = Tk()
root.title("Headlines and Timer")
root.configure(bg="#2C3E50")  # Dark brown background

# Create a variable to hold the selected source
selected_source = StringVar(root)

# Create a frame for category selection
category_frame = Frame(root, bg="#2C3E50")  # Dark brown background
category_frame.pack(padx=10, pady=10)

# Add a label for the category selection
category_label = Label(category_frame, text="Category:", font=("Helvetica", 16), fg="white", bg="#2C3E50")  # Dark brown background
category_label.grid(row=0, column=0, padx=5)

# Add buttons for selecting categories
categories = [("Sports", "ESPN"), ("Finance", "Investing"), ("Politics", "Politics"), ("Health", "Health")]
for index, (text, source) in enumerate(categories):
    category_button = Button(category_frame, text=text, font=("Helvetica", 14), fg="white", bg="#1ABC9C", 
                             command=lambda source=source: update_category(source))
    category_button.grid(row=0, column=index+1, padx=5)

# Create a button to open the timer window
timer_button = Button(category_frame, text="Open Timer", font=("Helvetica", 14), fg="white", bg="#1ABC9C",
                      command=open_timer_window)
timer_button.grid(row=0, column=len(categories) + 1, padx=5)

# Create a frame for displaying headlines
frame = Frame(root, bg="#34495E")  # Dark brown background
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Add a placeholder label instructing the user to select a category
placeholder_label = Label(frame, text="Please select a category to view headlines.", 
                          font=("Helvetica", 18, "bold"), fg="white", bg="#2C3E50")
placeholder_label.pack(pady=20)

# Start the main event loop
root.mainloop()

# Quit the driver after closing the application
driver.quit()
