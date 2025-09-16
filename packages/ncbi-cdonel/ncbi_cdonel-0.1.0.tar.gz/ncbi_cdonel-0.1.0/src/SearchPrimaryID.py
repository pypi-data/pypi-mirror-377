from Bio import Entrez

class SearchPrimaryID:
    
    """
    Abstract class that contains PrimaryIDs from NCBI database. Uses session history 
    (WebEnv and QueryKey) so that larger queries can be made. 

    Parameters
    ----------
    db : str
        Name of NCBI database to access (Ex. nucleotide).
    idtype : str
        Type of primary id to return, default is GI number, 'acc' for accession.
    term : str
        Phrase to search for in NCBI database.
    retmax : int
        Maximum number of records to return.
    """
    
    def __init__(self, db=None, idtype=None, term=None, retmax=None):
        self.db = db
        self.idtype = idtype
        self.term = term
        self.retmax = retmax
        self.primary_ids = self.search(db=self.db, idtype=self.idtype, term=self.term, retmax=self.retmax)

    def search(self, db, idtype, term, retmax):
        """
        Returns
        -------
        Dictionary
            Containing IdList, WebEnv, QueryKey, Count, ...
        """
        stream_session = Entrez.esearch(db=db, term=term, usehistory="y", idtype=idtype, retmax=retmax)
        primary_ids = Entrez.read(stream_session)
        stream_session.close()
        return primary_ids
    
    def get_idlist(self):
        """
        Returns
        -------
        List
            Primary IDs from NCBI database, such as accession numbers.
        """
        return self.primary_ids["IdList"]
    

    def get_webenv(self):
        """
        Returns
        -------
        Str
            Web environment string.
        """
        return self.primary_ids["WebEnv"]
    

    def get_querykey(self):
        """
        Returns
        -------
        Int
            Integer query key.
        """
        return self.primary_ids['QueryKey']
    