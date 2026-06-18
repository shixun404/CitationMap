from citation_map import generate_citation_map

if __name__ == '__main__':
    scholar_id = 'MFWUo10AAAAJ'  # This is my Google Scholar ID. Replace this with your ID.
    generate_citation_map(scholar_id, use_proxy=True, num_processes=1)