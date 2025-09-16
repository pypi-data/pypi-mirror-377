from SearchPrimaryID import SearchPrimaryID
from FetchRecords import FetchRecords
from Bio import Entrez

class FetchNucleotides:

    def __init__(self, search, rettype, retmax, output_path, email, api_key):
        Entrez.email = email
        Entrez.api_key = api_key
        self.search = search
        self.rettype = rettype
        self.retmax = retmax
        self.output_path = output_path
        self.primary_ids = SearchPrimaryID(db='nucleotide', idtype='acc', term=self.search, retmax=self.retmax)
        self.records = FetchRecords(primary_ids=self.primary_ids, db='nucleotide', idtype='acc', rettype=self.rettype, retmode='text', output_path=self.output_path)
