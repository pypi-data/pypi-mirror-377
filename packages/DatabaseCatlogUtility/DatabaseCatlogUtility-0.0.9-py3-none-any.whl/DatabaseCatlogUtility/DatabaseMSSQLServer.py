import loggerutility as logger
import pandas as pd
import traceback

class DatabaseMSSQLServer:
    
    def getTables(self,connectObj, dbDetails, userInfo, tableName=""):
        logger.log(f"inside DatabaseMSSQLServer getTables","0")
        resultStr = ""
        transDB = ""
        isTableFound = False
        
        if "transDB" in userInfo.keys():
            if len(userInfo["transDB"]) != 0 : 
                transDB = userInfo["transDB"]
                logger.log(f"transDB: {transDB}","0")

        if 'DATABASE' in dbDetails.keys():
            if dbDetails.get('DATABASE') != None:
                databaseName = dbDetails['DATABASE']
                logger.log(f"databaseName: {databaseName}","0")

        try:
            if (len(userInfo) != 0):
                cursor = connectObj.cursor()
                if ("" == tableName):	
                    selectQuery = '''SELECT table_name FROM information_schema.tables WHERE table_catlog="''' + databaseName +'"' 
                    logger.log(f"selectQuery {selectQuery}","0")
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    logger.log(f"resultStr DatabaseMSSQLServer getTable: {resultStr}","0")
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
                    logger.log(f"TableJson : {tableJson}", "0")
                    
                else:
                    logger.log(f"DatabaseMSSQLServer getTables else","0")
                    tableName = "'%"+tableName+"%'";
                    selectQuery =  "SELECT OBJECT_NAME FROM ALL_OBJECTS WHERE (OBJECT_TYPE='TABLE' OR OBJECT_TYPE='SYNONYM') AND  OWNER= '" +transDB.upper()+ "' AND OBJECT_NAME LIKE " + tableName.upper()  
                    
                    logger.log(f"SelectQuery DatabaseMSSQLServer getTables: {selectQuery}","0")
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    logger.log(f"DatabaseMSSQLServer getTables IF resultStr = {resultStr}","0")
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
                    # logger.log(f"TableJson: {tableJson}", "0")
            
                if(not isTableFound ) : 
                    resultStr = self.getErrorXml("Tables not found in the DatabaseMSSQLServer Database against the Schema "+transDB+"", "Table not Exist")
                    logger.log(f"error String DatabaseMSSQLServer getTables {resultStr}", "0")
            
            resultStr = tableJson
            
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
        
        finally:
            if (connectObj != None):
                connectObj.close()
                logger.log(f"DatabaseMSSQLServer DB connection closed","0")
        return resultStr
                
    def getColumns(self, connectObj, tableNames, userInfo, dbDetails):
        logger.log(f"inside DatabaseMSSQLServer getColumns()", "0")
        if "transDB" in userInfo.keys():
            if len(userInfo["transDB"]) != 0: 
                transDB = userInfo["transDB"]

        if 'DATABASE' in dbDetails.keys():
            if dbDetails.get('DATABASE') != None:
                databaseName = dbDetails['DATABASE']
                logger.log(f"databaseName: {databaseName}","0")
        
        resultStr = ""
        tableArray = tableNames.split(",")            
        counter = 0 
        mainDataArray=[]
                        
        try:
            if len(userInfo) != 0 :
                if  (tableNames !=  "") and (tableNames != None):
                     
                    for j in range(len(tableArray)):
                        
                        columnDataArray=[]
                        mainDataJson = {}
                        currentTable= tableArray[j]
                        selectQuery = '''SELECT column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME ="''' + tableArray[j] +'" ORDER BY ORDINAL_POSITION'  
                        logger.log(f"selectQuery: {selectQuery}","0")
                        
                        cursor = connectObj.cursor()
                        cursor.execute(selectQuery)
                        resultStr = cursor.fetchall()
                        logger.log(f"resultStr getColumns DatabaseMSSQLServer: {resultStr}", "0")
                        
                        for i in range(len(resultStr)):
                            counter+=1
                            columnData = {}
                            columnName = resultStr[i][0]
                            columnSize = resultStr[i][1] 
                            colType    = resultStr[i][2]
                            isNullable = resultStr[i][3]
                            javaType = ""
                            defaultFunction = ""
                            expression = ""
                            content = (columnName.replace("_", " ")).lower()
                            
                            if("CHAR".lower() == colType.lower()) or ("VARCHAR2".lower()==colType.lower()) or  ("VARCHAR".lower() == colType.lower()):
                                javaType = "java.lang.String"
                            
                            elif ("NUMBER".lower() == colType.lower()):
                                javaType = "java.math.BigDecimal"
                                defaultFunction = "SUM"
                            
                            elif ("DATE".lower() == colType.lower()):
                                javaType = "java.sql.Date"
                            
                            else:
                                javaType = "java.lang.String"
                                colType  = "CHAR"
                            
                            if( not"".lower() == defaultFunction.lower()):
                                expression = defaultFunction + "(" + columnName +")" 
                            
                            else:
                                pass
                            
                            columnData["DBNAME"]            =   columnName
                            columnData["NAME"]              =   columnName
                            columnData["CAPS"]              =   "false"
                            columnData["WIDTH"]             =   100
                            columnData["DBSIZE"]            =   columnSize
                            columnData["KEY" ]              =   "false"
                            columnData["COLID" ]            =   str(counter)
                            columnData["COLTYPE" ]          =   colType
                            columnData["NATIVETYPE" ]       =   "AN"
                            columnData["JAVATYPE" ]         =   javaType
                            columnData["DEFAULTFUNCTION" ]  =   defaultFunction
                            columnData["EXPRESSIONTYPE" ]   =   "C"
                            columnData["HIDDEN" ]           =   ""
                            columnData["DBTABLE" ]          =   currentTable
                            columnData["FORMAT" ]           =   ""
                            columnData["content"]           =   content
                            columnData["FEILD_TYPE"]        =   "TEXTBOX"
                            columnData["value"]             =   ""
                            columnData["name"]              =   content
                            columnData["descr"]             =   content
                            columnData["expression"]        =   expression
                            columnData["tableName"]         =   currentTable
                            columnData["tableDisplayName"]  =   currentTable.replace("_", " ").lower()
                            columnData["FUNCTION"]          =   defaultFunction;
                            columnData["groupName"]         =   ""
                            columnDataArray.append(columnData)
                    
                        mainDataJson["TABLE_NAME"]      =   currentTable
                        mainDataJson["COLUMN"]          =   columnDataArray
                        mainDataJson["DISPLAY_NAME"]    =   currentTable.replace("_", " ").lower()
                        mainDataArray.append(mainDataJson)
                    
                    logger.log(f"mainDataArray DatabaseMSSQLServer : {mainDataArray}","0")
                    connectObj.close()
                    connectObj = None
            
            resultStr = mainDataArray
            logger.log(f"resultStr: {resultStr}","0")
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
        
        finally:
            if connectObj != None:
                connectObj.close()
                logger.log(f"DatabaseMSSQLServer getColumns Connection closed. ","0" )
        
        return resultStr	
    
    def getTableData(self, connectObj, tableName, userInfo, dbDetails):
        selectQuery = "SELECT * FROM " + tableName + " WHERE ROWNUM <= 50"
        logger.log(f"selectQuery: {selectQuery}","0")
        df = pd.read_sql(selectQuery, connectObj)
        tableDataJson = df.assign( **df.select_dtypes(['datetime']).astype(str).to_dict('list') ).to_json(orient="records")
        return tableDataJson

    def getErrorXml(self, descr, trace):
        errorXml ='''<Root>
                            <Header>
                                <editFlag>null</editFlag>
                            </Header>
                            <Errors>
                                <error type="E">
                                    <message><![CDATA['''+descr+''']]></message>
                                    <trace><![CDATA['''+trace+''']]></trace>
                                    <type>E</type>
                                </error>
                            </Errors>
                        </Root>'''
        
        return errorXml

    
