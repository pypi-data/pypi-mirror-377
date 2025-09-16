from SearchPrimaryID import SearchPrimaryID
from FetchRecords import FetchRecords
from Bio import Entrez

class FetchPubmed:

    def __init__(self, search, retmax, output_path, email, api_key):
        Entrez.email = email
        Entrez.api_key = api_key
        self.search = search
        self.retmax = retmax
        self.output_path = output_path
        self.primary_ids = SearchPrimaryID(db='pubmed', term=self.search, retmax=self.retmax)
        self.records = FetchRecords(primary_ids=self.primary_ids, db='pubmed', rettype='medline', retmode='text', output_path=self.output_path)