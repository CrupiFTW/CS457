'''
Created by Alex Crupi and Chase Hammons, 3/8/18, version 2
'''
import os, re

globalScopeDirectory = ""
workingDirectory = ""


def main():
    try:
        while (True):
            command = ""
            while not ";" in command and not "--" in command:
                command += raw_input("\n enter a command \n")  # Read input from terminal

            command = command.split(";")[0]  # Remove ; from command
            commandUp = str(command)  # Normalize input
            commandUp = commandUp.upper()

            if "--" in command:  # Pass comments
                pass

            elif "CREATE DATABASE" in commandUp:
                createDatabase(command)

            elif "DROP DATABASE" in commandUp:
                dropDatabase(command)

            elif "USE" in commandUp:
                useDatabase(command)

            elif "CREATE TABLE" in commandUp:
                createTable(command)

            elif "DROP TABLE" in commandUp:
                dropTable(command)

            elif "DELETE FROM" in commandUp:
                deleteFrom(command)

            elif "SELECT" in commandUp:
                selectCommand(command, commandUp)

            elif "ALTER TABLE" in commandUp:
                alterTable(command)

            elif "INSERT INTO" in commandUp:
                insertInto(command)

            elif "UPDATE" in commandUp:
                updateFrom(command)

            elif ".EXIT" in command:  # Exit if specified before EOF
                print "All done"
                exit()

    except (EOFError, KeyboardInterrupt) as e:  # Exit elegantly
        print "\nConnection to database terminated."


def useEnabled():  # Catch when a database isn't enabled
    if globalScopeDirectory is "":
        raise ValueError("!Failed to use table because no database is selected")
    else:
        global workingDirectory
        workingDirectory = os.path.join(os.getcwd(), globalScopeDirectory)


def createDatabase(command):
    try:

        directory = command.split("CREATE DATABASE ")[1]  # Store the string after CREATE DATABASE
        if not os.path.exists(directory):  # Only create if it doesn't exist
            os.makedirs(directory)
            print "Database " + directory + " created."
        else:
            print "!Failed to create database " + directory + " because it already exists"

    except IndexError:
        print "!No database name specified"


def dropDatabase(command):
    try:
        directory = command.split("DROP DATABASE ")[1]  # Store the string after DROP DATABASE
        if os.path.exists(directory):  # Ensure database exists
            for toRemove in os.listdir(directory):  # Empty folder, then remove folder
                os.remove(directory + "/" + toRemove)
            os.rmdir(directory)
            print "Database " + directory + " deleted."
        else:
            print "!Failed to delete database " + directory + " because it does not exist"
    except IndexError:
        print "!No database name specified"


def useDatabase(command):
    try:
        global globalScopeDirectory
        globalScopeDirectory = command.split("USE ")[1]  # Store the string after USE (with 'global' scope)
        if os.path.exists(globalScopeDirectory):
            print "Using database " + globalScopeDirectory + " ."
        else:
            raise ValueError("!Failed to use database because it does not exist")
    except IndexError:
        print "!No database name specified"
    except ValueError as err:
        print err.args[0]


def createTable(command):
    try:
        useEnabled()  # Ensure database is selected
        subDirectory = command.split("CREATE TABLE ")[1]  # Get string to use for table name
        subDirectory = subDirectory.split(" (")[0].lower()
        fileName = os.path.join(workingDirectory, subDirectory)
        if not os.path.isfile(fileName):
            with open(fileName, "w") as table:  # Create file to act as table
                print "Table " + subDirectory + " created."
                if "(" in command:  # Check for start of argument section
                    out = []  # Create list for output to file
                    data = command.split("(", 1)[1]  # Remove (
                    data = data[:-1]  # Remove )
                    loopCount = data.count(",")  # Count the number of arguments
                    for x in range(loopCount + 1):
                        out.append(data.split(", ")[
                                       x])  # Import all arguments into list for printing and sorting later
                    table.write(" | ".join(out))  # Output the array to a file

        else:
            print "!Failed to create table " + subDirectory + " because it already exists"
    except IndexError:
        print "!Failed to remove Table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def dropTable(command):
    try:
        useEnabled()  # Ensure database is selected
        subDirectory = command.split("DROP TABLE ")[1].lower()  # Get string to use for table name
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


def selectCommand(command, commandUp):
    try:
        useEnabled()  # Ensure database is selected
        tableName = re.split("FROM ", command, flags=re.IGNORECASE)[1].lower()  # Get string to use for table name
        if "WHERE" in commandUp:
            tableName = re.split("WHERE", tableName, flags=re.IGNORECASE)[0]
            if " " in tableName:
                tableName = tableName.split(" ")[0]
        fileName = os.path.join(workingDirectory, tableName)
        output = ""

        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:  # Since there should already be tables created, use r+
                if "WHERE" in commandUp: #using the where to find the matches with all attributes
                    itemToFind = re.split("WHERE ", command, flags=re.IGNORECASE)[1]
                    data = table.readlines()
                    mainCount, output = where(itemToFind,"select",data)
                    for line in output:
                        print line

                if "SELECT *" in commandUp:
                    if not output == "": #checks if output is allocatioed
                        for line in output:
                            print line
                    else:
                        output = table.read()
                        print output

                else: #if doesnt want all attributes, trim down output

                    arguments = re.split("SELECT", command, flags=re.IGNORECASE)[1]
                    attributes = re.split("FROM", arguments, flags=re.IGNORECASE)[0]
                    attributes = attributes.split(",")


                    if not output == "":  # checks if output is allocated
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


def alterTable(command):
    try:
        useEnabled()  # Ensure database is selected
        tableName = command.split("ALTER TABLE ")[1]
        tableName = tableName.split(" ")[0].lower()
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            if "ADD" in command:  # Only checks for add at time of first project
                with open(fileName, "a") as table:  # Use A to append data to end of the file
                    additionalString = command.split("ADD ")[1]
                    table.write(" | " + additionalString)
                    print "Table " + tableName + " modified."
        else:
            print "!Failed to alter table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to remove Table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def insertInto(command):
    try:
        useEnabled()  # Ensure database is selected
        tableName = command.split(" ")[2].lower()  # Get string to use for table name
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            if "values" in command:  # Check for start of argument section
                with open(fileName, "a") as table:  # OPen file to insert into
                    out = []  # Create list for output to file
                    data = command.split("(", 1)[1]  # Remove (
                    data = data[:-1]  # Remove )
                    loopCount = data.count(",")  # Count the number of arguments
                    for x in range(loopCount + 1):
                        out.append(data.split(",")[x].lstrip())  # Import all arguments into list for printing and sorting later
                        if "\"" == out[x][0] or "\'" == out[x][0]:
                            out[x] = out[x][1:-1]
                    table.write("\n")
                    table.write(" | ".join(out))  # Output the array to a file
                    print "1 new record created."
            else:
                print "!Failed to insert into " + tableName + " beacause no arguments were given"
        else:
            print "!Failed to alter table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to insert into Table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def deleteFrom(command):
    try:
        useEnabled()  # Ensure database is selected
        tableName = re.split("DELETE FROM ", command, flags=re.IGNORECASE)[1]  # Get string to use for table name
        tableName = tableName.split(" ")[0].lower()
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:
                data = table.readlines()

                itemToDelete = re.split("WHERE ", command, flags=re.IGNORECASE)[1]
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



def updateFrom(command):
    try:
        useEnabled()  # Ensure database is selected
        commandUpper = command.upper()
        tableName = re.split("UPDATE ", command, flags=re.IGNORECASE)[1]  # Get string to use for table name
        tableName = re.split("SET", tableName, flags=re.IGNORECASE)[0].lower().strip()
        fileName = os.path.join(workingDirectory, tableName)
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:
                data = table.readlines()
                itemToUpdate = re.split("WHERE ", command, flags=re.IGNORECASE)[1]
                setValue = re.split("SET ", command, flags=re.IGNORECASE)[1]
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


def returnColIndex(data):
    colIndex = data[0].split(" | ")
    for x in range(len(colIndex)):
        colIndex[x] = colIndex[x].split(" ")[0]
    return colIndex


def where(argumentToFind, actionToApply, data, updateValue = ""):
    mainCount = 0
    colIndex = returnColIndex(data)
    colNames = colIndex
    inData = list(data)
    out = []
    flag = 0
    if "=" in argumentToFind:  # Figure out the operator for splitting command
        if "!=" in argumentToFind:
            relColumn = argumentToFind.split(" !=")[0]
            flag = 1
        else:
            relColumn = argumentToFind.split(" =")[0]

        argumentToFind = argumentToFind.split("= ")[1]
        if "\"" in argumentToFind or "\'" in argumentToFind:  # Cleanup var
            argumentToFind = argumentToFind[1:-1]
        for line in data:
            lineCheck = splitLines(line)
            if argumentToFind in lineCheck:
                colIndex = colNames.index(relColumn)
                lineIndex = lineCheck.index(argumentToFind)
                if lineIndex == colIndex:  # Check for proper column
                    if actionToApply == "delete":
                        del inData[inData.index(line)]  # Remove matched field
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

    elif ">" in argumentToFind:  # Figure out the operator for splitting command
        relColumn = argumentToFind.split(" >")[0]
        argumentToFind = argumentToFind.split("> ")[1]
        for line in data:  # Check each row
            lineCheck = line.split(" | ")
            for x in range(len(lineCheck)):  # Check each column item
                lineCheck[x] = lineCheck[x].split(" ")[0]
                try:
                    lineCheck[x] = float(lineCheck[x])  # Only check numeric fields
                    # lineCheck[x] = int(lineCheck[x])
                    if lineCheck[x] > float(argumentToFind):  # Match query
                        tempColIndex = colIndex.index(relColumn)
                        # print "x: ", x, " colIndex: ", colIndex, " mainIndex: ", data.index(line)
                        if x == tempColIndex:  # Check for proper column
                            if actionToApply == "delete":
                                del inData[inData.index(line)]  # Remove matched field
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


def splitLines(line):
    lineCheck = line.split(" | ")
    for x in range(len(lineCheck)):  # Check each column item
        lineCheck[x] = lineCheck[x].split(" ")[0]
    return lineCheck


if __name__ == '__main__':
    main()

