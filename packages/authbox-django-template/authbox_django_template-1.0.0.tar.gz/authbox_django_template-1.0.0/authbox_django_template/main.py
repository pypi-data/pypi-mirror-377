import argparse
from bs_get_all_text import scrape_text
from convert_to_django import scrape_all

def main():
    print("Hello, let's convert to django template!")
    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument("--templatename", help="Template Name (like ilanding)", required=True)
    parser.add_argument("--filepath", help="File path (usually index.html)", required=True)
    args = parser.parse_args()
    # print(f"File Path is, {args.filepath}!")
    scrape_text(args.filepath)
    scrape_all(args.templatename, 'res.html')
    scrape_all(args.templatename, 'src.html')

if __name__ == "__main__":
    main()
