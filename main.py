from goodreads import check_book_has_french_version, return_all_book_links_from_search, return_book_info_from_link

QUERY = "Get Shorty"

book_links = return_all_book_links_from_search("Get Shorty")

book_info = return_book_info_from_link(book_links[0])

french_versions = check_book_has_french_version(book_info["editions_link"])

print(french_versions)