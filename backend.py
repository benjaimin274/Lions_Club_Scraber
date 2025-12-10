import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from datetime import datetime

# 179 Gewinnmöglichkeiten
# Theoretisch 2500 Kalender

def get_urls():
    """
    Gets all the urls for the winning number tables.
    First url corresponds to the current day, last url to 01.12.2025.
    """
    url = "https://lionshorbsulz.de/"
    response = requests.get(url) 
    soup = BeautifulSoup(response.text, 'html.parser')
    headers = soup.find_all('header', class_="entry-header") 
    urls = []
    for header in headers:
        a = header.find("a")  # first <a> inside the header
        if a and a.get("href"):
            urls.append(a["href"])
    relevant_urls = filter_urls(urls)
    return relevant_urls

def filter_urls(urls: list[str]):
    """
    Slices the list of urls, so that the last url is from the 01.12.2025.
    """
    start_url = "https://lionshorbsulz.de/2025/12/01/die-ersten-gewinnzahlen-2025/"
    stop_index = urls.index(start_url) + 1
    relevant_urls = urls[0: stop_index]
    return relevant_urls

# Its not always in table format (e.g. 06.12.2025)
def get_table(url):
    """
    Extracts the table of the given url.
    If there is no table, the function returns None.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_="has-fixed-layout") # only get the first table (there should be only one)
    if table is None:
        return None # -> Returns None if there is no identifiable table
    else:
        table = StringIO(str(table))
        df = pd.read_html(table)[0] # Do not use header = 0 due to inconsistent tables
        return df

def fix_table(df):
    if df is None:
        return None
    elif df.shape[1] != 3:
        return None # <-- Returns None if the shape is corrupted
    
    expected_col_names = ["Sponsor", "Gewinn", "Gewinnzahl"]
    first_row = df.iloc[0, :].values.tolist() #different syntax due to np array
    
    print(first_row)
    if first_row == expected_col_names:
        df = df.drop([0]) # drop the first row
        df.columns = expected_col_names
        df = df.reset_index(drop = True)
    else:
        df.columns = expected_col_names
    df["Gewinnzahl"] = pd.to_numeric(df["Gewinnzahl"], errors= "coerce")
    return df

def convert_to_german_date(date):
    format = '%Y/%m/%d'
    datetime_obj = datetime.strptime(date, format)
    return datetime_obj.strftime("%d.%m.%Y")

def get_date(url):
    date = url[25: 35]
    german_date = convert_to_german_date(date)
    return german_date

def title_of_article(url):
    return url[36: -2]

def gather_winning_numbers(url: str, df: pd.DataFrame, wins: dict):
    keys = list(wins.keys())
    keys.remove("Datum")
    for row, number in enumerate(df.iloc[:, 2]):
        # Ensure that no errors emerge!
        try:
            number = int(number) # <-- ensure that the numbers are int
        except:
            continue
        if number == 692 or number == 795 or number == 799:
            german_date = get_date(url)
            wins["Datum"].append(german_date)
            values = df.iloc[row, :].values
            for i, key in enumerate(keys):
                wins[key].append(values[i])

def main_current_day(relevant_urls: list[str], entry: int = 0): # <-- selected day controlable via a variable.
    failed_extractions = {}
    wins = {
        "Datum": [],
        "Sponsor": [],
        "Gewinn": [],
        "Gewinnzahl": []
    }
    url = relevant_urls[entry]
    df = get_table(url)
    df = fix_table(df)

    if df is None: # -> e.g. extraction failed
        german_date = get_date(url)
        title = title_of_article(url)
        failed_extractions["Datum"] = german_date
        failed_extractions["Titel"] = title
        failed_extractions["Url"] = url
    else:
        gather_winning_numbers(url, df, wins)
    
    if failed_extractions == {}:
        failed_extractions = None

    if wins["Datum"] != []:
        return pd.DataFrame(wins), failed_extractions
    else:
        return None, failed_extractions

def main_all_days(relevant_urls):
    failed_extractions = {
        "Datum": [],
        "Titel": [],
        "Url": [],
    }
    wins = {
        "Datum": [],
        "Sponsor": [],
        "Gewinn": [],
        "Gewinnzahl": []
    }
    for url in relevant_urls:
        df = get_table(url)
        df = fix_table(df)
        if df is not None:
            gather_winning_numbers(url, df, wins)
        else:
            german_date = get_date(url)
            title = title_of_article(url)
            failed_extractions["Datum"].append(german_date)
            failed_extractions["Titel"].append(title)
            failed_extractions["Url"].append(url)
    if failed_extractions["Datum"] == []:
        failed_extractions = None
    else:
        failed_extractions = pd.DataFrame(failed_extractions)
    if wins["Datum"] != []:
        return pd.DataFrame(wins), failed_extractions
    else:
        return None, failed_extractions

# Maybe create a class that stores and manages everything?!
# Later developement stage...

if __name__ == "__main__":
    relevant_urls = get_urls()
    main_current_day(relevant_urls)
    pass
    # Changes can be simply pushed via:
    # git push
    # It is already linked to the github repos