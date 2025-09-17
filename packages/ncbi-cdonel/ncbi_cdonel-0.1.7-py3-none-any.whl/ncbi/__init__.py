from Bio import Entrez

class FetchRecords:
    
    """
    Abstract class that writes NCBI records out to file using session history from SearchPrimaryID. 

    Parameters
    ----------
    primary_ids : Dictionary 
        containing, IdList, WebEnv, QueryKey, ...
    db : str NCBI database
    idtype : str 
        default is GI numbers, 'acc' for accession numbers.
    rettype : str
        'genbank' to return GenBank record or 'fasta' to return FASTA records.
    retmode : str
        what type of file is returned 'text' or 'xml'.
    filename : str
        Name of output file.

    Output
    ------
    Writes records to /data.
    """
    
    def __init__(self, primary_ids=None, db=None, idtype=None, rettype=None, retmode=None, output_path=None):
        self.primary_ids = primary_ids
        self.db = db
        self.idtype = idtype
        self.batch_size = self.set_batch_size(primary_ids)
        self.rettype = rettype
        self.retmode = retmode
        self.output_path = output_path

        self.fetch_records(
                            db = self.db,
                            batch_size=self.batch_size, 
                            output_path=self.output_path, 
                            rettype=self.rettype,
                            retmode=retmode,
                            primary_ids = self.primary_ids,
                            idtype=idtype
                            )

    def fetch_records(self, db, rettype, retmode, batch_size, idtype, primary_ids, output_path):
        count = len(primary_ids.get_idlist())
        with open(output_path, 'w', encoding="utf-8") as output_handle:
            for start in range(0, count, batch_size):
                end = min(count, start + batch_size)
                print("Downloading record %i to %i" % (start + 1, end))

                stream = Entrez.efetch(
                    db=db,
                    rettype=rettype,
                    retmode=retmode,
                    retstart=start,
                    retmax=batch_size,
                    webenv=primary_ids.get_webenv(),
                    query_key=primary_ids.get_querykey(),
                    idtype=idtype
                )   
                
                data = stream.read()
                output_handle.write(data)
                stream.close()

    def set_batch_size(self, primary_ids):

        """
        Sets batch size based on expected number of sequences to be downloaded.

        Parameters
        ----------
        primary_ids : Dictionary 
            containing, IdList, WebEnv, QueryKey, ...

        Returns
        -------
        batch_size : int
        """

        count = len(primary_ids.get_idlist())
        if count <= 9999:
            batch_size = count
            return batch_size
        
        elif count > 10000:
            batch_size = 10000
            return batch_size
        
        
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


class FetchPubmed:
    
    def __init__(self, search, retmax, output_path, email, api_key):
        Entrez.email = email
        Entrez.api_key = api_key
        self.search = search
        self.retmax = retmax
        self.output_path = output_path
        self.primary_ids = SearchPrimaryID(db='pubmed', term=self.search, retmax=self.retmax)
        self.records = FetchRecords(primary_ids=self.primary_ids, db='pubmed', rettype='medline', retmode='text', output_path=self.output_path)