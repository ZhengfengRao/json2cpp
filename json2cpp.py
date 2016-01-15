#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import shutil
import time

from pyparsing import *

rapidjson_path = "rapidjson"
current_time = time.strftime('%Y-%m-%d, %H:%M',time.localtime(time.time()))

######################################## file       template    ####################################

FILE_HEADER = '''#include "base.h"

using namespace json2cpp;

'''

FILE_FOOTER = '''

}
'''

BASE_H = '''/*
 * File:   base.h
 * Author: json2cpp
 *
 * Created on ''' + current_time + '''
 */

#ifndef JSON2CPP_BASE_H
#define	JSON2CPP_BASE_H

#include <string>
#include <vector>

using namespace std;

/*使用rapidjson做序列化，保证序列化后的json参数有序*/
#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include "rapidjson/error/en.h"

#include "macro.h"
namespace json2cpp{

enum{
    ERR_OK = 0x0,
    ERR_REQUEST_CONFIGURE_INVALID = 1000,
    ERR_REQUEST_OPEN_CONFIGURE_FILE_FAILED,
    ERR_REQUEST_CONFIGURE_FILE_ERROR,
    ERR_REQUEST_INIT_IDMAKER_FAILED,
    ERR_REQUEST_FIELD_NOT_SET,
    ERR_REQUEST_HTTP_FAILED,
    ERR_RESPONSE_RETURNED_ERROR_STATE,
    ERR_RESPONSE_PARAM_TO_JSON_FAILED,
    ERR_RESPONSE_FIELD_NOT_SET,
};

//request && response field
template<typename T>
class Field
{
protected:
    T m_tValue;
    std::string m_strName;
    bool m_bNeed;
    bool m_bSet;
public:
    Field(const std::string& strName, bool bNeed = false)
    :m_tValue() //T类型初始化
    ,m_strName(strName)
    ,m_bNeed(bNeed)
    ,m_bSet(false)
    {
    }

    virtual ~Field()
    {
    }

    void SetValue(const T& value)
    {
        m_tValue = value;
        m_bSet = true;
    }

    const T& GetValue() const
    {
        return m_tValue;
    }

    T& GetValue()
    {
        return m_tValue;
    }

    bool IsValueSet() const
    {
        return m_bSet;
    }

    bool IsValid() const
    {
        return !((m_bNeed == true) && (m_bSet == false));
    }

    virtual void Clear()
    {
        m_bSet = false;
    }

    const std::string& GetName() const
    {
        return m_strName;
    }

private:
    void SetName(const std::string& strName)
    {
        m_strName = strName;
    }
};

template<typename T>
class VectorField: public Field<T>
{
public:
    VectorField(const std::string& strName, bool bNeed = false)
    :Field<T>::Field(strName, bNeed)
    {
    }

    virtual ~VectorField(){}

    virtual void Clear()
    {
        T().swap(this->m_tValue);
        this->m_bSet = false;

        //无法编译通过，因为是继承模板类
        //m_bSet = false;
    }
};

class IRequest
{
public:
    IRequest(){};
    virtual ~IRequest(){};

    virtual uint32_t ToJson(std::string& strJson, std::string& strErrMsg) const = 0;
    virtual bool IsValid(std::string& strErrMsg) const = 0;
};

class IResponse
{
public:
    Field<int> m_JSFCode;                                //JSF协议错误代码             Y
    Field<std::string> m_JSFMessage;                     //JSF协议错误信息

public:
    IResponse()
        :m_JSFCode("code", true)
        ,m_JSFMessage("error")
    {
        Init();
    }

    virtual ~IResponse()
    {
    }

    virtual void Init()
    {
        m_JSFCode.Clear();
        m_JSFMessage.Clear();
    }

    virtual uint32_t FromJson(const std::string& strJson, int status)
    {
        uint32_t dwRet = ERR_OK;

        Init();
        if(status == 200)//http:ok
        {
            m_JSFCode.SetValue(0);
            m_JSFMessage.SetValue("");
            return dwRet;
        }

        //http:error
        //可能的http状态：http://jpcloud.jd.com/pages/viewpage.action?pageId=14357054
        //报错时返回的字符串格式通常为：{"code":500,"error":"错误描述"}
        //但也可能是其他格式或非JSON字符串(webserver报错比如404)，所以需要做容错处理
        rapidjson::Document doc;
        if(doc.Parse<0>(strJson.c_str()).HasParseError() || !doc.IsObject())
        {
            dwRet = ERR_RESPONSE_PARAM_TO_JSON_FAILED;
            m_JSFCode.SetValue(dwRet);
            m_JSFMessage.SetValue("string can not be parsed as json object! str:" + strJson);
        }
        else
        {
            if(doc.HasMember("code") && doc["code"].IsInt())
            {
                m_JSFCode.SetValue(doc["code"].GetInt());
            }
            else
            {
                m_JSFCode.SetValue(status);
            }

            if(doc.HasMember("error") && doc["error"].IsString())
            {
                m_JSFMessage.SetValue(doc["error"].GetString());
            }
            else//没有按格式返回错误，就将返回的全部字符串保存起来
            {
                m_JSFMessage.SetValue(strJson);
            }

            dwRet = ERR_RESPONSE_RETURNED_ERROR_STATE;
        }

        //no need
        //IsValid()

        return dwRet;
    }

    virtual bool IsValid(std::string& strErrMsg) const
    {
        CHECK_REQUEST_FIELD(m_JSFCode, strErrMsg);
        CHECK_REQUEST_FIELD(m_JSFMessage, strErrMsg);

        return true;
    }
};

}
#endif	/* JSON2CPP_BASE_H */
'''

MACRO_H = '''/*
 * File:   macro.h
 * Author: json2cpp
 *
 * Created on ''' + current_time + '''
 */

#ifndef JSON2CPP_MACRO_H
#define	JSON2CPP_MACRO_H

namespace json2cpp{

#define CHECK_REQUEST_FIELD(field, strErrMsg)     \\
    if(!field.IsValid()) \\
    {   \\
        strErrMsg.clear(); \\
        strErrMsg.append("field["); \\
        strErrMsg.append(field.GetName()); \\
        strErrMsg.append("] not set."); \\
        return false;   \\
    }

#define TOJSON_REQUEST_FIELD_INT(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), field.GetValue(), allocator);\\
    }

//使用const-string，不复制字符串
//http://miloyip.github.io/rapidjson/zh-cn/md_doc_tutorial_8zh-cn.html#CreateModifyValues
#define TOJSON_REQUEST_FIELD_STRING(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), rapidjson::StringRef(field.GetValue().c_str()), allocator);\\
    }

#define TOJSON_REQUEST_FIELD_STRING_SETVALUE(field, jsonObject) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject.SetString(rapidjson::StringRef(field.GetValue().c_str())); \\
    }

#define TOJSON_REQUEST_FIELD_OBJECT(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        rapidjson::Value objectValue(rapidjson::kObjectType); \\
        field.GetValue().ToJson(objectValue, allocator); \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), objectValue, allocator); \\
    }

#define TOJSON_REQUEST_FIELD_STR_ARRAY(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        rapidjson::Value value(rapidjson::kArrayType); \\
        for(std::vector<std::string>::const_iterator it = field.GetValue().begin(); \\
            it != field.GetValue().end(); \\
            it++) \\
        { \\
            value.PushBack(rapidjson::StringRef(it->c_str()), allocator); \\
        } \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), value, allocator); \\
    }

#define FROMJSON_RESPONSE_FIELD_NUMBER(values, field) \\
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsNumber()) \\
    { \\
        field.SetValue(values[field.GetName().c_str()].GetInt()); \\
    }

#define FROMJSON_RESPONSE_FIELD_STRING(values, field) \\
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsString()) \\
    { \\
        field.SetValue(values[field.GetName().c_str()].GetString()); \\
    }

#define FROMJSON_RESPONSE_FIELD_OBJECT(values, field) \\
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsObject()) \\
    { \\
        const rapidjson::Value& val = values[field.GetName().c_str()]; \\
        field.GetValue().FromJson(val); \\
        field.SetValue(field.GetValue()); \\
    }

#define JSONVALUE_TOSTRING(json, str) \\
    rapidjson::StringBuffer buffer; \\
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer); \\
    json.Accept(writer); \\
    str= buffer.GetString();

}

'''

CLASS_TOJSON_HEADER = '''	void ToJson(rapidjson::Value& root, rapidjson::Document::AllocatorType& allocator) const
    {
'''

CLASS_TOJSON_FOOTER = '''
    }

'''

TOJSON_HEADER = '''     virtual uint32_t ToJson(std::string& strJson, std::string& strErrMsg) const
    {
        strJson = "";
        if(IsValid(strErrMsg) == false)
        {
            return ERR_REQUEST_FIELD_NOT_SET;
        }

        rapidjson::Document doc;
        rapidjson::Document::AllocatorType& allocator = doc.GetAllocator();
        rapidjson::Value root(rapidjson::kObjectType);
'''

TOJSON_FOOTER = '''
        JSONVALUE_TOSTRING(root, strJson);
        return ERR_OK;
    }
'''

ISVALID_HEADER = '''    virtual bool IsValid(std::string& strErrMsg) const
    {
'''

ISVALID_FOOTER = '''
        return true;
    }
'''

RESPONSE_INVALID_HEADER = '''       if(!IResponse::IsValid(strErrMsg))
        {
            return false;
        }
'''

INIT_HEADER = '''   virtual void Init()
    {
        IResponse::Init();
'''

INIT_FOOTER = '''   }
'''

CLASS_FROMJSON_HEADER = '''    void FromJson(const rapidjson::Value& values)
    {
'''

CLASS_FROMJSON_FOOTER = '''
    }

'''

FROMJSON_HEADER = '''   virtual uint32_t FromJson(const std::string& strJson, int status)
    {
        uint32_t dwRet = ERR_OK;

        Init();
        dwRet = IResponse::FromJson(strJson, status);
        if(dwRet != ERR_OK)
        {
            return dwRet;
        }

        rapidjson::Document doc;
        if(doc.Parse<0>(strJson.c_str()).HasParseError() || !doc.IsObject())
        {
            dwRet = ERR_RESPONSE_PARAM_TO_JSON_FAILED;
            m_JSFCode.SetValue(dwRet);
            m_JSFMessage.SetValue("parse response failed. " +  std::string(rapidjson::GetParseError_En(doc.GetParseError())));
        }
        else
        {
            const rapidjson::Value& values = doc;
'''

FROMJSON_FOOTER = '''
            std::string strError;
            if(!IsValid(strError))
            {
                dwRet = ERR_RESPONSE_FIELD_NOT_SET;
                m_JSFCode.SetValue(dwRet);
                m_JSFMessage.SetValue(strError);
            }
        }

        return dwRet;
    }
'''

######################################## classes definition ####################################
request_iter_marcos = {"": ""}
request_iter_marcos_file = {"": ""}
response_iter_marcos = {"": ""}
response_iter_marcos_file = {"": ""}


def construct_request_iter_marco(vec_type):
    # print "construct_request_iter_marco-->" + vec_type
    normal_type = ["short", "int", "long", "bool", "unsigned", "uint64_t", "int64_t", "double"]
    common_str_head = "\tif(field.IsValueSet()) \\\n" \
                      "\t{ \\\n" \
                      "\t\trapidjson::Value value(rapidjson::kArrayType); \\\n"
    common_str_foot = "\t\tjsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), value, allocator); \\\n" \
                      "\t}\n\n"

    if vec_type in normal_type:    # Normal Type (Numbers)
        # print "Normal"
        request_iter_marcos_file[vec_type] = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                "_ARRAY(field, jsonObject, allocator) \\\n" + \
                common_str_head + \
                "\t\tfor(std::vector<" + vec_type + ">::const_iterator it = field.GetValue().begin(); \\\n" \
                "\t\t\tit != field.GetValue().end(); \\\n" \
                "\t\t\tit++) \\\n" \
                "\t\t{ \\\n" \
                "\t\t\tvalue.PushBack(*it, allocator); \\\n" \
                "\t\t} \\\n" + \
                common_str_foot
    elif vec_type == "string":
        # print "string"
        request_iter_marcos_file[vec_type] = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                "_ARRAY(field, jsonObject, allocator) \\\n" + \
                common_str_head + \
                "\t\tfor(std::vector<" + vec_type + ">::const_iterator it = field.GetValue().begin(); \\\n" \
                "\t\t\tit != field.GetValue().end(); \\\n" \
                "\t\t\tit++) \\\n" \
                "\t\t{ \\\n" \
                "\t\t\tvalue.PushBack(rapidjson::StringRef(it->c_str()), allocator); \\\n" \
                "\t\t} \\\n" + \
                common_str_foot
    else:
        # print "Object"
        request_iter_marcos_file[vec_type] = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                "_ARRAY(field, jsonObject, allocator) \\\n" + \
                common_str_head + \
                "\t\tfor(std::vector<" + vec_type + ">::const_iterator it = field.GetValue().begin(); \\\n" \
                "\t\t\tit != field.GetValue().end(); \\\n" \
                "\t\t\tit++) \\\n" \
                "\t\t{ \\\n" \
                "\t\t\trapidjson::Value objectValue(rapidjson::kObjectType); \\\n" \
                "\t\t\tit->ToJson(objectValue, allocator); \\\n" \
                "\t\t\tvalue.PushBack(objectValue, allocator); \\\n" \
                "\t\t} \\\n" + \
                common_str_foot
    request_iter_marcos[vec_type] = "TOJSON_REQUEST_FIELD_" + vec_type.upper() + "_ARRAY"


def construct_response_iter_marco(vec_type):
    # print "construct_request_iter_marco-->" + vec_type
    normal_type = ["short", "int", "long", "bool", "unsigned", "uint64_t", "int64_t", "double"]
    common_str_head = "\tif(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()]." \
                      "IsArray()) \\\n" \
                      "\t{ \\\n"
    iter_c_str_head = "\t\tconst rapidjson::Value& val = values[field.GetName().c_str()]; \\\n" \
                      "\t\tfor (rapidjson::Value::ConstValueIterator itr = val.Begin(); itr != val.End(); ++itr) \\\n" \
                      "\t\t{ \\\n"
    iter_c_str_foot = "\t\t} \\\n"

    common_str_foot = "\t\tfield.SetValue(vec); \\\n" \
                      "\t}\n\n"

    if vec_type in normal_type:    # Normal Type (Numbers)
        # print "Normal"
        response_iter_marcos_file[vec_type] = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                "_ARRAY(values, field) \\\n" + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\tvec.push_back(itr->GetInt()); \\\n" + \
                iter_c_str_foot + \
                common_str_foot

    elif vec_type == "string":
        # print "string"
        response_iter_marcos_file[vec_type] = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                "_ARRAY(values, field) \\\n" + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\tvec.push_back(itr->GetString()); \\\n" + \
                iter_c_str_foot + \
                common_str_foot
    else:
        # print "Object"
        response_iter_marcos_file[vec_type] = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                "_ARRAY(values, field) \\\n" + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\t" + vec_type + " typeVar; \\\n" + \
                "\t\t\ttypeVar.FromJson(*itr); \\\n" + \
                "\t\t\tvec.push_back(typeVar); \\\n" + \
                iter_c_str_foot + \
                common_str_foot
    response_iter_marcos[vec_type] = "FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + "_ARRAY"


class Field:
    def __init__(self):
        self.description = ""
        self.type = ""
        self.name = ""
        self.jsonname = ""
        self.optional = 0

    def is_valid(self):
        # return self.type != "" and self.name != "" and self.jsonname != ""
        return self.type != "" and self.name != ""

    def get_field_type2(self):
        if "vector" in self.type:
            return "VectorField<" + self.type + " >"
        else:
            return "Field<" + self.type + ">"

    def get_field_type(self):
        if self.type == "vector<int>":
            return "VectorField<std::vector<int> >"
        elif self.type == "vector<short>":
            return "VectorField<std::vector<short> >"
        elif self.type == "vector<string>":
            return "VectorField<std::vector<std::string> >"
        elif self.type == "string":
            return "Field<std::string>"
        else:
            return "Field<" + self.type + ">"

    def get_tojson_method(self):
        # print "get_tojson_method -->"
        normal_type = ["short", "int", "long", "bool", "unsigned", "uint64_t", "int64_t", "double"]
        if self.type in normal_type:
            # print "normal_type"
            return "TOJSON_REQUEST_FIELD_INT"
        elif self.type == "string":
            # print "string"
            return "TOJSON_REQUEST_FIELD_STRING"
        elif "vector" in self.type:
            # print "vector"
            vector_type = self.type
            vector_type = vector_type.strip("vector").strip("<").strip(">")
            # print vector_type
            if vector_type not in request_iter_marcos:
                construct_request_iter_marco(vector_type)
            # if vector_type in normal_type:
            #     return "TOJSON_REQUEST_FIELD_NUM_ARRAY"
            # elif vector_type == "string":
            #     return "TOJSON_REQUEST_FIELD_STR_ARRAY"
            # else:
            #     return "TOJSON_REQUEST_FIELD_OBJECT_ARRAY"
            return request_iter_marcos[vector_type]
        else:
            # print "object"
            return "TOJSON_REQUEST_FIELD_OBJECT"

    # def get_tojson_method(self):
    #     if self.type in ["short", "int", "long", "bool", "unsigned", "uint64_t", "int64_t", "double"]:
    #         return "TOJSON_REQUEST_FIELD_INT"
    #     elif self.type == "string":
    #         return "TOJSON_REQUEST_FIELD_STRING"
    #     elif self.type in ["vector<int>", "vector<short>", "vector<string>"]:
    #         return "TOJSON_REQUEST_FIELD_ARRAY"
    #     else:
    #         print "[警告]不支持的变量类型:" + self.type
    #         return ""

    def get_fromjson_method(self):
        if self.type in ["short", "int", "long", "bool", "unsigned", "uint64_t", "int64_t", "double"]:
            return "FROMJSON_RESPONSE_FIELD_NUMBER"
        elif self.type == "string":
            return "FROMJSON_RESPONSE_FIELD_STRING"
        elif "vector" in self.type:
            vector_type = self.type
            vector_type = vector_type.strip("vector").strip("<").strip(">")
            # print vector_type
            if vector_type not in response_iter_marcos:
                construct_response_iter_marco(vector_type)
            return response_iter_marcos[vector_type]
        else:
            return "FROMJSON_RESPONSE_FIELD_OBJECT"

    def dump_declaration(self):
        str = ""
        if self.is_valid():
            str = "\t" + self.get_field_type2() + "\t\t\tm_" + self.name + ";"
            if self.description != "":
                str += "\t\t\t\t//" + self.description.decode("gbk")
        return str

    def dump_initialize_list(self):
        str = ""
        if self.is_valid():
            str += "\t\t,m_" + self.name + "(\"" + self.jsonname + "\", " + ("true" if self.optional == 0 else "false") + ")\n"
        return str

    def dump_tojson(self):
        str = ""
        if self.is_valid():
            str = "\t\t" + self.get_tojson_method() + "(m_" + self.name + ", root, allocator);\n"
        return str

    def dump_fromjson(self):
        str = ""
        if self.is_valid():
            str = "\t\t\t" + self.get_fromjson_method() + "(values, m_" + self.name + ");\n"
        return str

    def dump_isvalid(self):
        str = ""
        if self.is_valid():
            str = "\t\tCHECK_REQUEST_FIELD(m_" + self.name + ", strErrMsg);\n"
        return str

    def dump_init(self):
        str = ""
        if self.is_valid():
            str = "\t\tm_" + self.name + ".Clear();\n"
        return str


class FieldCollector:
    def __init__(self):
        self.fields = []

    def is_valid(self):
        if len(self.fields) == 0:
            return 0
        for field in self.fields:
            if field.is_valid() == 0:
                return 0
        return 1

    def dump_declaration(self):
        str = "public:\n"
        for field in self.fields:
            str += field.dump_declaration()
            str += "\n"
        return str

    def dump_initialize_list(self):
        str = ""
        for field in self.fields:
            str += field.dump_initialize_list()
        return str

    def dump_isvalid(self):
        str = ""
        for field in self.fields:
            str += field.dump_isvalid()
        return str


class Request(FieldCollector):
    def dump_tojson(self):
        str = ""
        for field in self.fields:
            str += field.dump_tojson()
        return str


class Response(FieldCollector):
    def dump_fromjson(self):
        str = ""
        for field in self.fields:
            str += field.dump_fromjson()
        return str

    def dump_init(self):
        str = ""
        for field in self.fields:
            str += field.dump_init()
        return str


class Class(FieldCollector):
    def __init__(self):
        FieldCollector.__init__(self)
        self.description = ""
        self.name = ""

    def dump_to_json(self):
        str = ""
        for field in self.fields:
            str += field.dump_tojson()
        to_json_method = CLASS_TOJSON_HEADER + "\n" \
            + str \
            + CLASS_TOJSON_FOOTER

        return to_json_method

    def dump_from_json(self):
        str = ""
        for field in self.fields:
            str += field.dump_fromjson()
        from_json_method = CLASS_FROMJSON_HEADER + "\n" \
            + str \
            + CLASS_FROMJSON_FOOTER

        return from_json_method

    def dump(self):
        init_list = self.dump_initialize_list()
        init_list = list(init_list)
        init_list[2] = " "
        init_list = "".join(init_list)
        class_str = "class " + self.name + "\n{\n" \
            + self.dump_declaration() \
            + "\npublic:\n" \
            + "\t" + self.name + "() : \n" \
            + init_list \
            + "\t{}\n\n" \
            + "\t~" + self.name + "(){}\n\n" \
            + self.dump_to_json() \
            + self.dump_from_json() \
            + "};\n\n"
        return class_str


class Interface:
    def __init__(self):
        self.description = ""
        self.name = ""
        self.request = 0
        self.response = 0

    def is_valid(self):
        return self.name != ""\
            and isinstance(self.request, Request) and self.request.is_valid() \
            and isinstance(self.response, Response) and self.response.is_valid()

    @property
    def dump(self):
        request_str = "class " + self.name + "Request: public IRequest\n{\n" \
            + self.request.dump_declaration() \
            + "\npublic:\n" \
            + "\t" + self.name + "Request()\n" \
            + "\t\t:IRequest()\n" \
            + self.request.dump_initialize_list() \
            + "\t{}\n\n" \
            + "\t~" + self.name + "Request()\n\t{}\n\n" \
            + TOJSON_HEADER + "\n"\
            + self.request.dump_tojson()\
            + TOJSON_FOOTER + "\n"\
            + ISVALID_HEADER \
            + self.request.dump_isvalid() \
            + ISVALID_FOOTER \
            + "};"

        response_str = "class " + self.name + "Response: public IResponse\n{\n" \
            + self.response.dump_declaration() \
            + "\npublic:\n" \
            + "\t" + self.name + "Response()\n" \
            + "\t\t:IResponse()\n" \
            + self.response.dump_initialize_list() \
            + "\t{}\n\n" \
            + "\t~" + self.name + "Response()\n\t{}\n\n" \
            + INIT_HEADER + "\n" \
            + self.response.dump_init() \
            + INIT_FOOTER + "\n" \
            + FROMJSON_HEADER \
            + self.response.dump_fromjson() \
            + FROMJSON_FOOTER + "\n"\
            + ISVALID_HEADER \
            + RESPONSE_INVALID_HEADER + "\n"\
            + self.response.dump_isvalid() \
            + ISVALID_FOOTER \
            + "};"

        return request_str + "\n\n" + response_str
        #source file


def key_value_field(keyName):
    equal = Suppress("=")
    return Group(keyName + equal + quotedString)


######################################## parse  tokens ####################################
def load_grammar():
    quot = Suppress("\"")
    lbrace = Suppress("{")
    rbrace = Suppress("}")
    lbracket = Suppress("(")
    rbracket = Suppress(")")
    semicolon = Suppress(";")
    at = Suppress("@")
    comma = Suppress(",")
    equal = Suppress("=")
    nspace = Suppress("::")
    word = Word(alphanums + "_/")
    interface_key = "Interface"
    class_key = "class"
    namespace_key = "namespace"
    interface_name = word
    request_key = "Request"
    response_key = "Response"
    jsonname_key = "jsonname"
    description_key = "description"
    optional_key = "optional"
    field_name = word

    #field_type = oneOf("short int string vector<short> vector<int> vector<string>")
    namespace_field = Group(namespace_key + word + ZeroOrMore(nspace + word))
    field_type = Word(alphanums + "_/<>")
    description = Group(at + description_key + equal + quotedString)
    jsonname = Group(at + jsonname_key + equal + quotedString)
    keyValueField = Group(word + equal + quotedString)
    jsonField = Group(jsonname + Optional(comma + key_value_field(description_key)) \
                      + Optional(comma + key_value_field(optional_key)))
    # field = Group(Optional(description) + jsonname + field_type + field_name + Optional(optional_key) + semicolon)
    field = Group(jsonField + field_type + field_name + semicolon)
    request = Group(request_key + lbrace + OneOrMore(field) + rbrace + semicolon)
    response = Group(response_key + lbrace + OneOrMore(field) + rbrace + semicolon)
    interface = Group(Optional(description) \
        + interface_key + interface_name + lbrace \
        + request \
        + response\
        + rbrace + semicolon)

    classGram = Group(Optional(description) \
        + class_key + interface_name + lbrace \
        + OneOrMore(field) \
        + rbrace + semicolon)

    grammar = ZeroOrMore(namespace_field) + ZeroOrMore(classGram) + OneOrMore(interface)
    return OneOrMore(grammar).ignore(cppStyleComment)


def parse_namespace(token, base_dir):
    namespace_list = []
    base_dir_str = base_dir
    for i in range(len(token)):
        if i == 0:
            pass
        else:
            namespace_list.append(token[i])
            base_dir_str = base_dir_str + os.sep + token[i]
    return namespace_list, base_dir_str


def parse_class(class_token):
    classField = Class()
    class_token_len = len(class_token)

    # class description
    description_dis = 0
    if type(class_token[0]) != list:
        if class_token[0] != "class":
            print "[ERROR] Parsing Class token failed: class key word not found!"
        description_dis = 1
    else:
        classField.description = parse_description(class_token[0])

    # class name
    class_name = class_token[description_dis + 2]
    if type(class_name) != str:
        print u"[ERROR]class name <" + class_name + u">should be str type, but now: " + type(class_name)
        return
    classField.name = class_name

    # class fields
    for i in range(class_token_len):
        if i <= description_dis + 2:
            # class keyword & class name
            pass
        else:
            field = parse_field(class_token[i])
            if isinstance(field, Field) and field.is_valid():
                classField.fields.append(field)
    return classField


def parse_interface(interface_token):
    if type(interface_token) != list:
        print u"[ERROR] Unsupported interface_token type:<" + type(interface_token) + u">"
        print interface_token

    interface = Interface()
    interface_token_len = len(interface_token)

    # interface description
    description_dis = 0
    if 5 == interface_token_len:    # Have Comments here
        interface.description = parse_description(interface_token[0])
        description_dis = 1
    elif interface_token_len != 4:
        print u"[ERROR] Expected interface_token_len is [4-5], actually is: " + str(interface_token_len)
        print interface_token
        return

    # interface keyword
    # interface_token[description_dis]

    # interface name
    interface_name = interface_token[description_dis + 1]
    if type(interface_name) != str:
        print u"[ERROR]Interface name <" + interface_name + u">should be str type, but now: " + type(interface_name)
        return
    interface.name = interface_name

    # interface request
    interface_request = interface_token[description_dis + 2]
    interface.request = parse_request(interface_request)

    # interface response
    interface_response = interface_token[description_dis + 3]
    if type(interface_response) != list:
        print u"[错误]错误的response类型." + type(interface_response)
        print interface_response
        return
    interface.response = parse_response(interface_response)

    return interface


def parse_description(description_tokens):
    if type(description_tokens) == list and len(description_tokens) == 2:
        if type(description_tokens[1] == str) and description_tokens[1] != "":
            return description_tokens[1].strip("\"")
    return ""


def parse_key_value_field(keyvalue_tokens):
    if type(keyvalue_tokens) == list and len(keyvalue_tokens) == 2:
        if type(keyvalue_tokens[1] == str) and keyvalue_tokens[1] != "":
            return keyvalue_tokens[1].strip("\"")
    return ""


def parse_to_key_value_field_arrays(tokens):
    key_value = {"jsonname": ""}
    for m in range(len(tokens)):
        keyName = tokens[m][0];
        if keyName == "jsonname":
            key_value["jsonname"] = parse_key_value_field(tokens[m])
        elif keyName == "description":
            key_value["description"] = parse_key_value_field(tokens[m])
        elif keyName == "optional":
            key_value["optional"] = parse_key_value_field(tokens[m])
    return key_value


def parse_request(request_tokens, object_type="request"):
    if type(request_tokens) != list:
        print u"[ERROR] Wrong request/response type define: " + str(type(request_tokens))
        print request_tokens
        return

    request_token_len = len(request_tokens)
    if request_token_len < 2:
        print u"[ERROR] Unexpected end field of request/response, expected:[>=2], actual:" + str(request_token_len)
        print request_tokens
        return

    object = Request() if (object_type == "request") else Response()
    for i in range(request_token_len):
        if i == 0:
            # request/response keyword
            pass
        else:
            field = parse_field(request_tokens[i])
            if isinstance(field, Field) and field.is_valid():
                object.fields.append(field)
    return object


def parse_response(response_tokens):
    return parse_request(response_tokens, "response")


def parse_field(field_tokens):
    if type(field_tokens) != list:
        print u"[ERROR] Wrong field type, field_tokens is not list: " + str(type(field_tokens))
        print field_tokens
        return

    field_token_len = len(field_tokens)
    if field_token_len != 3:
        print u"[ERROR]expected field_token_len should be 3, actually is: " + str(field_token_len)
        print field_tokens
        return

    field = Field()

    # jsonname field
    jsonname_field_tokens = field_tokens[0]
    if type(jsonname_field_tokens) != list:
        print u"[ERROR] Wrong jsonname_field_tokens type: " + str(type(jsonname_field_tokens))
        print jsonname_field_tokens
        return

    key_values = parse_to_key_value_field_arrays(jsonname_field_tokens)
    if key_values["jsonname"] == "":
        print u"[ERROR] jsonname field is NULL!"
        print jsonname_field_tokens
        return
    field.jsonname = key_values["jsonname"]

    if "description" in key_values and key_values["description"] != "":
        field.description = key_values["description"]

    if "optional" in key_values and key_values["optional"] == "true":
        field.optional = 1

    # field type
    field_type_token = field_tokens[1]
    if type(field_type_token) != str:
        print u"[ERROR] Wrong field type, NOT str: " + str(type(field_type_token))
        print field_type_token
        return
    field.type = field_type_token

    # field name
    field_name_token = field_tokens[2]
    if type(field_name_token) != str:
        print u"[ERROR] Wrong field_name type: " + str(type(field_name_token))
        print field_name_token
        return
    field.name = field_name_token

    return field


'''
################################ generate c++ files ####################################
'''
def generate_base(macros, base_directory):
    macro_h = open(base_directory + os.sep + "macro.h", "w")
    macro_h.write(macros)
    macro_h.close()

    base_h = open(base_directory + os.sep + "base.h", "w")
    base_h.write(BASE_H)
    base_h.close()

    # rapidjson library
    if not os.path.exists(rapidjson_path):
        print u"[ERROR] rapidjson库路径不存在." + os.path.abspath(rapidjson_path)
        exit(-1)
    if not os.path.isdir(rapidjson_path):
        print u"[ERROR] rapidjson库路径不是目录." + os.path.abspath(rapidjson_path)
        exit(-1)

    try:
        rapidjson_directory = base_directory + os.sep + "rapidjson"
        if os.path.exists(rapidjson_directory):
            shutil.rmtree(rapidjson_directory)
        shutil.copytree(os.path.abspath(rapidjson_path), rapidjson_directory)
    except Exception, e:
        print e


def generate_test(base_directory):
    pass


def generate_interface(base_directory, namspace_str, class_fields, interface):
    class_str = ""
    for classField in class_fields:
        class_str += classField.dump()

    ns_str = ""
    file_footer = "\n"
    # handle namespace
    if namspace_str:
        for nameS in namspace_str:
            ns_str = ns_str + "namespace " + nameS + " { "
            file_footer += "} "
        ns_str += "\n"
    # print ns_str
    header = FILE_HEADER + ns_str + class_str + interface.dump + file_footer

    header_h = open(base_directory + os.sep + interface.name + ".h", "w")
    header_h.write(header)
    header_h.close()


def generate_files(tokens, base_dir):
    if type(tokens) != list or len(tokens) < 1:
        print u"[错误]无效的tokens. type:" + type(tokens) + ", len:" + len(tokens)
        print tokens
        return

    # print "--- tokens ---"
    # print tokens
    # print "-----------------"
    class_fields = []
    namespace = ""
    for token in tokens:
        # print token
        if (type(token[0]) == list and token[1] == "class") or token[0] == "class":
            # print "Parse class..."
            class_field = parse_class(token)
            class_fields.append(class_field)
        elif (type(token[0]) == list and token[1] == "Interface") or token[0] == "Interface":
            # print "Parse Interface..."
            interface = parse_interface(token)
        elif token[0] == "namespace":
            # print "Parse  namespace..."
            namespace = parse_namespace(token, base_dir)
        else:
            print "[ERROR] Parsing token failed! No class or Interface key word find!"
            return

    base_directory = base_dir
    namespace_str = ""
    if namespace != "":
        namespace_str = namespace[0]
        # print namespace_str
        base_directory = namespace[1]
        # print base_directory
    print "Generating code in dir ---> \"" + base_directory + "\""

    # Create dir by namespace
    if not os.path.exists(base_directory):
        try:
            os.makedirs(base_directory)
        except OSError, why:
            print u"[错误]创建目标文件夹." + os.path.abspath(base_directory) + u"失败."
            exit(-1)

    generate_interface(base_directory, namespace_str, class_fields, interface)
    str_out = MACRO_H
    for req_macros in request_iter_marcos_file:
        str_out += request_iter_marcos_file[req_macros]
    for res_macros in response_iter_marcos_file:
        str_out += response_iter_marcos_file[res_macros]
    str_out += "\n#endif	/* JSON2CPP_MACRO_H */\n"
    # base files
    generate_base(str_out, base_directory)


'''
##################################      main           ####################################
'''
def usage():
    print "json2cpp {grammar_file} {generated_directory}"


def parse_param(argv):
    grammar_file = argv[1]
    base_directory = argv[2]

    if not os.path.exists(grammar_file):
        print u"[错误]文件不存在:" + os.path.abspath(grammar_file)
        exit(-1)

        if not os.path.isfile(grammar_file):
            print u"[错误]" + os.path.abspath(grammar_file) + u"不是有效的文件."
            exit(-1)

    # base_directory = base_directory + os.sep + "jsf"
    # if not os.path.exists(base_directory):
    #     try:
    #         os.makedirs(base_directory)
    #     except OSError, why:
    #         print u"[错误]创建目标文件夹." + os.path.abspath(base_directory) + u"失败."
    #         exit(-1)

    return os.path.abspath(grammar_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        exit(-1)

    file_path = parse_param(sys.argv)
    grammar = load_grammar()
    tokens = grammar.parseFile(file_path).asList()
    generate_files(tokens, sys.argv[2])
    print current_time