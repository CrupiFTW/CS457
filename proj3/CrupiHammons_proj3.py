'''
Created by Alex Crupi and Chase Hammons, 4/15/18, version 3
'''

import os, re
from contextlib import contextmanager #This is needed for opening multiple files

globalScopeDirectory = ""
workingDirectory = ""


def main():
    try:
        while (True):
            input = ""
            while not ";" in input and not "--" in input:
                input += raw_input("\n enter a command \n").strip('\r')  #Read the input command from terminal

            input = input.split(";")[0]  #Remove ; from the input command
            inputString = str(input)  #Normalize the input command
            inputString = inputString.upper()

            if "--" in input:  #Pass the comments
                pass

            elif "ALTER TABLE" in inputString:
                alterTable(input)

            elif "CREATE DATABASE" in inputString:
                createDatabase(input)

            elif "CREATE TABLE" in inputString:
                createTable(input)

            elif "DELETE FROM" in inputString:
                deleteFrom(input)

            elif "DROP DATABASE" in inputString:
                dropDatabase(input)

            elif "DROP TABLE" in inputString:
                dropTable(input)

            elif "INSERT INTO" in inputString:
                insertInto(input)

            elif "SELECT" in inputString:
                selectInput(input, inputString)

            elif "UPDATE" in inputString:
                updateFrom(input)

            elif "USE" in inputString:
                useDatabase(input)

            elif ".EXIT" in input:  #Exit database if specified before EOF
                print "All done"
                exit()

    except (EOFError, KeyboardInterrupt) as e:  #Exit script elegantly
        print "\n Connection to database terminated."

#Tier One Functions

@contextmanager
def multiFileManager(files, mode='rt'):
    """ Open multiple files and make sure they all get closed. """
    files = [open(file, mode) for file in files]
    yield files
    for file in files:
        file.close()

def useEnabled():  # Catch the error when a database hasn't been enabled
    if globalScopeDirectory is "":
        raise ValueError("!Failed to use table because no database was selected")
    else:
        global workingDirectory
        workingDirectory = os.path.join(os.getcwd(), globalScopeDirectory)

def returnColIndex(data):
    colIndex = data.split(" | ")
    for x in range(len(colIndex)):
        colIndex[x] = colIndex[x].split(" ")[0]
    return colIndex

def splitLines(line):
    lineCheck = line.split(" | ")
    for x in range(len(lineCheck)):  #Check that each column has an item
        lineCheck[x] = lineCheck[x].split(" ")[0]
    return lineCheck


def joinWhere(searchItem, tableVaribles, dataArray, joinType = 'inner'):
    
    counter = 0
    out = []
    flag = 0
    numTables = len(dataArray)
    matchedData = []
    emptyCols = ""

    #Collect column data from the selected array
    #Then check if the collected column data matches

    if "=" in searchItem:  #Evaluate the operator
        if "!=" in searchItem:
            rCol = searchItem.split(" !=")[0]
        else:
            leftSearch = searchItem.split(" =")[0]
            leftSearch = leftSearch.split(".")[1]

        rightSearch = searchItem.split("= ")[1]
        rightSearch = rightSearch.split(".")[1]


    if numTables == 2:
        leftTable = dataArray[0]
        rightTable = dataArray[1]
    else:
        print "!JOIN ONLY ACCEPTS TWO TABLES"
        return -1, -1

    leftData = []
    rightData = []

    leftColumn = get_column(leftTable[0])
    rightColumn = get_column(rightTable[0])
    
    for line in leftTable:
    #If not leftSearch in line:
        lineSeperated = separate(line)
        leftData.append(lineSeperated[leftColumn.index(leftSearch)])

    for line in rightTable:
        lineSeperated = separate(line)
        rightData.append(lineSeperated[rightColumn.index(rightSearch)])

    #Both the inner and outer joins start with matching data
    for x in range(len(leftData)):
        for y in range(len(rightData)):
            if leftData[x] == rightData[y]:
                rightTable[y] = rightTable[y].strip('\n')
                out.append(rightTable[y] + ' | ' + leftTable[x])
                counter += 1
                if join_type == 'left':
                    matchedData.append(leftTable[x])

    if join_type == 'left':
        number_of_data = len(rightColumn)
        for x in range(number_of_data):
            empty_cols += ' | '

        for x in range(len(leftData)):
            if not leftColumn[0] in leftTable[x]: #Remove the table key
                if not leftTable[x] in matchedData: #Do not run unless there are no matches within the provided data
                    out.append(leftTable[x].strip('\n') + emptyCols)
                    counter += 1
    return counter, out

def where(argumentToFind, actionToApply, data, updateValue = ""):
    mainCount = 0
    colIndex = returnColIndex(data)
    colNames = colIndex
    inData = list(data)
    out = []
    flag = 0
    if "=" in argumentToFind:  #Figure out the operator for splitting up the input
        if "!=" in argumentToFind:
            relColumn = argumentToFind.split(" !=")[0]
            flag = 1
        else:
            relColumn = argumentToFind.split(" =")[0]

        argumentToFind = argumentToFind.split("= ")[1]
        if "\"" in argumentToFind or "\'" in argumentToFind:  #Cleanup var
            argumentToFind = argumentToFind[1:-1]
        for line in data:
            lineCheck = splitLines(line)
            if argumentToFind in lineCheck:
                colIndex = colNames.index(relColumn)
                lineIndex = lineCheck.index(argumentToFind)
                if lineIndex == colIndex:  #Check for correct column
                    if actionToApply == "delete":
                        del inData[inData.index(line)]  #Remove the matching field
                        out = inData
                        mainCount += 1
                    if actionToApply == "select":
                        out.append(inData[inData.index(line)])
                    if actionToApply == "update":
                        attribute, field = updateValue.split(" = ")
                        if attribute in colNames:
                            splitLine = splitLines(line)
                            splitLine[colNames.index(attribute)] = field.strip().strip("'")
                            inData[inData.index(line)] = (' | ').join(splitLine)
                            out = inData
                            mainCount += 1

    elif ">" in argumentToFind:  #Figure out the operator for splitting up the input
        relColumn = argumentToFind.split(" >")[0]
        argumentToFind = argumentToFind.split("> ")[1]
        for line in data:  #Check each row
            lineCheck = line.split(" | ")
            for x in range(len(lineCheck)):  #Check each column item
                lineCheck[x] = lineCheck[x].split(" ")[0]
                try:
                    lineCheck[x] = float(lineCheck[x])  #Only check numeric fields
                    if lineCheck[x] > float(argumentToFind):  #Match query
                        tempColIndex = colIndex.index(relColumn)
                        if x == tempColIndex:  #Check for correct column
                            if actionToApply == "delete":
                                del inData[inData.index(line)]  #Remove matched field
                                out = inData
                                mainCount += 1
                            if actionToApply == "select":
                                out.append(inData[inData.index(line)])
                            if actionToApply == "update":
                                print "hi"
                except ValueError:
                    continue
    if flag:
        out = list(set(data)-set(out))
    return mainCount, out

#Tier Two Functions

def alterTable(input):
    try:
        useEnabled()  #Check that a database is selected
        tableName = input.split("ALTER TABLE ")[1]
        tableName = tableName.split(" ")[0].lower()
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            if "ADD" in input:  #Only checks for during first project
                with open(fileName, "a") as table:  #Use A to append data to end of the file
                    additionalString = input.split("ADD ")[1]
                    table.write(" | " + additionalString)
                    print "Table " + tableName + " modified."
        else:
            print "!Failed to alter table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to remove Table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def createDatabase(input):
    try:
        directory = input.split("CREATE DATABASE ")[1]  #Store the string after CREATE DATABASE
        if not os.path.exists(directory):  #Only create it if it doesn't exist
            os.makedirs(directory)
            print "Database " + directory + " created."
        else:
            print "!Failed to create database " + directory + " because it already exists"
    except IndexError:
        print "!No database name specified"

def createTable(input):
    try:
        useEnabled()  #Check that a database is selected
        subDirectory = input.split("CREATE TABLE ")[1]  #Get a string to use for the table name
        subDirectory = subDirectory.split(" (")[0].lower()
        fileName = os.path.join(workingDirectory, subDirectory)
        if not os.path.isfile(fileName):
            with open(fileName, "w") as table:  #Create a file to act as a table
                print "Table " + subDirectory + " created."
                if "(" in input:  #Check for the start of argument section
                    out = []  #Create a list for output to file
                    data = input.split("(", 1)[1]  #Remove (
                    data = data[:-1]  #Remove )
                    loopCount = data.count(",")  #Count the number of arguments
                    for x in range(loopCount + 1):
                        out.append(data.split(", ")[
                                       x])  #Import all arguments into list for printing and sorting later
                    table.write(" | ".join(out))  #Output the array to a file
        else:
            print "!Failed to create table " + subDirectory + " because it already exists"
    except IndexError:
        print "!Failed to remove Table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def deleteFrom(input):
    try:
        useEnabled()  #Check that a database is selected
        tableName = re.split("DELETE FROM ", input, flags=re.IGNORECASE)[1]  #Get a string to use for the table name
        tableName = tableName.split(" ")[0].lower()
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:
                data = table.readlines()
                itemToDelete = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                mainCount, out = where(itemToDelete, "delete", data)
                table.seek(0)
                table.truncate()
                for line in out:
                    table.write(line)
                if mainCount > 0:
                    print mainCount, " records deleted."
                else:
                    print "No records deleted."
        else:
            print "!Failed to alter table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to alter Table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def dropDatabase(input):
    try:
        directory = input.split("DROP DATABASE ")[1]  #Store the string after DROP DATABASE
        if os.path.exists(directory):  #Ensure that the database exists
            for toRemove in os.listdir(directory):  #Empty the folder, then remove the folder
                os.remove(directory + "/" + toRemove)
            os.rmdir(directory)
            print "Database " + directory + " deleted."
        else:
            print "!Failed to delete database " + directory + " because it does not exist"
    except IndexError:
        print "!No database name specified"

def dropTable(input):
    try:
        useEnabled()  #Check that a database is selected
        subDirectory = input.split("DROP TABLE ")[1].lower()  #Get string to use for the table name
        filePath = os.path.join(workingDirectory, subDirectory)
        if os.path.isfile(filePath):
            os.remove(filePath)
            print "Table " + subDirectory + " deleted."
        else:
            print "!Failed to delete Table " + subDirectory + " because it does not exist"
    except IndexError:
        print "!Failed to remove Table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def insertInto(input):
    try:
        useEnabled()  #Check that a database is selected
        tableName = input.split(" ")[2].lower()  #Get string to use for the table name
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            if "values" in input:  #Check for start of argument section
                with open(fileName, "a") as table:  #Open the file to insert into
                    out = []  #Create list for output to file
                    data = input.split("(", 1)[1]  #Remove (
                    data = data[:-1]  #Remove )
                    loopCount = data.count(",")  #Count the number of arguments
                    for x in range(loopCount + 1):
                        out.append(data.split(",")[x].lstrip())  #Import all arguments into list for printing and sorting later
                        if "\"" == out[x][0] or "\'" == out[x][0]:
                            out[x] = out[x][1:-1]
                    table.write("\n")
                    table.write(" | ".join(out))  #Output the array to a file
                    print "1 new record created."
            else:
                print "!Failed to insert into " + tableName + " beacause no arguments were given"
        else:
            print "!Failed to alter table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to insert into Table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def selectInput(input, inputString):
    try:
        tableVaribles = []
        fileNames = []
        joinType = ""

        useEnabled()  #Check that a database is selected
        (fileNames, tableVaribles, joinType) = selectHelper(fileNames, tableVaribles, joinType, inputString, input);
        output = ""

    #File Management

        with multiFileManager(fileNames, "r+") as tables:
            data = []
            dataArray = []

    #Selection
            if "JOIN" in inputString:
                for table in tables:
                    data = table.readlines()
                    dataArray.append(data)
                toJoinOn = re.split("on", input, flags=re.IGNORECASE)[1]
                counter, output = joinWhere(toJoinOn, tableVaribles, dataArray, joinType)
            #Using the WHERE to find the matches with all attributes
            elif "WHERE" in inputString:
                searchItem = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                counter = 0
                if len(tables) == 1: #typical where behavior
                    data = tables[0].readlines()
                    counter, output = where(searchItem, "select", data)
                else: #implicit inner join
                    for table in tables:
                        data = table.readlines()
                        dataArray.append(data)
                        counter += 1
                    counter, output = joinWhere(searchItem, tableVaribles, dataArray)

        #Printing
            if "SELECT *" in inputString:
                #Checks if the output is allocated from WHERE
                if not output == "":  
                    for line in output:
                        print line
                #If there is no restriction from WHERE print all
                else: 
                    for table in tables:
                        output += table.read()
                    print output
            #If doesnt want all of the attributes then trim down the output
            else:
                arguments = re.split("SELECT", input, flags=re.IGNORECASE)[1]
                attributes = re.split("FROM", arguments, flags=re.IGNORECASE)[0]
                attributes = attributes.split(",")
                if not output == "":  #Check if the output is allocated
                    lines = output
                else:
                    lines = table.readlines()
                    data = lines
                for line in lines:
                    out = []
                    for attribute in attributes:
                        attribute = attribute.strip()
                        colIndex = get_column(data)
                        if attribute in colIndex:
                            separatedLine = separate(line)
                            out.append(separatedLine[colIndex.index(attribute)].strip())
                    print " | ".join(out)
    except IndexError:
        print "!Failed to select because no table name is specified"
    except ValueError as err:
        print err.args[0]

def joinOn(input, inputString):
    toJoinOn = re.split("on", input, flags=re.IGNORECASE)[1]

    if "INNER" in inputString:
        return joinWhere(searchItem, tableVaribles, dataArray)
    if "OUTTER" in inputString:
        if "LEFT" in inputString:
            counter, out = where(toJoinOn, "SELECT", data)
            for line in data:
                for matchedData in out:
                    print "hi"
        elif "RIGHT" in inputString:
            counter, out = where(toJoinOn, "SELECT", data)

def updateFrom(input):
    try:
        useEnabled()  #Check that a database is selected
        tableName = re.split("UPDATE ", input, flags=re.IGNORECASE)[1]  #Get string to use for the table name
        tableName = re.split("SET", tableName, flags=re.IGNORECASE)[0].lower().strip()
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:
                data = table.readlines()
                itemToUpdate = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                setValue = re.split("SET ", input, flags=re.IGNORECASE)[1]
                setValue = re.split("WHERE ",setValue, flags=re.IGNORECASE)[0]
                mainCount, out = where(itemToUpdate, "update", data, setValue)
                table.seek(0)
                table.truncate()
                for line in out:
                    if not "\n" in line:
                        line += "\n"
                    table.write(line)
                if mainCount > 0:
                    print mainCount, " records updated."
                else:
                    print "No records updated."
        else:
            print "!Failed to alter table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to alter Table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def useDatabase(input):
    try:
        global globalScopeDirectory
        globalScopeDirectory = input.split("USE ")[1]  #Store the string after USE (with global scope)
        if os.path.exists(globalScopeDirectory):
            print "Using database " + globalScopeDirectory + " ."
        else:
            raise ValueError("!Failed to use database because it does not exist")
    except IndexError:
        print "!No database name specified"
    except ValueError as err:
        print err.args[0]

def selectHelper(fileNames, tableVaribles, joinType, inputString, input):
    tableArray = []
    tableLookup = {}
    tableNames = []

#TableName Parsing
    if "JOIN" in inputString:
        trimmedInput = re.split("FROM ", input, flags =re.IGNORECASE)[1]

        #The left table will always be [0]
        if "LEFT" in inputString:
            leftTableName = re.split("LEFT", trimmedInput, flags=re.IGNORECASE)[0].lower()
            rightTableName = re.split("JOIN ", trimmedInput, flags=re.IGNORECASE)[1].lower()
            rightTableName = re.split("ON", rightTableName, flags=re.IGNORECASE)[0].strip()
            leftTableName = re.split(" ", leftTableName, flags=re.IGNORECASE)[0].strip()
            rightTableName = re.split(" ", rightTableName, flags=re.IGNORECASE)[0].strip()
            tableArray.append(leftTableName)
            tableArray.append(rightTableName)
            joinType = 'left'

        elif "INNER" in inputString:
            leftTableName = re.split("INNER", trimmedInput, flags=re.IGNORECASE)[0].lower()
            rightTableName = re.split("JOIN ", trimmedInput, flags=re.IGNORECASE)[1].lower()
            rightTableName = re.split("ON", rightTableName, flags=re.IGNORECASE)[0].strip()
            leftTableName = re.split(" ", leftTableName, flags=re.IGNORECASE)[0].strip()
            rightTableName = re.split(" ", rightTableName, flags=re.IGNORECASE)[0].strip()
            tableArray.append(leftTableName)
            joinType = 'inner'
            tableArray.append(rightTableName)
        elif "RIGHT" in inputString: #Not currently implemented
            tableArray = re.split("RIGHT", trimmedInput, flags=re.IGNORECASE)[0].lower()
            tableArray = re.split("JOIN", trimmedInput, flags=re.IGNORECASE)[1].lower()
            joinType = 'right'
    elif "WHERE" in inputString:
        tableNames = re.split("FROM ", input, flags=re.IGNORECASE)[1].lower()
        tableNames = re.split("WHERE", tableNames, flags=re.IGNORECASE)[0]
    else: #if not join or where
        tableNames = re.split("FROM ", input, flags=re.IGNORECASE)[1].lower()  #Get the string to use for the table name
        if "," in tableNames:
            for table in re.split(", ", tableNames):
                tableArray.append(table)
        else:
            tableArray.append(tableNames)
    if " " in tableNames:
        tableNames = tableNames.strip("\r") #This removes any leftover returns
        tableNames = tableNames.strip() #This removes any whitespace
    if "," in tableNames:
        for table in re.split(", ", tableNames):
            table, tableVarible = re.split(" ", table, flags=re.IGNORECASE) #grab the left table name
            tableLookup[tableVarible] = table
            tableArray.append(table)
            tableVaribles.append(tableVarible)

        #TableName Parsing section for WHERE statements
        #https://stackoverflow.com/questions/7945182/opening-multiple-an-unspecified-number-of-files-at-once-and-ensuring-they-are
        
    #Loop through every tableName to make every file path
    for tableNames in tableArray:
        if tableName:
            fileNames.append(os.path.join(workingDirectory, tableName))

    return fileNames, tableVaribles, joinType

if __name__ == '__main__':
    main()