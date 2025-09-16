# updated 01-Aug-23

import snowflake.connector
import loggerutility as logger

class SnowFlake:
    def getConnection(self, dbDetails):  
        logger.log(f"inside SnowFlake getConnection","0") 
        uid  = ""                                             
        pwd  = ""                                             
        url  = ""                                             
        pool = None
        database = ""
        port     = ""
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
            self.pool = snowflake.connector.connect(account=url, database=database, user=uid, password=pwd)
        except Exception as e:
            logger.log(f"\nIssue in SnowFlake connection.{e}","0")
            
            return e
        if pool !=None:
            logger.log(f"\nConnected to SnowFlake DB.","0")
            
        return pool
