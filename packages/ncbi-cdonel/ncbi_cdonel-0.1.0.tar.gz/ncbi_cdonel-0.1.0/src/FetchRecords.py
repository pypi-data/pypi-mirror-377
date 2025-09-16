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
        