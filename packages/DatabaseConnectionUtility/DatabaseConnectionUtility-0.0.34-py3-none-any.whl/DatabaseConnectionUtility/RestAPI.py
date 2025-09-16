
import os, requests, json
import pandas as pd
import loggerutility as logger
import commonutility as common
from json.decoder import JSONDecodeError

class RestAPI:
    
    password    =  ""
    requestType =  "POST"
    headers     =  {"TOKEN_ID" : ""}
    drillDown   =  ""
    argumentList=  ""

    def testAPI(self, dbDetails):

        if 'URL' in dbDetails.keys():
            if dbDetails.get('URL') != None:
                url = dbDetails['URL'].strip()
        
        if 'KEY' in dbDetails.keys():
            if dbDetails.get('KEY') != None:
                self.password = dbDetails['KEY']

        if 'AUTHENTICATION_TYPE' in dbDetails.keys():
            if dbDetails.get('AUTHENTICATION_TYPE') != None:
                authenticationType = dbDetails['AUTHENTICATION_TYPE']
        
        if 'NAME' in dbDetails.keys():
            if dbDetails.get('NAME') != None:
                userName = dbDetails['NAME']
        
        if 'LOGIN_URL' in dbDetails.keys():
            if dbDetails.get('LOGIN_URL') != None:
                loginUrl = dbDetails['LOGIN_URL'].strip()
        
        if 'REQUEST_TYPE' in dbDetails.keys() and dbDetails['REQUEST_TYPE'] != None:
            self.requestType = dbDetails['REQUEST_TYPE'].upper()
            logger.log(f"\n\nrequestType :::: \t{self.requestType}\t{type(self.requestType)}\n","0")

        if 'DRILLDOWN_VARIABLE' in dbDetails.keys() and dbDetails['DRILLDOWN_VARIABLE'] != None:
            self.drillDown = dbDetails['DRILLDOWN_VARIABLE']
            logger.log(f"\n\drillDown :::: \t{self.drillDown}\t{type(self.drillDown)}\n","0")

        self.headers["TOKEN_ID"] = self.password
        try:
            if authenticationType == "N":
                
                if self.requestType == "GET" :
                    response = requests.request("GET",url)
                
                elif self.requestType == "POST":
                    response = requests.request("POST", url)


                if str(response.status_code) == '200':
                    logger.log(f"\n\n URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n ","0")
                    return str(response.status_code)
                
                else:
                    logger.log(f"Invalid response for {response.url} and request type '{self.requestType}' {str(response)}","0")
                    raise Exception(f"Invalid response {str(response.status_code)} for {response.url}")
                

            elif authenticationType == "T":
                logger.log(f"Inside token-based condition","0")
                
                if self.requestType == "GET" :
                    finalServerUrl = self.create_GetRequest_url(url, self.headers)
                    response = requests.request("GET", finalServerUrl)   
                
                elif self.requestType == "POST":
                    response = requests.request("POST", url , headers=self.headers)   
                
                logger.log(f"\n\n TYpe-T Response::: {response.text} \t DATA-TYpe::{type(response.text)}\n ","0")
                if str(response.status_code) == '200':
                    logger.log(f"\n\n URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n ","0")
                    return str(response.status_code)
                
                else:
                    logger.log(f"Invalid response for {response.url} and request type '{self.requestType}' {str(response)}","0")
                    raise Exception(f"Invalid response for {response.url} {str(response)}")
                

            elif authenticationType == "S":
                try:
                    session= requests.Session()
                    login_formParam = {'USER_CODE': userName, 'PASSWORD': self.password, 'DATA_FORMAT':'JSON','APP_ID': 'INSIGHTCON'  }
                    logger.log(f"login_formParam session login::::{login_formParam}","0")
                    
                    if self.requestType == "GET" :
                        finalLoginUrl = self.create_GetRequest_url(loginUrl, login_formParam)
                        response = session.get(finalLoginUrl)
                    
                    elif self.requestType == "POST":
                        response = session.post(loginUrl , login_formParam)
                    
                    logger.log(f"\n\n Login URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n ","0")
                    logger.log(f"\n\n response sessionBased loginURL::: {response.text} \t{type(response.text)} \n ","0")                    
                    if str(response.status_code) == '200':
                        status = (json.loads(response.text))['Response']['status']
                        
                        if status == 'success':
                            logger.log(f"Session based login successful","0")
                            return str(response.status_code)

                        elif status == 'error':
                            logger.log(f"session login response :: {json.loads(response.text)}","0")
                            errorMessage = str(json.loads(response.text)['Response']['results'])
                            logger.log(f"session login errorMessage :: {errorMessage}{type(errorMessage)}","0")
                            raise Exception(errorMessage)
                    else:
                        logger.log(f"Invalid response for {response.url} and request type '{self.requestType}' {str(response)}","0")
                        raise Exception(f"Invalid response for {response.url} {str(response)}")
                    
                except Exception as e:
                    logger.log(f'\n Print exception returnSring inside auth_type-S : {e}', "0")
                    raise Exception(e)

            else:
                logger.log(f"Invalid authentication Type::{authenticationType}","0")
                raise Exception(f"Invalid Authentication Type::'{authenticationType}'")
                
        except Exception as e:
            logger.log(f"exception in RestAPI:: {e}","0")
            raise Exception(e)

    def getData(self, calculationData):
        columnNameList  =  []
        jsonDataResponse=  ""
        functionName    =  ""
        main_formParam  =  {'DATA_FORMAT':'JSON','APP_ID': 'INSIGHTCON'}
        description     =  ""
        trace           =  ""
        argumentList    =  {}
        response        =  ""
        finalServerUrl  =  ""
        
        logger.log(f"inside RestAPI getData() calculationData::{calculationData}","0")
        if 'dbDetails' in calculationData.keys() and calculationData.get('dbDetails') != None:
            if 'AUTHENTICATION_TYPE' in calculationData['dbDetails'] and calculationData.get('dbDetails')['AUTHENTICATION_TYPE'] != None:
                authentication_Type = calculationData['dbDetails']['AUTHENTICATION_TYPE']

            if 'URL' in calculationData['dbDetails'] and calculationData.get('dbDetails')['URL'] != None:
                serverUrl = calculationData['dbDetails']['URL'].strip()

            if 'NAME' in calculationData['dbDetails'] and calculationData.get('dbDetails')['NAME'] != None:
                userName = calculationData['dbDetails']['NAME']

            if 'KEY' in calculationData['dbDetails'] and calculationData.get('dbDetails')['KEY'] != None:
                self.password = calculationData['dbDetails']['KEY']
            
            if 'source_sql' in calculationData.keys():
                if calculationData.get('source_sql') != None:
                    main_sqlQuery = calculationData['source_sql']
            
            if 'LOGIN_URL' in calculationData['dbDetails'] and calculationData.get('dbDetails')['LOGIN_URL'] != None:
                loginUrl = calculationData['dbDetails']['LOGIN_URL'].strip()

            if 'argumentList' in calculationData and calculationData['argumentList'] != {}:
                argumentList = json.loads(calculationData['argumentList'])
                logger.log(f"\n\nargumentList :::: \t{argumentList}\t{type(argumentList)}\n","0")

            if 'REQUEST_TYPE' in calculationData['dbDetails'] and calculationData.get('dbDetails')['REQUEST_TYPE'] != None:
                self.requestType = calculationData['dbDetails']['REQUEST_TYPE'].upper()
                logger.log(f"\n\requestType :::: \t{self.requestType}\t{type(self.requestType)}\n","0")

            if 'DRILLDOWN_VARIABLE' in calculationData['dbDetails'] and calculationData.get('dbDetails')['DRILLDOWN_VARIABLE'] != None:
                self.drillDown = calculationData.get('dbDetails')['DRILLDOWN_VARIABLE']
                logger.log(f"\n\ndrillDown :::: \t{self.drillDown}\t{type(self.drillDown)}\n","0")

        self.headers["TOKEN_ID"] = self.password
        if authentication_Type == 'N':               
            try:
                paramJson, functionName = self.extractQueryParams(main_sqlQuery, argumentList)

                if self.requestType == "GET" :
                    logger.log(f"Type-N  'GET' ")
                    finalServerUrl = self.create_GetRequest_url(serverUrl, paramJson)
                    logger.log(f"Type-N finalServerUrl for requestType 'GET' ::: {finalServerUrl}")
                    response = requests.request("GET", finalServerUrl)   
                
                elif self.requestType == "POST":
                    logger.log(f"Type-N ServerUrl RequestType 'POST' CAll ::: {serverUrl}")
                    response = requests.request("POST", serverUrl , data = paramJson)
            
                logger.log(f"\n\n Authentication Type::: {authentication_Type} \n Main URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n raw response::: {response.text}\n\n ","0")
                if len(response.text) == 0:
                    returnErr = "Blank response returned against the requested url. No records found."
                    raise Exception(returnErr)

                if str(response.status_code) == '200':
                    logger.log(f"{response.url}\t<{response}>","0")
                    logger.log(f"\nRest_API Type-N raw responseee ::: {response.text} {type(response.text)}\n","0")
                    if type(response) != dict :
                        jsonDataResponse = response.json()
                    
                else:
                    logger.log(f"Auth_Type-N Response status: <{str(response.status_code)}>","0")
                    trace = f" {str(response.url)}  <{str(response.status_code )}> "
                    description = str(response.text)
                    errorXML =common.getErrorXml(description, trace)
                    logger.log(f"\nMain Url response  : {errorXML} \t{type(errorXML)}","0")     
                    raise Exception(errorXML)


            except Exception as e:
                logger.log(f'\n Print exception returnString inside auth_type-N : {e}', "0")
                raise Exception(e)

        elif authentication_Type == 'T':      
            try:
                
                paramJson, functionName = self.extractQueryParams(main_sqlQuery, argumentList, self.password)
                
                if self.requestType == "GET" :
                    finalServerUrl = self.create_GetRequest_url(serverUrl, paramJson)
                    logger.log(f"Type-T finalServerUrl for requestType 'GET' ::: {finalServerUrl}")
                    response = requests.request("GET", finalServerUrl, headers=self.headers)   
                
                elif self.requestType == "POST":
                    logger.log(f"Type-T ServerUrl RequestType 'POST' CAll ::: {serverUrl}")
                    response = requests.request("POST", serverUrl , headers=self.headers, data = paramJson)   
                
                logger.log(f"\n\n Authentication Type::: {authentication_Type} \n  Main URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n raw response::: {response.text}\n\n ","0")
                if len(response.text) == 0:
                    returnErr = "Blank response returned against the requested url. No records found."
                    raise Exception(returnErr)
        
                if str(response.status_code) == '200':
                    logger.log(f"{response.url}\t<{response}>","0")
                    logger.log(f"\nRest_API Type-T raw responseee ::: {response.text} {type(response.text)}\n","0")
                    
                    if type(response) != dict:
                        status = response.json()['Response']['status']
                    else:
                        status = response['Response']['status']   

                    if status == "success" :
                        if type(response) != dict:
                            jsonDataResponse = response.json()["Response"]["results"]
                        else:
                            jsonDataResponse = response["Response"]["results"]
                        logger.log(f"Auth_Type-T jsonDataResponse : {jsonDataResponse}","0")

                    elif status == "error":
                        errorXML = self.filter_ResponseError(response)
                        raise Exception(errorXML)
                        
                else:
                    logger.log(f"Auth_Type-T Response status: <{str(response.status_code)}>","0")
                    trace = f" {str(response.url)}  <{str(response.status_code )}> "
                    description = str(response.text)
                    errorXML =common.getErrorXml(description, trace)
                    logger.log(f"\nMain Url response  : {errorXML} \t{type(errorXML)}","0")     
                    raise Exception(errorXML)


            except Exception as e:
                logger.log(f'\n Print exception returnSring inside auth_type-T : {e}', "0")
                raise Exception(e)

        elif authentication_Type == 'S':   
            try:
                paramJson, functionName = self.extractQueryParams(main_sqlQuery, argumentList)        
                main_formParam = {**main_formParam, **paramJson}            # concat both json  
                logger.log(f"RestAPI getData() main_formParam  ::::{main_formParam}","0")
                
                session= requests.Session()
                login_formParam = {'USER_CODE': userName, 'PASSWORD': self.password, 'DATA_FORMAT':'JSON','APP_ID': 'INSIGHTCON'  }
                logger.log(f" RestAPI getData() TYPE_S login_formParam :::::{login_formParam}","0")
                
                if self.requestType == "GET" :
                    finalLoginUrl = self.create_GetRequest_url(loginUrl, login_formParam)
                    logger.log(f"Type-S finalLoginUrl for requestType 'GET' ::: {finalLoginUrl}")
                    response = session.get(finalLoginUrl, headers=self.headers)
                elif self.requestType == "POST" :    
                    response = session.post(loginUrl , login_formParam, headers=self.headers)
                
                logger.log(f"\n\n Authentication Type::: {authentication_Type} \n  Login URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n raw response::: {response.text}\n {type(response.text)}\n ","0")
                if str(response.status_code) == '200':
                    logger.log(f"\nType-S LoginUrl ::: {response.url} \n","0")
                    if type(response) != dict :
                        status = (json.loads(response.text))['Response']['status']
                    else:
                        status = (response)['Response']['status']
        
                    if status == 'success':
                        logger.log(f"Session based login successful","0")

                        cookie                      = response.cookies
                        tokenId                     = (json.loads(response.text))['Response']['results']['TOKEN_ID'] if type(response.text) != dict else (response.text)['Response']['results']['TOKEN_ID'] 
                        serverUrl                   = serverUrl + "/" + functionName if serverUrl[-1] != "/" else serverUrl +  functionName
                        main_formParam['TOKEN_ID']  = tokenId
                        
                        logger.log(f" RestAPI getData() TYPE_S cookie :::::{cookie} tokenid:::::::{tokenId}\nserverUrl:::::::{serverUrl}","0")
                        logger.log(f"Rest_API main_formParam getData() line 196::::{main_formParam}","0")
                        
                        if self.requestType == "GET" :
                            finalServerUrl = self.create_GetRequest_url(serverUrl, main_formParam)
                            logger.log(f"Type-S finalServerUrl for requestType 'GET' ::: {finalServerUrl}")
                            response = session.get(finalServerUrl , headers=self.headers, cookies=cookie)    
                        elif self.requestType == "POST" :    
                            response = session.post(serverUrl , main_formParam, headers=self.headers, cookies=cookie)
                        
                        logger.log(f"\n\n Authentication Type::: {authentication_Type} \n  Main URL::: {response.url} \n Request Type::: {self.requestType} \n Status_Code::: {response}\n raw response::: {response.text}\n Response DatType::: {type(response.text)}\nLine\n ","0")
                        
                        if len(response.text) == 0:
                            returnErr = "Blank response returned against the requested url. No records found."
                            raise Exception(returnErr)

                        if response.status_code != 200:
                            trace = f" {str(response.url)}  <{str(response.status_code )}> "
                            description = str(response.text)
                            errorXML =common.getErrorXml(description, trace)
                            logger.log(f"\nMain Url response  : {errorXML} \t{type(errorXML)}","0")     
                            raise errorXML
                        
                        if type(response) != dict:
                            try :
                                response = json.loads(response.text)
                            except JSONDecodeError as err:
                                logger.log(f"Decoding response JSON has failed. \nPlease check the received response below::: '{response.text}'")
                                returnErr = response.text
                                raise Exception(returnErr)
                            
                        logger.log(f"Main-Url response ::: {response} \n","0")
                        status = response['Response']['status']
                        
                        if status == "success":
                            jsonDataResponse=response['Response']['results']
                        elif status == "error":
                            errorXML = self.filter_ResponseError(response)
                            raise Exception(errorXML)

                        logger.log(f"\n type(jsonDataResponse) : \t{type(jsonDataResponse)}\n","0")     
                        if type(jsonDataResponse) == str :
                            jsonDataResponse=json.loads(jsonDataResponse)
                        logger.log(f"Rest_API Type-S responseee after convert  ::: {jsonDataResponse} \n{type(jsonDataResponse)}","0")
                        
                    elif status == 'error':
                        logger.log(f" Type-S LoginUrl Error-Case : {response.json()}","0")
                        errorMessage = response.json()["Response"]["results"]
                        raise Exception(errorMessage)
                        

                else:
                    logger.log(f"Login-Url Response Status: {str(response.status_code)}","0")
                    trace = f" {str(response.url)}  <{str(response.status_code )}> "
                    description = str(response.text)
                    errorXML =common.getErrorXml(description, trace)
                    raise Exception(errorXML)
                
            except Exception as e:
                logger.log(f'\n Print exception returnSring inside auth_type-S : {e}', "0")
                raise Exception(e)
        
        logger.log(f"jsonDataResponse::{jsonDataResponse}","0")
        if functionName == "getVisualData":
            dfObject = pd.DataFrame(jsonDataResponse[1:])
        else:
            dfObject = pd.DataFrame(jsonDataResponse)
        logger.log(f"dfObject::{dfObject}","0")

        columnNameStr= main_sqlQuery[7:main_sqlQuery.find("from")].strip()
        if "," in columnNameStr:
            columnNameStr=columnNameStr.split(",")
            columnNameList=[i.strip() for i in columnNameStr]
            dfObject = dfObject[columnNameList]
            logger.log(f" RestAPI no-AuthenticationType df:: {dfObject}","0")
        elif "*" in columnNameStr:
            pass
        else:
            dfObject = dfObject[columnNameStr].to_frame()  

        return dfObject
           
    def extractQueryParams(self, sqlQuery, argumentList, tokenId=""):
        paramJson   = {}
        paramLst    = []
        functionName= ""
        jsonOBJ     = {}
        logger.log(f"source_sql query::::{sqlQuery}","0")

        
        if len(tokenId) > 0 :
            paramJson["TOKEN_ID"] = tokenId 
        
        for keyName in list(argumentList.keys()):
            logger.log(f"keyName:: {keyName}")
            if keyName.rfind("_") != -1 :
                logger.log(f'case "_" present in keyName at position {keyName.rfind("_")} ')
                if keyName[ keyName.rfind("_")+1 ].isdigit():
                    logger.log("case digit after '_' found")
                    new_keyName = keyName[:keyName.rfind("_")]
                    if new_keyName[-1] == '"' :
                        logger.log(f"Double quotes found in key Name case")
                        new_keyName = new_keyName[:-1]
                    argumentList[new_keyName] = argumentList.pop(keyName)
        logger.log(f"\n\nargumentList after removing handing '_' Case::::{argumentList}\n","0")

        sqlQuery = " ".join([word.lower() if word in ["FROM","WHERE","AND","OR"] else word for word in sqlQuery.split()])
        logger.log(f"updated sqlQuery::: {sqlQuery}")

        if " where " in sqlQuery:
            functionName = sqlQuery[sqlQuery.find(" from ")+5 : sqlQuery.find("where")].strip()
            logger.log(f"RestAPI getData() functionName where::{functionName}","0")
        else:
            functionName = sqlQuery[sqlQuery.find(" from ")+5 :].strip()
            logger.log(f"RestAPI getData() functionName from::{functionName}","0")

        if " where " in sqlQuery:
            new_sql= sqlQuery[sqlQuery.find(" where ")+6:].strip()
            logger.log(f"new_sql::{new_sql}","0")
            if " and " in new_sql:
                new_sql1=new_sql.split(" and ")
                paramLst=[i.strip() for i in new_sql1]
                logger.log(f" final paramLst::{paramLst}","0")
            else:
                paramLst.append(new_sql)
                logger.log(f"final paramLst else::{paramLst}","0")

        for i in paramLst:
            element=i.split(" =")
            logger.log(f" paramLst element:/n  {element}","0")    
            paramJson[element[0].strip()] = element[1].strip()[1:-1]
            logger.log(f"Line 319 before replacing argumentList:::","0")
        
        
        logger.log(f"paramJson line 391:::{paramJson} \nfunctionName:::{functionName} \n","0")
        
        logger.log(f"Drill-down value:'{self.drillDown}'\n","0")   
        if self.drillDown != "" and self.drillDown in paramJson.keys():
            logger.log(f"Drill-down value:'{self.drillDown}' is PRESENT in paramJson case. \n","0")   
            if len(paramJson[self.drillDown]) > 0:                                                                                      
                try :
                    jsonOBJ = json.loads(paramJson[self.drillDown])
                    if len(argumentList ) > 0:
                        for i in range(len(argumentList)):
                            key = list(argumentList.keys())[i]
                            logger.log(f"KEY line 390:: {key}")
                            jsonOBJ[key] = argumentList[key]
                        paramJson[self.drillDown] = str(jsonOBJ).replace( "'", '"')
                        logger.log(f"\n\nLine 391  After Drill-Down BLANK case paramJson :: {paramJson}\n","0")
                except Exception as err :
                    raise Exception("'drillDown' value is not valid JSON format.",err)

            else:
                if len(argumentList ) > 0:
                    for i in range(len(argumentList)):
                        key = list(argumentList.keys())[i]
                        logger.log(f"KEY line 412:: {key}")     
                        jsonOBJ[key] = argumentList[key]
                    paramJson[self.drillDown] = str(jsonOBJ).replace( "'", '"')
                    logger.log(f"\n\nLine 416  CASE len(paramJson[drillDown]) is 0   :: {paramJson}\n","0")
        
        elif self.drillDown != "" and self.drillDown not in paramJson.keys():
            if len(argumentList ) > 0:
                for i in range(len(argumentList)):
                    key = list(argumentList.keys())[i]
                    logger.log(f"KEY line 422:: {key}")     
                    jsonOBJ[key] = argumentList[key]
                paramJson[self.drillDown] = str(jsonOBJ).replace( "'", '"')
                logger.log(f"\n\nLine 425 CASE self.drillDown not in paramJson.keys   :: {paramJson}\n","0")

        else:
            logger.log(f"Drill-Down BLANK case {self.drillDown} \n","0")    
            logger.log(f"argumentList ::: {argumentList}")    
            if len(argumentList) > 0 :
                for i in range(len(argumentList)):
                    key = list(argumentList.keys())[i]
                    logger.log(f"KEY line 432:: {key}")     
                    paramJson[key] = argumentList[key]
                    logger.log(f"\n\nLine 434  After Drill-Down BLANK case paramJson :: {paramJson}\n","0")
    
        logger.log(f"\n\n FINAL paramJson line 436:::{paramJson} \nfunctionName:::{functionName} \n","0")
        return paramJson, functionName

    def create_GetRequest_url(self, url, paramJson):
        serverUrl = url + "?" if url[-1] != "?" else url
        for index in range(len(paramJson)):
            serverUrl = serverUrl + list(paramJson.keys())[index] + "=" + list(paramJson.values())[index] + "&"
        
        if serverUrl[-1] == "&":
            serverUrl = serverUrl[:-1]
        logger.log(f"serverUrl line 467 ::: {serverUrl}")
        return serverUrl

    def filter_ResponseError(self, response):
        errorMessage=json.loads(response['Response']['results'])['Root']['Errors']['error']
        logger.log(f"\nRest_API responseee errorMessage::: {errorMessage} \n{type(errorMessage)}","0")
        if "description" in errorMessage:
            description = errorMessage["description"]
        if "message" in errorMessage:
            message = errorMessage["message"]
        if "trace" in errorMessage:
            trace = errorMessage["trace"]
        errorXML =common.getErrorXml(description, trace, message)
        logger.log(f"\n errorXML : {errorXML} \t{type(errorXML)}","0")     
        return errorXML


