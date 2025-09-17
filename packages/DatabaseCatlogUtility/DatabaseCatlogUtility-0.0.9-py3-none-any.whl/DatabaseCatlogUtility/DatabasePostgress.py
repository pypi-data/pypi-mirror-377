import loggerutility as logger
import pandas as pd
import traceback

class DatabasePostgress:
    
    def getTables(self,connectObj, dbDetails, userInfo, tableName=""):
        logger.log(f"inside DatabasePostgress getTables","0")
        resultStr = ""
        transDB = ""
        databaseName=""
        isTableFound = False
        
        if "transDB" in userInfo.keys():
            if len(userInfo["transDB"]) != 0 : 
                transDB = userInfo["transDB"]
                logger.log(f"transDB: {transDB}","0")

        if 'DB_INSTANCE' in dbDetails.keys():
            if dbDetails.get('DB_INSTANCE') != None:
                databaseName = dbDetails['DB_INSTANCE']
                logger.log(f"databaseName: {databaseName}","0")

        try:
            if (len(userInfo) != 0):
                cursor = connectObj.cursor()
                if ("" == tableName):	
                    selectQuery = "SELECT table_name FROM information_schema.tables WHERE table_schema = '" + databaseName + "'"
                    logger.log(f"selectQuery {selectQuery}","0")
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    logger.log(f"resultStr DatabasePostgress getTable: {resultStr}","0")
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
                    logger.log(f"TableJson : {tableJson}", "0")
                    
                else:
                    logger.log(f"DatabasePostgress getTables else","0")
                    tableName = "%" + tableName + "%"
                    selectQuery = f"""SELECT table_name FROM information_schema.tables WHERE table_schema = '{databaseName}' AND table_name LIKE '{tableName}'"""

                    logger.log(f"SelectQuery DatabasePostgress getTables: {selectQuery}","0")
                    cursor.execute(selectQuery)
                    resultStr = cursor.fetchall()
                    logger.log(f"DatabasePostgress getTables IF resultStr = {resultStr}","0")
                    
                    tableJson={"Root":{"TABLEDETAILS":[]}}
                    for i in resultStr:
                        isTableFound = True
                        tableJson["Root"]["TABLEDETAILS"].append( { "TABLE_NAME" : i[0] } ) 
                    # logger.log(f"TableJson: {tableJson} ", "0")
            
                if(not isTableFound ) : 
                    resultStr = self.getErrorXml("Tables not found in the DatabasePostgress Database against the Schema "+transDB+"", "Table not Exist")
                    logger.log(f"error String DatabasePostgress getTables: {resultStr}", "0")
            
            resultStr = tableJson
            
        except Exception as e:
            trace = traceback.format_exc()
            descr = str(e)
            logger.log(f"{self.getErrorXml(descr, trace)}","0")
        
        finally:
            if (connectObj != None):
                connectObj.close()
                logger.log(f"DatabasePostgress DB connection closed","0")
        return resultStr
                
    def getColumns(self, connectObj, tableNames, userInfo, dbDetails):
        resultStr = ""
        tableArray = tableNames.split(",")            
        counter = 0 
        mainDataArray=[]

        logger.log(f"inside DatabasePostgress getColumns()", "0")
        if "transDB" in userInfo.keys():
            if len(userInfo["transDB"]) != 0: 
                transDB = userInfo["transDB"]
                
        if 'DATABASE' in dbDetails.keys():
            if dbDetails.get('DATABASE') != None:
                databaseName = dbDetails['DATABASE']
                logger.log(f"databaseName: {databaseName}","0")

        try:
            if len(userInfo) != 0 :
                if  (tableNames !=  "") and (tableNames != None):
                     
                    for j in range(len(tableArray)):
                        
                        columnDataArray=[]
                        mainDataJson = {}
                        currentTable= tableArray[j]

                        schema_query = f"""SELECT table_schema from INFORMATION_SCHEMA.TABLES WHERE table_name = '{currentTable}'"""
                        logger.log(f"getSchemaQuery ::: {schema_query}")
                        cursor = connectObj.cursor()
                        cursor.execute(schema_query)
                        schema_row = cursor.fetchone()

                        logger.log(f"schema_name ::: {databaseName}")
                        if schema_row:
                            schema_name = schema_row[0]
                            logger.log(f"Schema of {currentTable}: {schema_name}", "0")
                        else:
                            schema_name = databaseName

                        selectQuery = f"""SELECT column_name, character_maximum_length, data_type, is_nullable FROM information_schema.columns WHERE table_schema = '{schema_name}' AND table_name = '{tableArray[j]}'"""
                        logger.log(f"selectQuery: {selectQuery}","0")
                        
                        cursor = connectObj.cursor()
                        cursor.execute(selectQuery)
                        resultStr = cursor.fetchall()
                        logger.log(f"resultStr getColumns DatabasePostgress: {resultStr}", "0")
                        
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
                    
                    logger.log(f"mainDataArray DatabasePostgress : {mainDataArray}","0")
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
                logger.log(f"DatabasePostgress getColumns Connection closed. ","0" )
        
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

    
