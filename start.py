# -*- coding: utf-8 -*- 
import mysql.connector 
import re
import json
import sys

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

def cleanClassName(text):   # 找所有的变量

    for eachClass in text:

        if ':' in eachClass['name']:     #包括 :
            tempp = eachClass['name'].split(":")
            eachClass['name'] = tempp[0]
        elif '{' in eachClass['name']:    # 包括 {
            tempp = eachClass['name'].split("{")
            eachClass['name'] = tempp[0]

    return text

def cleanname(text):  #整理函数名

    for eachFunction in text:
        if ':' in eachFunction['name']:     # 包括 :
            tempp = eachFunction['name'].split(":")
            eachFunction['name'] = tempp[0]
        elif '{' in eachFunction['name']:   # 包括 {
            tempp = eachFunction['name'].split("{")
            eachFunction['name'] = tempp[0]
    return text

def cleanVariable(text):  #整理变量
    index = 0
    for eachVariable in text:
        if ':' in eachVariable['name']:     # 包括 :
            temp = eachVariable['name'].split(':')
            eachVariable['name'] = temp[0]
        elif '=' in eachVariable['name']:    # 包括 =
            temp = eachVariable['name'].split("=")
            eachVariable['name'] = temp[0]
        elif ',' in eachVariable['name']:     # 包括 ,
            temp = eachVariable['name'].split(",")
            eachVariable['name'] = temp[0]
            (index)
            #insert new item in the text list    在文本列表中插入新项
            for item in temp:
                if item == temp[0]:
                    continue
                else:
                    tempVariable = {}
                    tempVariable['stLine'] = text[index]['stLine']
                    tempVariable['name'] = [item]
                    tempVariable['type'] = text[index]['type']
                    text.insert(index+1,tempVariable)
                    index = index + 1
        index = index + 1
    return text

def getVariables(line, lineNum):
    ret = []

    line = line.split(';')[0]
    x = line.split(',')
    if len(x[0].strip().split()) < 2 or "::" in line:
        return ret
    for idx, str1 in enumerate(x):
        y = str1.strip().split('=')
        result = {}
        
        str_first = x[0].strip().split("=")[0].strip().split()
        result['type'] = ""
        for i in range(len(str_first) - 1):
            result['type'] = result['type'] + str_first[i]
        
        result['stLine'] = lineNum
        if idx == 0:
            result['name'] = str_first[len(str_first) - 1].split('=')[0]
        else:
            result['name'] = y[0].strip()
        
        if 'return' in result['type'] or 'using' in result['type']:
            return ret

        if '"' in result['type'] or '"' in result['name']:
            continue    
        result['parent'] = 'none'
        result['parentName'] = "none"
        result['isConst']   = "No"
        ret.append(result)
    return ret

def getConst(line, lineNum):
    line = line.split('#define')[1]
    result = {}
    result['name'] = line.strip().split()[0]
    result['type'] = 'define'
    result['stLine'] = lineNum
    result['parent'] = 'none'
    result['parentName'] = "none"
    result['isConst']   = "Yes"
    ret = []
    ret.append(result)
    return ret

try: # 连接数据库
    dbcon = mysql.connector.connect(user='root',password='new-password',host='localhost',database='C++/Cdata')  
    cur = dbcon.cursor() 

    cur.execute("SELECT FileID, FileName FROM FileTable")
    files = cur.fetchall()

    for f_idx in range(len(files)):
        classArray = []
        functionArray = [] 
        variableArray = []
        externalVariableArray = []
        dataArray = []
        try:

        # ************************************* find class : 得到类****************************************
            sampleClass = {}

            sampleFunction = {}
            isFun = False
            stFunLine = 0

            sampleVariable = {}
            
            with open(files[f_idx][1], 'rb') as fp:  #open file and seach every line : 打开文件并搜索每一行
                line = fp.readline()
                cdata = line
                cnt = 1
                while line:
                    line = line.decode('utf-8')
                    clean(line)
                    
                    if re.search(r"^class", line.strip()):      # if finds the first word 'class': 找到第一次单词 'class' 的时候
                        x = re.split("\s", line.strip(), 1)
                        sampleClass['name'] = x[1]
                        sampleClass['stLine'] = cnt

                    elif re.search(r"^};", line.strip()):     # when finds the '};'   :找到 '};'  的时候
                        sampleClass['endLine'] = cnt
                        classArray.append(sampleClass)
                        sampleClass = {}
                    # below is for function   跟函数有关
                    elif re.search(r'(?<=(?<=int\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["int"]:
                        sampleFunction['name'] = re.findall(r'(?<=(?<=int\s)).*?(?=\s?\()', line)[0]
                        sampleFunction['type'] = "int"
                        sampleFunction['stLine'] = cnt
                        sampleFunction['endLine'] = 0
                        sampleFunction['parent'] = "none"
                        sampleFunction['parentName'] = "none"
                        functionArray.append(sampleFunction)
                        sampleFunction = {}
                        isFun = True
                        stFunLine = cnt
                    elif re.search(r'(?<=(?<=void\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["void"]:
                        sampleFunction['name'] = re.findall(r'(?<=(?<=void\s)).*?(?=\s?\()', line)[0]
                        sampleFunction['type'] = "void"
                        sampleFunction['stLine'] = cnt
                        sampleFunction['endLine'] = 0
                        sampleFunction['parent'] = "none"
                        sampleFunction['parentName'] = "none"
                        functionArray.append(sampleFunction)
                        sampleFunction = {}
                        isFun = True
                        stFunLine = cnt
                    elif re.search(r'(?<=(?<=string\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["string"]:
                        sampleFunction['name'] = re.findall(r'(?<=(?<=string\s)).*?(?=\s?\()', line)[0]
                        sampleFunction['type'] = "string"
                        sampleFunction['stLine'] = cnt
                        sampleFunction['endLine'] = 0
                        sampleFunction['parent'] = "none"
                        sampleFunction['parentName'] = "none"
                        functionArray.append(sampleFunction)
                        sampleFunction = {}
                        isFun = True
                        stFunLine = cnt
                    elif re.search(r'(?<=(?<=double\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["double"]:
                        sampleFunction['name'] = re.findall(r'(?<=(?<=double\s)).*?(?=\s?\()', line)[0]
                        sampleFunction['type'] = "double"
                        sampleFunction['stLine'] = cnt
                        sampleFunction['endLine'] = 0
                        sampleFunction['parent'] = "none"
                        sampleFunction['parentName'] = "none"
                        functionArray.append(sampleFunction)
                        sampleFunction = {}
                        isFun = True
                        stFunLine = cnt
                    elif re.search(r'(?<=(?<=float\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["float"]:
                        sampleFunction['name'] = re.findall(r'(?<=(?<=float\s)).*?(?=\s?\()', line)[0]
                        sampleFunction['type'] = "float"
                        sampleFunction['stLine'] = cnt
                        sampleFunction['endLine'] = 0
                        sampleFunction['parent'] = "none"
                        sampleFunction['parentName'] = "none"
                        functionArray.append(sampleFunction)
                        sampleFunction = {}
                        isFun = True
                        stFunLine = cnt
                    elif re.search(r'(?<=(?<=char\s)).*?(?=\s?\()', line) and re.findall(r"^\w+",line.strip()) == ["char"]:
                        sampleFunction['name'] = re.findall(r'(?<=(?<=char\s)).*?(?=\s?\()', line)[0]
                        sampleFunction['type'] = "char"
                        sampleFunction['stLine'] = cnt
                        sampleFunction['endLine'] = 0
                        sampleFunction['parent'] = "none"
                        sampleFunction['parentName'] = "none"
                        functionArray.append(sampleFunction)
                        sampleFunction = {}
                        isFun = True
                        stFunLine = cnt
                    elif '}' in line and isFun == True and cnt > stFunLine:
                        isFun = False
                        functionArray[len(functionArray)-1]['endLine'] = cnt
                    #below is for variable  跟变量有关
                    elif re.match(r'[ \t]*[a-zA-Z0-9_*]+\s[a-zA-Z0-9_*]+.*;', line) and '(' not in line:
                        variableArray = variableArray + getVariables(line, cnt)
                    elif "#define" in line:
                        variableArray = variableArray + getConst(line, cnt)
                        
                    line = fp.readline()
                    cnt += 1
                #保存在数据库中   
                classArray = cleanClassName(classArray)   #得到类
                functionArray = cleanname(functionArray) # 函数
                
                # Determine the parent of function
                for idx, eachFunc in enumerate(functionArray):
                    for eachClass in classArray:
                        if eachFunc['stLine'] > eachClass['stLine'] and eachFunc['stLine'] < eachClass['endLine']:
                            functionArray[idx]['parent'] = 'class'
                            functionArray[idx]['parentName'] = eachClass['name']
                # Save in the database 
                funcNo = 1
                funcClassNo = 1
                
                for eachFunc in functionArray:
                    if eachFunc['parent'] == 'class':
                        sql_value = [files[f_idx][0], eachFunc['parentName'], eachFunc['name'], funcClassNo, eachFunc['type'], 'public', "Body"]
                        val = (tuple(sql_value))
                        sql = "INSERT INTO `FuncClassTable` (`FileID`, `ClassName`, `FuncName`, `FuncNo`, `ReturnType`, `MarkedArea`, `FuncBody`) VALUES (%s, %s, %s, %s, %s, %s, %s)" # INSERT INTO ExternalVariableTable
                        cur.execute(sql, val)
                        funcClassNo = funcClassNo + 1
                    else:  
                        sql_value = [files[f_idx][0], eachFunc['name'], funcNo, eachFunc['type'], "Body"]
                        val = (tuple(sql_value))
                        sql = "INSERT INTO `FuncInfoTable` (`FileID`, `FuncName`, `FuncNo`, `ReturnType`, `FuncBody`) VALUES (%s, %s, %s, %s, %s)" # INSERT INTO FunctionTable
                        cur.execute(sql, val)
                        funcNo = funcNo + 1
                    dbcon.commit()

                # variableArray = cleanVariable(variableArray)  # 变量
                # Determine parent of Variable
                for idx, each in enumerate(variableArray):
                    for eachClass in classArray:
                        if each['stLine'] > eachClass['stLine'] and each['stLine'] < eachClass['endLine']:
                            variableArray[idx]['parent'] = 'class'
                            variableArray[idx]['parentName'] = eachClass['name']
                    for eachFunc in functionArray:
                        if each['stLine'] > eachFunc['stLine'] and each['stLine'] < eachFunc['endLine']:
                            variableArray[idx]['parent'] = 'func'
                            variableArray[idx]['parentName'] = eachFunc['name']
                # Save Varialbes to Database
                classVariableNo = 1
                funcVariableNo = 1
                VariableNo = 1
                for each in variableArray:
                    if each['parent'] == 'class':
                        valArray = [files[f_idx][0], classVariableNo, each['parentName'], each['name'], each['type'], 'public']
                        val = (tuple(valArray))
                        sql = "INSERT INTO `ClassVariable` (`FileID`, `VariableNo`, `ClassName`, `VariableName`, `VariableType`, `MarkedArea`) VALUES (%s, %s, %s, %s, %s, %s)" # INSERT INTO ExternalVariableTable
                        cur.execute(sql, val)
                        classVariableNo = classVariableNo + 1
                    elif each['parent'] ==  'func':
                        valArray = [files[f_idx][0], funcVariableNo, each['type'], each['name'],  each['parentName'], "YES"]
                        val = (tuple(valArray))
                        sql = "INSERT INTO `FuncVariable` (`FileID`, `VariableNo`, `VariableType`, `VariableName`, `FuncName`, `IsInput`) VALUES (%s, %s, %s, %s, %s, %s)" # INSERT INTO ExternalVariableTable
                        cur.execute(sql, val)
                        funcVariableNo = funcVariableNo + 1
                    else:
                        valArray = [files[f_idx][0], VariableNo, each['type'], each['name'], each['isConst']]
                        val = (tuple(valArray))
                        sql = "INSERT INTO `VariableTable` (`FileID`, `VariableNo`, `VariableType`, `VariableName`, `IsConst`) VALUES (%s, %s, %s, %s, %s)" # INSERT INTO ExternalVariableTable
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




