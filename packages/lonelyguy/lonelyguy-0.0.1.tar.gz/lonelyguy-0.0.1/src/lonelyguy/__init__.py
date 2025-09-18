import webbrowser
import sys


__all__ = ["open_urls"]

# Please go checkout these profiles!!
DEFAULT_URLS = [
    "https://www.discord.com/users/886120777630486538",
    "https://www.github.com/lonelyguy12",
    "https://www.instagram.com/lonelyguy7973",
]

def open_urls(urls_to_open):
    print("Opening your profiles...")
    try:
        browser = webbrowser.get('chrome')
    except webbrowser.Error:
        print("Chrome not found, using default browser.")
        browser = webbrowser.get()

    for url in urls_to_open:
        print(f"-> {url}")
        browser.open_new_tab(url)
    print("Pwease go check them out!!")

def main():
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print("No URLs provided. Opening default set.")
        urls = DEFAULT_URLS
    
    open_urls(urls)