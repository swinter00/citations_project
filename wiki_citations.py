import bz2
import os
import re
from bs4 import BeautifulSoup as Soup

def extract_info(read_filename, write_filename, date, append_bool):
    '''
    Function parses an xml Wikipedia data dump and writes all journal references present in the dump to a tsv file in the format
    Reference\tArticle Title\tDate. The references can be appended to an existing tsv file by setting append_bool = True.
    '''
    with bz2.open(os.path.dirname(os.path.abspath(__file__)) + "/" + read_filename, "r") as f:
        doc = f.read().decode("utf-8")
    soup = Soup(doc, "xml")
    ref_dict = {}
    for page in soup.findAll("page"):
        title = page.title.text
        references = re.findall(r'(?i)<ref.{0,50}>{{Cite journal.*?</ref>', page.text)
        if references != []:
            for ref in references:
                if ref not in ref_dict.keys():
                    ref_dict[ref] = (title, date)
    if append_bool:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/" + write_filename, "r") as f:
            existing = f.read()
    else:
        existing = "Reference\tArticle Title\tDate\n"
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + write_filename, "w") as f:
        f.write(existing)
        for key in ref_dict.keys():
            try:
                f.write(key + "\t" + ref_dict[key][0] + "\t" + ref_dict[key][1] + "\n")
            except:
                continue

class Reference:
    def __init__(self):
        self.title = None
        self.authors = None
        self.journal = None
        self.published = None
        self.referenced = None
        self.wiki_article = None
        self.citations = []

    def __str__(self):
        return self.title
     
def convert_to_class(ref):
    '''
    Converts a single reference that has been extracted from the data dump to an instance of the Reference class.
    '''
    r = Reference()
    try:
        r.wiki_article = ref.split("\t")[1]
    except:
        r.wiki_article = None
    try:
        r.referenced = ref.split("\t")[2]
    except:
        r.referenced = None
    try:
        r.title = re.search(r"title\s?=\s?([\w,\s';\-\.\?\:]+)", ref).group(1).strip()
    except:
        r.title = None
    try:
        r.authors = find_authors(ref)
    except:
        r.authors = None
    try:
        r.journal = re.search(r"journal\s?=\s?([\w\.\s,-\[\]]+)", ref).group(1).strip(' []')
    except:
        r.journal = None
    try:
        r.published = re.search(r"year\s?=\s?(\d+)\b", ref).group(1)
    except:
        r.published = None
    return r

def find_authors(ref):
    '''
    Returns a string of authors from a reference, accounting for the different ways that authors are cited.
    '''
    check1 = re.search(r"author\s?=\s?([\w\s\.]+\b)", ref)
    if check1:
        return check1.group(1)
    check2 = re.search(r"vauthors\s?=\s?([\w\s\.,'-]+\b)", ref)
    if check2:
        return check2.group(1)
    check3_last = re.finditer(r"last\d{0,2}\s?=\s?([\w\s\-\.]+)\b", ref)
    check3_first = re.finditer(r"first\d{0,2}\s?=\s?([\w\s\-\.]+)\b", ref)
    if check3_last and check3_first:
        last_names = [match.group(1) for match in check3_last]
        first_names = [match.group(1) for match in check3_first]
        return ", ".join([" ".join(tup) for tup in list(zip(first_names, last_names))])
    return None

def read_from_file(filename):
    '''
    Reads a tsv file containing references and converts those references to a list of class instances
    '''
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + filename, "r") as f:
        references = f.readlines()[1:]
    ref_list = []
    for ref in references:
        ref_list.append(convert_to_class(ref))
    return ref_list

def main():
    extract_info("20180101articles10.xml-p2336425p3046511.bz2", "references.tsv", "20180101", True)
    ref_list = read_from_file("references.tsv")
    
if __name__ == "__main__":
    main()