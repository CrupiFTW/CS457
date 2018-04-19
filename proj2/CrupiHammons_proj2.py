'''
Created by Alex Crupi and Chase Hammons, 3/20/18, version 2
'''
import os, re

globalScopeDirectory = ""
workingDirectory = ""


def main():
    try:
        while (True):
            input = ""
            while not ";" in input and not "--" in input:
                input += raw_input("\n enter a command \n")  #Read the input command from terminal

            input = input.split(";")[0]  #Remove ; from the input command
            input_string = str(input)  #Normalize the input command
            input_string = input_string.upper()

            if "--" in input:  #Pass the comments
                pass

            elif "ALTER TABLE" in inputUp:
                alterTable(input)

            elif "CREATE DATABASE" in inputUp:
                createDatabase(input)

            elif "CREATE TABLE" in inputUp:
                createTable(input)

            elif "DELETE FROM" in inputUp:
                deleteFrom(input)

            elif "DROP DATABASE" in inputUp:
                dropDatabase(input)

            elif "DROP TABLE" in inputUp:
                dropTable(input)

            elif "INSERT INTO" in inputUp:
                insertInto(input)

            elif "SELECT" in inputUp:
                selectInput(input, inputUp)

            elif "UPDATE" in inputUp:
                updateFrom(input)

            elif "USE" in inputUp:
                useDatabase(input)

            elif ".EXIT" in input:  #Exit database if specified before EOF
                print "All done"
                exit()

    except (EOFError, KeyboardInterrupt) as e:  #Exit script elegantly
        print "\n Connection to database terminated."

#Tier One Functions

def useEnabled():  #Catch the error when a database hasn't been enabled
    if globalScopeDirectory is "":
        raise ValueError("!Failed to use table because no database was selected")
    else:
        global workingDirectory
        workingDirectory = os.path.join(os.getcwd(), globalScopeDirectory)

def returnColIndex(data):
    colIndex = data[0].split(" | ")
    for x in range(len(colIndex)):
        colIndex[x] = colIndex[x].split(" ")[0]
    return colIndex

def splitLines(line):
    lineCheck = line.split(" | ")
    for x in range(len(lineCheck)):  #Check that each column has an item
        lineCheck[x] = lineCheck[x].split(" ")[0]
    return lineCheck

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

def selectInput(input, inputUp):
    try:
        useEnabled()  #Check that a database is selected
        tableName = re.split("FROM ", input, flags=re.IGNORECASE)[1].lower()  #Get string to use for the table name
        if "WHERE" in inputUp:
            tableName = re.split("WHERE", tableName, flags=re.IGNORECASE)[0]
            if " " in tableName:
                tableName = tableName.split(" ")[0]
        fileName = os.path.join(workingDirectory, tableName)
        output = ""
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:  #Since there should already be tables created, use r+
                if "WHERE" in inputUp: #Using the where to find the matches with all attributes
                    itemToFind = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                    data = table.readlines()
                    mainCount, output = where(itemToFind,"select",data)
                    for line in output:
                        print line
                if "SELECT *" in inputUp:
                    if not output == "": #Checks if the output is allocated
                        for line in output:
                            print line
                    else:
                        output = table.read()
                        print output
                else: #If doesnt want all attributes, trim down output
                    arguments = re.split("SELECT", input, flags=re.IGNORECASE)[1]
                    attributes = re.split("FROM", arguments, flags=re.IGNORECASE)[0]
                    attributes = attributes.split(",")
                    if not output == "":  #This checks if the output is allocated
                        lines = output
                    else:
                        lines = table.readlines()
                        data = lines
                    for line in lines:
                        out = []
                        for attribute in attributes:
                            attribute = attribute.strip()
                            colIndex = returnColIndex(data)
                            if attribute in colIndex:
                                splitLine = splitLines(line)
                                out.append(splitLine[colIndex.index(attribute)].strip())
                        print " | ".join(out)
        else:
            print "!Failed to query table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to select because no table name is specified"
    except ValueError as err:
        print err.args[0]

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

if __name__ == '__main__':
    main()
