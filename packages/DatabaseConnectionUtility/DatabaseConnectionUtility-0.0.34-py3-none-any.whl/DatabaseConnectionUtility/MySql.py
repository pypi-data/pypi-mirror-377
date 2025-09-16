# updated  01-Aug-23

import mysql.connector as my_sql
import loggerutility as logger

class MySql:
    def getConnection(self, dbDetails):  
        logger.log(f"inside sql getConnection","0") 
        uid  = ""                                             
        pwd  = ""                                             
        url  = ""                                             
        port = 3306
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
                logger.log(f"instance:: {instance}","0")

        if 'DB_PORT' in dbDetails.keys():
            if dbDetails.get('DB_PORT') != None:
                port = dbDetails['DB_PORT']  
                logger.log(f"port:: {port}","0")

        try:
            pool = my_sql.connect(host=url, database=database, port=port, user=uid, password=pwd)
            if pool !=None:
                logger.log(f"\nConnected to Sql DB.","0")
        
        except Exception as e:
            logger.log(f"\nIssue in Sql connection.{e}","0")
            
            raise e
            
        return pool

