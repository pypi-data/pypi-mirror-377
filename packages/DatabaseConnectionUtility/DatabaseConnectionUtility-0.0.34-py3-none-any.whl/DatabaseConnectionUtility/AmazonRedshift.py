# updated 01-Aug-23

import pyodbc
import loggerutility as logger

class AmazonRedshift:
    def getConnection(self, dbDetails):  
        logger.log(f"inside AmazonRedshift getConnection","0") 
        uid  = ""                                             
        pwd  = ""                                             
        url  = ""                                             
        port = 5439
        pool = None
        database = ""
        driver="/opt/amazon/redshiftodbcx64/librsodbc64.so"
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
            pool = pyodbc.connect(f'DRIVER={driver};Server={url};Database={database};User ID={uid};Password={pwd};Port={port};String Types=Unicode')
            if pool !=None:
                logger.log(f"\nConnected to AmazonRedshift DB.","0")
        
        except Exception as e:
            logger.log(f"\nIssue in AmazonRedshift connection.{e}","0")
            
            raise e
            
        return pool

