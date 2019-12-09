# -*- coding: utf-8 -*- 
import mysql.connector 
import re
import json

def clean(text):    #整理text函数
    """
    Remove any extra whitespace and line breaks as needed.  #根据需要删除任何多余的空格和换行符。
    """
    # Replace linebreaks with spaces  用空格替换换行符
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Remove any leeding or trailing whitespace
    text = text.strip()

    # Remove consecutive spaces    删除连续空格
    text = re.sub(" +", " ", text)
    
    text = re.sub('[^\x00-\x7F]+',' ', text)

    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def findFunctions(text):       # find all functions  找所有的函数
    return re.findall(r'(?<=(?<=int\s)|(?<=void\s)|(?<=string\s)|(?<=double\s)|(?<=float\s)|(?<=char\s)).*?(?=\s?\()', text)

def findClassName(text):       # find all classes   找所有的类
    temp = re.findall(r'(?<=class\s).*?(?=\s)',text)
    for eachTempClass in temp:
        if(eachTempClass[len(eachTempClass)-1] == ':' or eachTempClass[len(eachTempClass)-1] == '{'):
            eachTempClass = eachTempClass[:-1]
    return temp

def findExternalVariable(text):   # find all variables   找所有的变量
    return text

def cleanClassName(text):   # 找所有的变量

    for eachClass in text:

        if ':' in eachClass['className']:     #包括 :
            tempp = eachClass['className'].split(":")
            eachClass['className'] = tempp[0]
        elif '{' in eachClass['className']:    # 包括 {
            tempp = eachClass['className'].split("{")
            eachClass['className'] = tempp[0]

    return text

def cleanFunctionName(text):  #整理函数名

    for eachFunction in text:
        if ':' in eachFunction['functionName'][0]:     # 包括 :
            tempp = eachFunction['functionName'][0].split(":")
            eachFunction['functionName'] = tempp[0]
        elif '{' in eachFunction['functionName'][0]:   # 包括 {
            tempp = eachFunction['functionName'][0].split("{")
            eachFunction['functionName'] = tempp[0]
    return text

def cleanVariable(text):  #整理变量
    index = 0
    for eachVariable in text:
        if ':' in eachVariable['variableName'][0]:     # 包括 :
            temp = eachVariable['variableName'][0].split(':')
            eachVariable['variableName'][0] = temp[0]
        elif '=' in eachVariable['variableName'][0]:    # 包括 =
            temp = eachVariable['variableName'][0].split("=")
            eachVariable['variableName'][0] = temp[0]
        elif ',' in eachVariable['variableName'][0]:     # 包括 ,
            temp = eachVariable['variableName'][0].split(",")
            eachVariable['variableName'][0] = temp[0]
            print(index)
            #insert new item in the text list    在文本列表中插入新项
            for item in temp:
                if item == temp[0]:
                    continue
                else:
                    tempVariable = {}
                    tempVariable['lineNum'] = text[index]['lineNum']
                    tempVariable['variableName'] = [item]
                    tempVariable['variableType'] = text[index]['variableType']
                    text.insert(index+1,tempVariable)
                    index = index + 1
        index = index + 1
    return text
 

try: # 连接数据库
    dbcon = mysql.connector.connect(user='root',password='new-password',host='localhost',database='cdata')  
    cur = dbcon.cursor() 

    cur.execute("SELECT FileID, FileName FROM filetable")
    myresult = cur.fetchall()
    filepath = myresult[len(myresult)-1][1]      # 获取文件路径

    # dbcon.close()

    classArray = []
    functionArray = [] 
    variableArray = []
    externalVariableArray = []
    dataArray = []
   
    try:

    #**************************************get all functions****************************************
        # f = open("ce.cpp", "rb")
        # cfile = f.read().decode('utf-8')
        # print(findFunctions(cfile))
        # f.close()
        
    #**********************************************End**********************************************
    
    # ************************************* find class : 得到类****************************************
        sampleClass = {}

        sampleFunction = {}
        isFun = False
        stFunLine = 0

        sampleVariable = {}
        
        with open(filepath, 'rb') as fp:  #open file and seach every line : 打开文件并搜索每一行
            line = fp.readline()
            cdata = line
            cnt = 1
            while line:
                line = line.decode('utf-8')
                clean(line)
                
                if re.search(r"^class", line.strip()):      # if finds the first word 'class': 找到第一次单词 'class' 的时候
                    x = re.split("\s", line.strip(), 1)
                    sampleClass['className'] = x[1]
                    sampleClass['stLine'] = cnt

                elif re.search(r"^};", line.strip()):     # when finds the '};'   :找到 '};'  的时候
                    sampleClass['endLine'] = cnt
                    classArray.append(sampleClass)
                    sampleClass = {}
                # below is for function   跟函数有关
                elif re.search(r'(?<=(?<=int\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["int"]:
                    sampleFunction['functionName'] = re.findall(r'(?<=(?<=int\s)).*?(?=\s?\()', line)
                    sampleFunction['functionType'] = "int"
                    sampleFunction['functionStLine'] = cnt
                    sampleFunction['functionEndLine'] = 0
                    functionArray.append(sampleFunction)
                    sampleFunction = {}
                    isFun = True
                    stFunLine = cnt
                elif re.search(r'(?<=(?<=void\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["void"]:
                    sampleFunction['functionName'] = re.findall(r'(?<=(?<=void\s)).*?(?=\s?\()', line)
                    sampleFunction['functionType'] = "void"
                    sampleFunction['functionStLine'] = cnt
                    sampleFunction['functionEndLine'] = 0
                    functionArray.append(sampleFunction)
                    sampleFunction = {}
                    isFun = True
                    stFunLine = cnt
                elif re.search(r'(?<=(?<=string\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["string"]:
                    sampleFunction['functionName'] = re.findall(r'(?<=(?<=string\s)).*?(?=\s?\()', line)
                    sampleFunction['functionType'] = "string"
                    sampleFunction['functionStLine'] = cnt
                    sampleFunction['functionEndLine'] = 0
                    functionArray.append(sampleFunction)
                    sampleFunction = {}
                    isFun = True
                    stFunLine = cnt
                elif re.search(r'(?<=(?<=double\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["double"]:
                    sampleFunction['functionName'] = re.findall(r'(?<=(?<=double\s)).*?(?=\s?\()', line)
                    sampleFunction['functionType'] = "double"
                    sampleFunction['functionStLine'] = cnt
                    sampleFunction['functionEndLine'] = 0
                    functionArray.append(sampleFunction)
                    sampleFunction = {}
                    isFun = True
                    stFunLine = cnt
                elif re.search(r'(?<=(?<=float\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["float"]:
                    sampleFunction['functionName'] = re.findall(r'(?<=(?<=float\s)).*?(?=\s?\()', line)
                    sampleFunction['functionType'] = "float"
                    sampleFunction['functionStLine'] = cnt
                    sampleFunction['functionEndLine'] = 0
                    functionArray.append(sampleFunction)
                    sampleFunction = {}
                    isFun = True
                    stFunLine = cnt
                elif re.search(r'(?<=(?<=char\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["char"]:
                    sampleFunction['functionName'] = re.findall(r'(?<=(?<=char\s)).*?(?=\s?\()', line)
                    sampleFunction['functionType'] = "char"
                    sampleFunction['functionStLine'] = cnt
                    sampleFunction['functionEndLine'] = 0
                    functionArray.append(sampleFunction)
                    sampleFunction = {}
                    isFun = True
                    stFunLine = cnt
                elif '}' in line and isFun == True and cnt > stFunLine:
                    isFun = False
                    functionArray[len(functionArray)-1]['functionEndLine'] = cnt
                #below is for variable  跟变量有关
                elif re.search(r'(?<=(?<=int\s)).*?(?=\s?\;)', line) and '(' not in line:
                    sampleVariable['lineNum'] = cnt
                    sampleVariable['variableName'] = re.findall(r'(?<=(?<=int\s)).*?(?=\s?\;)', line)
                    sampleVariable['variableType'] = 'int'
                    variableArray.append(sampleVariable)
                    sampleVariable = {}
                elif re.search(r'(?<=(?<=string\s)).*?(?=\s?\;)', line) and '(' not in line:
                    sampleVariable['lineNum'] = cnt
                    sampleVariable['variableName'] = re.findall(r'(?<=(?<=string\s)).*?(?=\s?\;)', line)
                    sampleVariable['variableType'] = 'string'
                    variableArray.append(sampleVariable)
                    sampleVariable = {}
                elif re.search(r'(?<=(?<=double\s)).*?(?=\s?\;)', line) and '(' not in line:
                    sampleVariable['lineNum'] = cnt
                    sampleVariable['variableName'] = re.findall(r'(?<=(?<=double\s)).*?(?=\s?\;)', line)
                    sampleVariable['variableType'] = 'double'
                    variableArray.append(sampleVariable)
                    sampleVariable = {}
                elif re.search(r'(?<=(?<=float\s)).*?(?=\s?\;)', line) and '(' not in line:
                    sampleVariable['lineNum'] = cnt
                    sampleVariable['variableName'] = re.findall(r'(?<=(?<=float\s)).*?(?=\s?\;)', line)
                    sampleVariable['variableType'] = 'float'
                    variableArray.append(sampleVariable)
                    sampleVariable = {}
                elif re.search(r'(?<=(?<=char\s)).*?(?=\s?\;)', line) and '(' not in line:
                    sampleVariable['lineNum'] = cnt
                    sampleVariable['variableName'] = re.findall(r'(?<=(?<=char\s)).*?(?=\s?\;)', line)
                    sampleVariable['variableType'] = 'char'
                    variableArray.append(sampleVariable)
                    sampleVariable = {}

                line = fp.readline()
                cnt += 1
            #保存在数据库中   
            classData = cleanClassName(classArray)   #得到类
            classNo = 1
            for eachClass in classData:
                valArray = [filepath, classNo, eachClass['className']]
                val = (tuple(valArray))
                sql = "INSERT INTO `ClassTable` (`FileID`, `ClassNo`, `ClassName`) VALUES (%s, %s, %s)" # INSERT INTO ClassTable
                cur.execute(sql, val)
                dbcon.commit()
                classNo = classNo+1

            functionArray = cleanFunctionName(functionArray) # 函数
            functionNo = 1  # save in the database 
            for each in functionArray:
                valArray = [filepath, functionNo, each['functionName'][0], each['functionType']]
                val = (tuple(valArray))
                sql = "INSERT INTO `FunctionTable` (`FileID`, `FuncNo`, `FuncName`, `ReturnType`) VALUES (%s, %s, %s, %s)" # INSERT INTO FunctionTable
                cur.execute(sql, val)
                dbcon.commit()
                functionNo = functionNo+1

            variableArray = cleanVariable(variableArray)  # 变量
            variableNo = 1   #save in the database
            for each in variableArray:
                valArray = [filepath, each['variableName'][0], each['variableType'], variableNo]
                val = (tuple(valArray))
                sql = "INSERT INTO `VariableTable` (`FileID`, `VariableName`, `ReturnType`,`VariableNo`) VALUES (%s, %s, %s, %s)" # INSERT INTO VariableTable
                cur.execute(sql, val)
                dbcon.commit()
                variableNo = variableNo+1
            # get external variable    #  外部变量
            lineCnt = []
            for i in range(0,cnt):
                lineCnt.append(i)
            for each in classArray:
                for i in range(each['stLine'],each['endLine']):
                    lineCnt[i] = "10000"
            for each in functionArray:
                for i in range(each['functionStLine'],each['functionEndLine']):
                    lineCnt[i] = '10000'
            for each in variableArray:
                if lineCnt[each['lineNum']] != '10000':
                    externalVariableArray.append(each)
            externalVariableNo = 1
            for each in externalVariableArray:
                valArray = [externalVariableNo, filepath, each['variableName'][0], each['variableType']]
                val = (tuple(valArray))
                sql = "INSERT INTO `ExternalVariableTable` (`VariableNo`, `FileID`, `VariableName`, `ReturnType`) VALUES (%s, %s, %s, %s)" # INSERT INTO ExternalVariableTable
                cur.execute(sql, val)
                dbcon.commit()
                externalVariableNo = externalVariableNo+1

    #****************************************End****************************************************

    except IOError:
        print("File not found or path is incorrect")
    finally:
        dbcon.close()
        print("exit")

except:
    print("database connection error")




