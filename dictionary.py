import requests
from bs4 import BeautifulSoup
from googlesearch import search
import tkinter as tk
from tkinter import ttk


# Function to check if the input is a name (capitalized)
def is_name(query):
    return query[0].isupper()


# Function to search for a name meaning from Google (by searching for "<name> name meaning")
def get_name_meaning_from_google(name):
    query = f"{name} name meaning"
    search_results = search(query, num_results=5)

    for url in search_results:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text(strip=True)
                    if 'meaning' in text.lower():
                        return text.split('.')[0] + '.'
        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    return "Meaning not found from Google search results."


# Function to fetch word details from Oxford Learners Dictionary
def fetch_word_details(query):
    formatted_query = query.replace(" ", "-").lower()
    url = f"https://www.oxfordlearnersdictionaries.com/definition/english/{formatted_query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    details = {}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            definition_section = soup.find('span', {'class': 'def'})
            details['definition'] = definition_section.text.strip() if definition_section else "Not found"

            pronunciation_section = soup.find('span', {'class': 'phonetics'})
            details['pronunciation'] = pronunciation_section.text.strip() if pronunciation_section else "Not found"

            # Fetch example sentences and enforce limitations
            example_section = soup.find_all('span', {'class': 'x'})
            examples = [example.text.strip() for example in example_section]

            if len(examples) < 2:
                details['examples'] = ["Not enough examples found."]
            else:
                details['examples'] = examples[:5]  # Limit to at most 5 examples

            # Parts of Speech
            parts_of_speech_section = soup.find_all('span', {'class': 'pos'})
            pos_detected = {pos.text.lower(): True for pos in parts_of_speech_section}
            details.update(pos_detected)

            # Default False for parts of speech not found
            for part in ['adjective', 'adverb', 'verb', 'noun', 'pronoun']:
                if part not in details:
                    details[part] = False

        else:
            print(f"Error: Received status code {response.status_code}")

    except Exception as e:
        print(f"Error fetching word details: {e}")

    return details



# Function to fetch synonyms and antonyms from Datamuse API
def fetch_synonyms_antonyms(query):
    api_url = "https://api.datamuse.com/words"
    details = {}

    try:
        response = requests.get(api_url, params={'ml': query})
        if response.status_code == 200:
            synonyms = [word['word'] for word in response.json()[:5]]
            details['synonyms'] = ', '.join(synonyms) if synonyms else "Not found"
    except Exception as e:
        print(f"Error fetching synonyms: {e}")
        details['synonyms'] = "Not found"

    try:
        response = requests.get(api_url, params={'rel_ant': query})
        if response.status_code == 200:
            antonyms = [word['word'] for word in response.json()[:5]]
            details['antonyms'] = ', '.join(antonyms) if antonyms else "Not found"
    except Exception as e:
        print(f"Error fetching antonyms: {e}")
        details['antonyms'] = "Not found"

    return details


# GUI Functionality
def search_meaning():
    search_type = type_combobox.get().lower()
    search_term = search_entry.get().strip()

    if not search_type or not search_term:
        result_label.config(text="Please select a type and enter a word or name.", bg="#f8d7da", fg="#721c24")
        return

    if search_type == "word":
        details = fetch_word_details(search_term)
        extra_details = fetch_synonyms_antonyms(search_term)

        result = f"Definition: {details.get('definition', 'Not found')}\n"
        result += f"Pronunciation: {details.get('pronunciation', 'Not found')}\n"
        result += f"Synonyms: {extra_details.get('synonyms', 'Not found')}\n"
        result += f"Antonyms: {extra_details.get('antonyms', 'Not found')}\n"
        result += f"Examples:\n" + "\n".join(f"- {ex}" for ex in details.get('examples', ["Not found"])) + "\n"
        result += f"Is Adjective: {details.get('adjective', False)}\n"
        result += f"Is Adverb: {details.get('adverb', False)}\n"
        result += f"Is Verb: {details.get('verb', False)}\n"
        result += f"Is Noun: {details.get('noun', False)}\n"
        result += f"Is Pronoun: {details.get('pronoun', False)}\n"

        # Display the result with highlighted pronunciation
        result_label.config(text=result, justify="left", font=("Arial", 12), padx=10, bg="#000000", fg="#FFFFFF")

        # Highlight Pronunciation result
        if "Pronunciation" in result:
            result_label.config(text=result.replace(details.get('pronunciation', 'Not found'), f'{details.get("pronunciation", "Not found")}'), justify="left", font=("Arial", 12), padx=10, bg="#000000", fg="#FFFFFF")

    elif search_type == "name":
        name_meaning = get_name_meaning_from_google(search_term)
        if name_meaning != "Meaning not found from Google search results.":
            result_label.config(text=f"Meaning of the name '{search_term}':\n{name_meaning}", justify="left", font=("Arial", 12), bg="#000000", fg="#FFFFFF")
        else:
            result_label.config(text=f"Meaning of the name '{search_term}' not found.", justify="left", font=("Arial", 12), bg="#000000", fg="#FFFFFF")


def update_search_label(event):
    # Dynamically change the label text based on the selected search type
    selected_type = type_combobox.get().lower()
    if selected_type == "word":
        search_label.config(text="Enter Word:", bg="#d1ecf1", fg="#0c5460")
    elif selected_type == "name":
        search_label.config(text="Enter Name:", bg="#f8d7da", fg="#721c24")


# GUI Setup
root = tk.Tk()
root.title("Word/Name Meaning Finder")
root.geometry("500x600")

# Label for search type
type_label = tk.Label(root, text="Select Type:", font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#007bff")
type_label.pack(pady=10)

# Combobox for type selection
type_combobox = ttk.Combobox(root, values=["Word", "Name"], state="readonly", font=("Arial", 12), width=15)
type_combobox.pack()

# Update search label when search type changes
type_combobox.bind("<<ComboboxSelected>>", update_search_label)

# Label for search term
search_label = tk.Label(root, text="Enter Word or Name:", font=("Arial", 14), bg="#f4f4f9", fg="#007bff")
search_label.pack(pady=10)

# Entry for search term
search_entry = tk.Entry(root, font=("Arial", 14), width=30, bd=2, relief="solid")
search_entry.pack()

# Search Button
search_button = tk.Button(root, text="Search", font=("Arial", 14), command=search_meaning, bg="#28a745", fg="white", bd=2, relief="solid")
search_button.pack(pady=20)

# Result display label
result_label = tk.Label(root, text="", font=("Arial", 12), justify="left", padx=10, pady=10, wraplength=450, bg="#f4f4f9", fg="#333333")
result_label.pack()

# Run the GUI
root.mainloop()
