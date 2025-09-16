# updated 01-Aug-23

import loggerutility as logger
import psycopg2


class Postgress:
    def getConnection(self, dbDetails):
        logger.log(f"Called Postgress getConnection.", "0")

        uid  = ""                                             
        pwd  = ""                                             
        url  = ""                                             
        port = 5432
        pool = None
        database = ""
        instance = ""

        if 'NAME' in dbDetails.keys():
            if dbDetails.get('NAME') != None:
                uid = dbDetails['NAME']
        
        if 'KEY' in dbDetails.keys():
            if dbDetails.get('KEY') != None:
                pwd = dbDetails['KEY']
        
        if 'URL' in dbDetails.keys():
            if dbDetails.get('URL') != None:
                url = dbDetails['URL']

        if 'DATABASE' in dbDetails.keys():
            if dbDetails.get('DATABASE') != None:
                database = dbDetails['DATABASE']

        if 'DB_INSTANCE' in dbDetails.keys():
            if dbDetails.get('DB_INSTANCE') != None:
                instance = dbDetails['DB_INSTANCE']  

        if 'DB_PORT' in dbDetails.keys():
            if dbDetails.get('DB_PORT') != None:
                port = dbDetails['DB_PORT']  

        try:
            self.pool = psycopg2.connect(database=database, user=uid, password=pwd, host=url, port=port)
            if self.pool != None:
                logger.log(f"Connected to Postgress DB.","0")
                # logger.log(f"{self.pool}")
        
        except Exception as e:
            logger.log(f"\nIssue in Postgress connection.{e}","0")
            raise e
            
        return self.pool
