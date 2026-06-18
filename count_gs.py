with open("output.txt", "r", encoding="utf-8") as f:
    content = f.read()
    count = content.count("[GS-only]")
    count_crossref = content.count("[CrossRef]")
print(count)
print(count_crossref)
