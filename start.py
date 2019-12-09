# -*- coding: utf-8 -*- 
import mysql.connector 
import re
import json
import sys

# This function cleans the comment "//", spaces at the beginning and at the end of the line
# Parameter line represent the each line of the c/cpp file
def clean(line):
    # First, clean the comment.
    result = line.split('//')[0] 
    result = result.split('/*')[0]
    result = result.split('*/')
    if len(result) > 1:
        result = result[1]
    else:
        result = result[0]
    # Then, clean the spaces
    result = result.strip()
    return result
# This function cleans the unnecessary letters from the class name
# clean ":" and "{"
def cleanName(name):   # 找所有的变量
    name = name.split(':')[0]
    name = name.split('{')[0].strip()
    return name
# Get variables in the line
def getVariables(line, lineNum, markedArea):
    ret = [] # array of variables, the return value

    line = line.split(';')[0] # Remove ";" letter
    x = line.split(',')
    # if the line contains "::", it means the line is related to class, it's the class variable
    # skip this case
    if len(x[0].strip().split()) < 2 or "::" in line:
        return ret
    for idx, str1 in enumerate(x):
        y = str1.strip().split('=')
        result = {} # save one variable
        
        # extract the type of variable
        str_first = x[0].strip().split("=")[0].strip().split()
        result['type'] = ""
        for i in range(len(str_first) - 1):
            result['type'] = result['type'] + str_first[i] + " "
        result['type'] = result['type'].strip()
        # the line number of the variable
        result['stLine'] = lineNum 
        # extract the variable name
        if idx == 0:
            result['name'] = str_first[len(str_first) - 1].split('=')[0]
        else:
            result['name'] = y[0].strip()
        # if this section contains the 'using' or 'return', it isn't the variable, so skip
        if 'return' in result['type'] or 'using' in result['type']:
            return ret
        # if this section contains the '"', it is the string, so skip
        if '"' in result['type'] or '"' in result['name']:
            continue    

        result['parent']     = 'none'
        result['parentName'] = "none"
        result['isConst']    = "No"
        result['isInput']    = "No"
        result['markedArea'] = markedArea

        ret.append(result)
    return ret
# get const values
def getConst(line, lineNum):
    line = line.split('#define')[1]
    result = {}
    result['name'] = line.strip().split()[0]
    result['type'] = 'define'
    result['stLine'] = lineNum
    result['parent'] = 'none'
    result['parentName'] = "none"
    result['isConst']   = "Yes"
    result['isInput']   = "No"

    ret = []
    ret.append(result)
    return ret
# get function parameters
def getFuncParams(line, lineNum, funcInfo):
    ret = []
    # Remove function name, type and bracket, so only parameters are left
    line = line.split(funcInfo['name'])[1].split('(')[1].split(')')[0]
    # Get each params as they are separated by comma
    params = line.split(',')
    for idx, param in enumerate(params):
        temp = param.strip().split('=')[0]
        result = {}
        result['type'] = ""
        temp = temp.strip().split()
        if len(temp) < 2:
            return ret
        for i in range(len(temp) - 1):
            result['type'] = result['type'] + temp[i] + " "
        result['type'] = result['type'].strip()    
        result['name'] = temp[len(temp) - 1]
        result['stLine'] = lineNum
        result['parent'] = 'func'
        result['parentName'] = funcInfo['name']
        if funcInfo['parent'] == 'class':
            result['parent'] = 'class-func'
            result['parentName'] = funcInfo['name'] + '&' + funcInfo['parentName']
        
        result['isConst']   = "No"
        result['isInput']   = "Yes"
        result['markedArea'] = funcInfo['markedArea']

        ret.append(result)
    return ret
# get All classes
def getAllClasses(lines):
    lineNum = 1
    sampleClass = {}

    isComment = False

    classArray   = []
    friendArray = []

    for line in lines:
        line = line.decode('utf-8')
        # Check if it's comment
        if "*/" in line:
            isComment = False
        if isComment == True:
            continue
        if "/*" in line:
            isComment = True

        line = clean(line)
        # if finds the first word 'class': 找到第一次单词 'class' 的时候
        if re.search(r"^class", line):
            x = re.split("\s", line, 1)
            sampleClass['name'] = cleanName(x[1])
            sampleClass['stLine'] = lineNum
            
        # when finds the '};'   :找到 '};'  的时候
        elif re.search(r"^};", line.strip()):
            sampleClass['endLine'] = lineNum
            classArray.append(sampleClass)
            sampleClass = {}
        # search friend functions and update their info
        if re.search(r"^friend", line):
            newFriend = {}
            x = line.split('(')[0].split()
            newFriend['name'] = x[len(x) - 1]
            newFriend['parentName'] = sampleClass['name']
            friendArray.append(newFriend)
        lineNum = lineNum + 1

    ret = {}
    ret['class']  = classArray
    ret['friend'] = friendArray

    return ret
# generate a new function
def newFunction(friendArray, func_name, func_type, stLine, parent, parentName, isPrivate, isPublic, isProtected):
    sampleFunction = {}
    
    sampleFunction['name'] = func_name
    sampleFunction['type'] = func_type
    sampleFunction['stLine'] = stLine
    sampleFunction['endLine'] = 0
    sampleFunction['parent'] = parent
    sampleFunction['parentName'] = parentName
    sampleFunction['body'] = ""
    sampleFunction['markedArea'] = 'private'

    # This function is class function, set parent and parent name
    if '::' in sampleFunction['name']:
        sampleFunction['parent'] = "class"
        temp = sampleFunction['name'].split("::")[0].split()
        sampleFunction['name'] = sampleFunction['name'].split("::")[1]
        if len(temp) == 1:
            sampleFunction['parentName'] = temp[0].strip()
        else:
            sampleFunction['parentName'] = temp[1].strip()
    sampleFunction['name'] = cleanName(sampleFunction['name'])
    if isPrivate:
        sampleFunction['markedArea'] = 'private'
    if isPublic:
        sampleFunction['markedArea'] = 'public'
    if isProtected:
        sampleFunction['markedArea'] = 'protected'
    
    # Check if this is a friend function
    for eachFriend in friendArray:
        if eachFriend['name'] in sampleFunction['name']:
            sampleFunction['parent'] = 'class'
            sampleFunction['parentName'] = eachFriend['parentName']
    return sampleFunction
# get All functions and variables    
def getAllFunctionsVars(lines, classArray, friendArray):
    # Add class names to variable types
    variableTypes = ['int', 'char', 'void', 'string', 'double', 'float', 'bool']
    for eachClass in classArray:
        variableTypes.append(eachClass['name'])

    variableArray = []
    functionArray = []

    # Shows if the current line is inside the comment, or not
    isComment = False
    # Shows if the current line is insdie the function, or not
    isFun = False
    # The start line of the function
    stFunLine = 0
    # Shows the current marked area
    isPrivate   = False
    isPublic    = False
    isProtected = False

    lineNum = 1

    for line in lines:
        line = line.decode('utf-8')
        
        if isComment == True and "*/" not in line:
            continue
        if "/*" in line:
            isComment = True
        if "*/" in line:
            isComment = False
       
        line = clean(line)

        if "private" in line:
            isPrivate   = True
            isPublic    = False
            isProtected = False
        if "public" in line:
            isPrivate   = False
            isPublic    = True
            isProtected = False
        if "protected" in line:
            isPrivate   = False
            isPublic    = False
            isProtected = True    
        
        # below is for function   跟函数有关
        # Constructor, Desructor are missing
        for eachClass in classArray:
            if lineNum > eachClass['stLine'] and lineNum < eachClass['endLine']:
                if re.match(r'^\w+ *\(.*\)', line) and eachClass['name'] in line: # Constructor
                    newFunc = newFunction(friendArray, eachClass['name'], 'null', lineNum, "class", eachClass['name'], isPrivate, isPublic, isProtected)
                    functionArray.append(newFunc)
                    isFun = True
                    stFunLine = lineNum

                    variableArray = variableArray + getFuncParams(line, lineNum, newFunc)
                elif re.match(r'^`\w+ *\(.*\)$', line) and eachClass['name'] in line: # Destructor
                    newFunc = newFunction(friendArray, '~' + eachClass['name'], 'null', lineNum, "class", eachClass['name'], isPrivate, isPublic, isProtected)
                    functionArray.append(newFunc)
                    isFun = True
                    stFunLine = lineNum

                    variableArray = variableArray + getFuncParams(line, lineNum, newFunc)
        # Normal Functions
        for variableType in variableTypes:
            if re.search('(?<=(?<=' + variableType +'\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == [variableType] and ";" not in line:
                newFunc = newFunction(friendArray, re.findall(r'(?<=(?<=' + variableType +'\s)).*?(?=\s?\()', line)[0], variableType, lineNum, "none", "none", isPrivate, isPublic, isProtected)
                functionArray.append(newFunc)
                isFun = True
                stFunLine = lineNum

                variableArray = variableArray + getFuncParams(line, lineNum, newFunc)
        # Check the end of the function
        if '}' in line and isFun == True and lineNum >= stFunLine:
            isFun = False
            functionArray[len(functionArray)-1]['endLine'] = lineNum
            functionArray[len(functionArray)-1]['body'] = functionArray[len(functionArray)-1]['body'][1:] 
        if isFun == True and functionArray[len(functionArray)-1]['stLine'] < lineNum:
            functionArray[len(functionArray)-1]['body'] = functionArray[len(functionArray)-1]['body'] + line
        #below is for variable  跟变量有关
        if re.match(r'[a-zA-Z0-9_*]+\s[a-zA-Z0-9_*]+.*;', line) and '(' not in line:
            variableArray = variableArray + getVariables(line, lineNum, 'private' if isPrivate else ('public' if isPublic else ( 'protected' if isProtected else 'null' )))
        elif "#define" in line:
            variableArray = variableArray + getConst(line, lineNum)
            
        lineNum += 1
    ret = {}
    ret['func'] = functionArray
    ret['var']  = variableArray

    return ret

# Main Part    
try: # 连接数据库
    dbcon = mysql.connector.connect(user='root',password='new-password',host='localhost',database='C++/Cdata')  
    cur = dbcon.cursor() 

    cur.execute("SELECT FileID, FileName FROM FileTable")
    files = cur.fetchall()

    for f_idx in range(len(files)):
        classArray    = []
        functionArray = [] 
        variableArray = []
        friendArray = []
        try:

        # ************************************* find class : 得到类****************************************
            
            #open file and seach every line : 打开文件并搜索每一行
            with open(files[f_idx][1], 'rb') as fp:
                lines = fp.readlines()
                
                # Get all classes and add their names to variable types
                temp = getAllClasses(lines)
                classArray = temp['class']
                friendArray = temp['friend']

                # Search functions and variables with variable types
                # variableTypes contains the default types and Class Names
                func_vars = getAllFunctionsVars(lines, classArray, friendArray)
                functionArray    = func_vars['func']
                variableArray    = func_vars['var']
                
                # Determine the parent of function
                for idx, eachFunc in enumerate(functionArray):
                    for eachClass in classArray:
                        if eachFunc['stLine'] >= eachClass['stLine'] and eachFunc['stLine'] <= eachClass['endLine'] and eachFunc['parent'] == "none":
                            functionArray[idx]['parent']     = 'class'
                            functionArray[idx]['parentName'] = eachClass['name']
                # Save in the database 
                funcNo = 1
                funcClassNo = 1
                
                for eachFunc in functionArray:
                    if eachFunc['parent'] == 'class':
                        sql_value = [files[f_idx][0], eachFunc['parentName'], eachFunc['name'], funcClassNo, eachFunc['type'], eachFunc['markedArea'], eachFunc['body']]
                        val = (tuple(sql_value))
                        sql = "INSERT INTO `FuncClassTable` (`FileID`, `ClassName`, `FuncName`, `FuncNo`, `ReturnType`, `MarkedArea`, `FuncBody`) VALUES (%s, %s, %s, %s, %s, %s, %s)" # INSERT INTO FuncClassTable
                        cur.execute(sql, val)
                        funcClassNo = funcClassNo + 1
                    else:  
                        sql_value = [files[f_idx][0], eachFunc['name'], funcNo, eachFunc['type'], eachFunc['body']]
                        val = (tuple(sql_value))
                        sql = "INSERT INTO `FuncInfoTable` (`FileID`, `FuncName`, `FuncNo`, `ReturnType`, `FuncBody`) VALUES (%s, %s, %s, %s, %s)" # INSERT INTO FuncInfoTable
                        cur.execute(sql, val)
                        funcNo = funcNo + 1
                    dbcon.commit()

                # Determine parent of Variable
                for idx, each in enumerate(variableArray):
                    # Check if variable belongs to function
                    for eachFunc in functionArray:
                        if each['stLine'] >= eachFunc['stLine'] and each['stLine'] <= eachFunc['endLine']:
                            # if variable belong to a function, then check if the func belongs to a class or not
                            if eachFunc['parent'] == "none":
                                variableArray[idx]['parent']     = 'func'
                                variableArray[idx]['parentName'] = eachFunc['name']
                            else:
                                variableArray[idx]['parent']     = 'class-func'
                                variableArray[idx]['parentName'] = eachFunc['name'] + "&" + eachFunc['parentName']
                    # Check if variable belongs to function unless it's belong to a function
                    for eachClass in classArray:
                        if each['stLine'] >= eachClass['stLine'] and each['stLine'] <= eachClass['endLine'] and each['parent'] == 'none':
                            variableArray[idx]['parent']     = 'class'
                            variableArray[idx]['parentName'] = eachClass['name']
                # Save Varialbes to Database
                classVariableNo     = 1
                funcVariableNo      = 1
                funcClassVariableNo = 1
                VariableNo          = 1

                for each in variableArray:
                    if each['parent'] == 'class':
                        valArray = [files[f_idx][0], classVariableNo, each['parentName'], each['name'], each['type'], each['markedArea']]
                        val = (tuple(valArray))
                        sql = "INSERT INTO `ClassVariable` (`FileID`, `VariableNo`, `ClassName`, `VariableName`, `VariableType`, `MarkedArea`) VALUES (%s, %s, %s, %s, %s, %s)" # INSERT INTO ClassVariable
                        cur.execute(sql, val)
                        classVariableNo = classVariableNo + 1
                    elif each['parent'] ==  'func':
                        valArray = [files[f_idx][0], funcVariableNo, each['type'], each['name'],  each['parentName'], each['isInput']]
                        val = (tuple(valArray))
                        sql = "INSERT INTO `FuncVariable` (`FileID`, `VariableNo`, `VariableType`, `VariableName`, `FuncName`, `IsInput`) VALUES (%s, %s, %s, %s, %s, %s)" # INSERT INTO FuncVariable
                        cur.execute(sql, val)
                        funcVariableNo = funcVariableNo + 1
                    elif each['parent'] ==  'class-func':
                        funcName = each['parentName'].split('&')[0]
                        className = each['parentName'].split('&')[1]
                        valArray = [files[f_idx][0], funcClassVariableNo, className, funcName, each['name'], each['type'], each['markedArea'], each['isInput']]
                        val = (tuple(valArray))
                        sql = "INSERT INTO `FuncClassVariable` (`FileID`, `VariableNo`, `ClassName`, `FuncName`, `VariableName`, `VariableType`, `MarkedArea`, `IsInput`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" # INSERT INTO FuncClassVariable
                        cur.execute(sql, val)
                        funcClassVariableNo = funcClassVariableNo + 1
                    else:
                        valArray = [files[f_idx][0], VariableNo, each['type'], each['name'], each['isConst']]
                        val = (tuple(valArray))
                        sql = "INSERT INTO `VariableTable` (`FileID`, `VariableNo`, `VariableType`, `VariableName`, `IsConst`) VALUES (%s, %s, %s, %s, %s)" # INSERT INTO VariableTable
                        cur.execute(sql, val)
                        VariableNo = VariableNo + 1    
                    dbcon.commit()
            
        #****************************************End****************************************************

        except IOError:
            print("File not found or path is incorrect")
        finally:
            fp.close()

    print("Done")
    dbcon.close()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_lineno)
    print(str(e))




