#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (c) 2015-2016 ZhengFeng Rao, nasacj

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import platform
import shutil
import time
import codecs

from pyparsing import *
ParserElement.enablePackrat()

JSON_API = ""
JSON_API_RAPIDJSON = "rapidjson"
JSON_API_JSONCPP = "jsoncpp"
rapidjson_path = JSON_API_RAPIDJSON
NORMAL_TYPE = ["short", "int", "bool", "uint32_t", "uint64_t", "int64_t", "double"]
current_time = time.strftime('%Y-%m-%d, %H:%M', time.localtime(time.time()))

######################################## file       template    ####################################

FILE_HEADER = '''#include "base.h"

using namespace json2cpp;

'''

FILE_FOOTER = '''

}
'''

BASE_H_HEADER = '''/*
 * File:   base.h
 * Author: json2cpp
 *
 * Created on ''' + current_time + '''
 */

#ifndef JSON2CPP_BASE_H
#define	JSON2CPP_BASE_H

#include <stdint.h>
#include <string>
#include <sstream>
#include <vector>

using namespace std;

'''

BASE_H_JSON_INCLUDE_JSONCPP = '''
#include "json/json.h"

'''

BASE_H_JSON_INCLUDE_RAPIDJSON = '''
#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include "rapidjson/error/en.h"

'''

BASE_H_BODY = '''
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
	ERR_RESPONSE_PARSE_PROCOTOL_FAILED,
};

template<typename T>
T String2Number(const std::string& str)
{
	T number;
	std::stringstream ss;
	ss<<str;
	ss>>number;

	return number;
}

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
    :m_tValue() //T
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

//遵循网关接口4.0规范:http://cf.jd.com/pages/viewpage.action?pageId=71986745
class IResponse
{
public:
    Field<int> m_JSFCode;                       //返回码
	Field<std::string> m_JSFErrorCode;			//业务返回的错误码(接口返回的code不为0时使用)
    Field<std::string> m_JSFMessage;            //错误信息
    Field<std::string> m_JSFMessageId;          //消息uuid
    Field<std::string> m_JSFMessageIp;          //服务器昵称
    Field<std::string> m_JSFMessageType;        //消息类型，目前有string,json,null

public:
    IResponse()
        :m_JSFCode("code", true)
		,m_JSFErrorCode("")
        ,m_JSFMessage("error")
        ,m_JSFMessageId("uid")
        ,m_JSFMessageIp("ip")
        ,m_JSFMessageType("type")
    {
        Init();
    }

    virtual ~IResponse()
    {
    }

    virtual void Init()
    {
        m_JSFCode.Clear();
		m_JSFErrorCode.Clear();
        m_JSFMessage.Clear();
        m_JSFMessageId.Clear();
        m_JSFMessageIp.Clear();
        m_JSFMessageType.Clear();
    }

    virtual uint32_t FromJson(const std::string& strJson, int status)
    {
        uint32_t dwRet = ERR_OK;

        Init();
'''

BASE_H_FOOTER = '''
        {
            dwRet = ERR_RESPONSE_PARAM_TO_JSON_FAILED;

            m_JSFCode.SetValue(dwRet);
            m_JSFMessage.SetValue("string can not be parsed as json object! str:" + strJson);
        }
        else
        {
			if(status == 200)//http:ok
			{
				if(doc.isMember(m_JSFCode.GetName()) && doc[m_JSFCode.GetName()].isString())
				{
					m_JSFCode.SetValue(String2Number<int>(doc[m_JSFCode.GetName()].asString()));
				}

				FROMJSON_RESPONSE_FIELD_STRING(doc, m_JSFMessageId);
				FROMJSON_RESPONSE_FIELD_STRING(doc, m_JSFMessageIp);
				FROMJSON_RESPONSE_FIELD_STRING(doc, m_JSFMessageType);
			}
			else
			{
				dwRet = ERR_RESPONSE_RETURNED_ERROR_STATE;
				m_JSFCode.SetValue(dwRet);
				m_JSFMessage.SetValue("http returned error status, str:" + strJson);
			}
        }

        //no need
        //IsValid()

        return dwRet;
    }

    virtual bool IsValid(std::string& strErrMsg) const
    {
        CHECK_REQUEST_FIELD(m_JSFCode, strErrMsg);
        CHECK_REQUEST_FIELD(m_JSFMessage, strErrMsg);
        CHECK_REQUEST_FIELD(m_JSFMessageId, strErrMsg);
        CHECK_REQUEST_FIELD(m_JSFMessageIp, strErrMsg);
        CHECK_REQUEST_FIELD(m_JSFMessageType, strErrMsg);

        return true;
    }
};

}
#endif	/* JSON2CPP_BASE_H */
'''


def build_BASE_H_FROMJSON(jsonAPI):
    base_h_str = ""
    if jsonAPI == JSON_API_RAPIDJSON:
        base_h_str = '''
        rapidjson::Document doc;
        if(doc.Parse<0>(strJson.c_str()).HasParseError())'''
    elif jsonAPI == JSON_API_JSONCPP:
        base_h_str = '''
        Json::Reader reader;
        Json::Value doc;
        if(!reader.parse(strJson, doc, false))'''
    return base_h_str;


def build_BASE_H(jsonAPI):
    base_str = ""
    base_include_json = ""
    base_body_fromjson = build_BASE_H_FROMJSON(jsonAPI)
    if jsonAPI == JSON_API_RAPIDJSON:
        base_include_json = BASE_H_JSON_INCLUDE_RAPIDJSON
    elif jsonAPI == JSON_API_JSONCPP:
        base_include_json = BASE_H_JSON_INCLUDE_JSONCPP
    base_str = BASE_H_HEADER + base_include_json + BASE_H_BODY + base_body_fromjson + BASE_H_FOOTER
    return base_str


MACRO_H_BASE = '''/*
 * File:   macro.h
 * Author: json2cpp
 *
 * Created on ''' + current_time + '''
 */

#ifndef JSON2CPP_MACRO_H
#define	JSON2CPP_MACRO_H

#define CHECK_REQUEST_FIELD(field, strErrMsg)     \\
    if(!field.IsValid()) \\
    {   \\
        strErrMsg.clear(); \\
        strErrMsg.append("field["); \\
        strErrMsg.append(field.GetName()); \\
        strErrMsg.append("] not set."); \\
        return false;   \\
    }

#define CHECK_FIELD_ISVALID_FATHER(father, strErrMsg) \\
    if (!father::IsValid(strErrMsg)) \\
        return false;

#define FROMJSON_RESPONSE_FIELD_FATHER(values) \\
    fromJson(values);

'''

MACRO_H_RAPIDJSON = '''
#define TOJSON_REQUEST_FIELD_NUMBER(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), field.GetValue(), allocator);\\
    }

//http://miloyip.github.io/rapidjson/zh-cn/md_doc_tutorial_8zh-cn.html#CreateModifyValues
#define TOJSON_REQUEST_FIELD_STRING(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), rapidjson::StringRef(field.GetValue().c_str()), allocator);\\
    }

#define TOJSON_REQUEST_FIELD_OBJECT(field, jsonObject, allocator) \\
    if(field.IsValueSet()) \\
    { \\
        rapidjson::Value objectValue(rapidjson::kObjectType); \\
        field.GetValue().toJson(objectValue, allocator); \\
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), objectValue, allocator); \\
    }

#define TOJSON_REQUEST_FIELD_FATHER(jsonObject, allocator) \\
    toJson(jsonObject, allocator);

#define FROMJSON_RESPONSE_FIELD_STRING(values, field) \\
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsString()) \\
    { \\
        field.SetValue(values[field.GetName().c_str()].GetString()); \\
    }

#define FROMJSON_RESPONSE_FIELD_STRING_NONAME_ONLY(values, field) \\
    if(values.IsString()) \\
    { \\
        field.SetValue(values.GetString()); \\
    }

#define FROMJSON_RESPONSE_FIELD_OBJECT(values, field) \\
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsObject()) \\
    { \\
        const rapidjson::Value& val = values[field.GetName().c_str()]; \\
        field.GetValue().fromJson(val); \\
        field.SetValue(field.GetValue()); \\
    }

#define FROMJSON_SET_ERROR_TO_RETURN(errorCode, errorMsg)\\
	dwRet = errorCode;\\
	m_JSFCode.SetValue(dwRet);\\
	m_JSFMessage.SetValue(errorMsg);\\
	return dwRet;\\

#define JSONVALUE_TOSTRING(json, str) \\
    rapidjson::StringBuffer buffer; \\
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer); \\
    json.Accept(writer); \\
    str= buffer.GetString();

'''

MACRO_H_JSONCPP = '''

#define TOJSON_REQUEST_FIELD_NUMBER(field, jsonObject) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject[field.GetName()] = field.GetValue(); \\
    }

#define TOJSON_REQUEST_FIELD_STRING(field, jsonObject) \\
    if(field.IsValueSet()) \\
    { \\
        jsonObject[field.GetName()] = field.GetValue(); \\
    }

#define TOJSON_REQUEST_FIELD_OBJECT(field, jsonObject) \\
    if(field.IsValueSet()) \\
    { \\
        Json::Value object; \\
        field.GetValue().toJson(object); \\
        jsonObject[field.GetName()] = object; \\
    }

#define TOJSON_REQUEST_FIELD_FATHER(jsonObject) \\
    toJson(jsonObject);

#define FROMJSON_RESPONSE_FIELD_STRING(values, field) \\
    if(values.isMember(field.GetName()) && values[field.GetName()].isString()) \\
    { \\
        field.SetValue(values[field.GetName()].asString()); \\
    }

#define FROMJSON_RESPONSE_FIELD_STRING_NONAME_ONLY(values, field) \\
    if(values.isString()) \\
    { \\
        field.SetValue(values.asString()); \\
    }

#define FROMJSON_RESPONSE_FIELD_OBJECT(values, field) \\
    if(values.isMember(field.GetName()) && values[field.GetName()].isObject()) \\
    { \\
        const Json::Value& val = values[field.GetName()]; \\
        field.GetValue().fromJson(val); \\
        field.SetValue(field.GetValue()); \\
    }

#define FROMJSON_SET_ERROR_TO_RETURN(errorCode, errorMsg)\\
	dwRet = errorCode;\\
	m_JSFCode.SetValue(dwRet);\\
	m_JSFMessage.SetValue(errorMsg);\\
	return dwRet;\\

#define JSONVALUE_TOSTRING(json, str) \\
    Json::FastWriter writer; \\
    str = writer.write(json);


'''

def build_MACRO_H_BASE(jsonAPI):
    macro_h = MACRO_H_BASE
    if jsonAPI == JSON_API_RAPIDJSON:
        macro_h += MACRO_H_RAPIDJSON
    elif jsonAPI == JSON_API_JSONCPP:
        macro_h += MACRO_H_JSONCPP
    return macro_h


CLASS_TOJSON_HEADER_RAPIDJSON = '''	void toJson(rapidjson::Value& root, rapidjson::Document::AllocatorType& allocator) const
    {
'''

CLASS_TOJSON_HEADER_JSONCPP = '''	void toJson(Json::Value& root) const
    {
'''

CLASS_TOJSON_FOOTER = '''\t}

'''

TOJSON_HEADER = '''    virtual uint32_t ToJson(std::string& strJson, std::string& strErrMsg) const
    {
        strJson = "";
        if(IsValid(strErrMsg) == false)
        {
            return ERR_REQUEST_FIELD_NOT_SET;
        }
'''


def build_TOJSON_HEADER(jsonAPI, isArrayOnly, hasFather):
    tojson_header = TOJSON_HEADER
    if jsonAPI == JSON_API_RAPIDJSON:
        tojson_header += '''
        rapidjson::Document doc;
        rapidjson::Document::AllocatorType& allocator = doc.GetAllocator();
        '''
        if isArrayOnly:
            tojson_header += "rapidjson::Value root(rapidjson::kArrayType);\n\n"
        else:
            tojson_header += "rapidjson::Value root(rapidjson::kObjectType);\n\n"
        if hasFather:
            tojson_header += "\t\tTOJSON_REQUEST_FIELD_FATHER(root, allocator)\n"
    elif jsonAPI == JSON_API_JSONCPP:
        tojson_header += '''
        Json::Value root;

'''
        if hasFather:
            tojson_header += "\t\tTOJSON_REQUEST_FIELD_FATHER(root)\n"

    return tojson_header

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

INIT_HEADER = '''    virtual void Init()
    {
'''

INIT_FOOTER = '''   }
'''

CLASS_FROMJSON_HEADER_RAPIDJSON = '''    void fromJson(const rapidjson::Value& values)
    {
'''

CLASS_FROMJSON_HEADER_JSONCPP = '''    void fromJson(const Json::Value& values)
    {
'''

CLASS_FROMJSON_FOOTER = '''\t}

'''

CLASS_FROMJSON_FUNC_HEADER = '''    virtual uint32_t FromJson(const std::string& strJson, string& strError)
    {
        uint32_t dwRet = ERR_OK;

        Init();
'''

CLASS_FROMJSON_FUNC_FOOTER = '''
            if(!IsValid(strError))
            {
                dwRet = ERR_RESPONSE_FIELD_NOT_SET;
            }
        }

        return dwRet;
    }

'''


def build_CLASS_FROMJSON_HEADER(jsonAPI):
    fromjson_header = CLASS_FROMJSON_FUNC_HEADER
    if jsonAPI == JSON_API_RAPIDJSON:
        fromjson_header += '''
        rapidjson::Document doc;
        if(doc.Parse<0>(strJson.c_str()).HasParseError())
        {
            dwRet = ERR_RESPONSE_PARAM_TO_JSON_FAILED;
            strError = std::string("parse response failed. ") +  std::string(rapidjson::GetParseError_En(doc.GetParseError()));
        }
        else
        {
            const rapidjson::Value& values = doc;

            this->fromJson(values);
'''
    elif jsonAPI == JSON_API_JSONCPP:
        fromjson_header += '''
        Json::Reader reader;
        Json::Value jsonResult;
        if (!reader.parse(strJson, jsonResult, false))
        {
            dwRet = ERR_RESPONSE_PARAM_TO_JSON_FAILED;
            strError = string("parse response failed. ") +  reader.getFormattedErrorMessages();
        }
        else
        {
            const Json::Value& values = jsonResult;

            this->fromJson(values);
'''
    return fromjson_header + CLASS_FROMJSON_FUNC_FOOTER


FROMJSON_HEADER = '''    virtual uint32_t FromJson(const std::string& strJson, int status)
    {
        uint32_t dwRet = ERR_OK;

        Init();
        dwRet = IResponse::FromJson(strJson, status);
        if(dwRet != ERR_OK)
        {
            return dwRet;
        }
'''


def build_FROMJSON_HEADER(jsonAPI, has_father):
    fromjson_header = FROMJSON_HEADER
    if jsonAPI == JSON_API_RAPIDJSON:
        fromjson_header += '''
		std::string strError;
        rapidjson::Document doc;
        if(doc.Parse<0>(strJson.c_str()).HasParseError())
        {
			FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARAM_TO_JSON_FAILED, "parse response failed. " + std::string(rapidjson::GetParseError_En(doc.GetParseError())));
        }
        else
        {	//遵循网关接口4.0规范:http://cf.jd.com/pages/viewpage.action?pageId=71986745
			//示例:	{"code": "0","ip": "大猫","result": {"......"},"type": "json"}
			//		{"code":"10067","error_response":{"code":"10067","uid": "c27832d1-e641-4dd9-bfc0-a39058f173bf","exception":"参数异常","gw_code":"D20013","parameter":"parameterTypes -> [], args -> []","en_desc": "","zh_desc": ""}}

            rapidjson::Value& values = doc;
			if (!values.IsObject())
			{
				FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "response is not a json object.");
			}

			//检查code，判断调用成功还是失败
			if (!(doc.HasMember("code") && doc["code"].IsString()))
			{
				FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "field 'code' not set, or not a string.");
			}

			if(values["code"].GetString() == "0")
			{//调用成功
				if (!(values.HasMember("type") && values["type"].IsString()))
				{
					FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "field 'type' not set, or not a string.");
				}

				if (values["type"].GetString() == "json")
				{
					if (!(values.HasMember("result") /*&& values["result"].IsObject()*/))
					{
						FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "field 'result' not set, or not an object.");
					}

					values = values["result"];

'''
    elif jsonAPI == JSON_API_JSONCPP:
        fromjson_header += '''
		std::string strError;
        Json::Reader reader;
        Json::Value jsonResult;
        if (!reader.parse(strJson, jsonResult, false))
        {
			FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARAM_TO_JSON_FAILED, "parse response failed. " +  reader.getFormattedErrorMessages());
        }
        else
        {	//遵循网关接口4.0规范:http://cf.jd.com/pages/viewpage.action?pageId=71986745
			//示例:	{"code": "0","ip": "大猫","result": {"......"},"type": "json"}
			//		{"code":"10067","error_response":{"code":"10067","uid": "c27832d1-e641-4dd9-bfc0-a39058f173bf","exception":"参数异常","gw_code":"D20013","parameter":"parameterTypes -> [], args -> []","en_desc": "","zh_desc": ""}}

            Json::Value& values = jsonResult;
			if (!values.isObject())
			{
				FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "response is not a json object.");
			}

			//检查code，判断调用成功还是失败
			if (!(values.isMember("code") && values["code"].isString()))
			{
				FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "field 'code' not set, or not a string.");
			}

			if(values["code"].asString() == "0")
			{//调用成功
				if (!(values.isMember("type") && values["type"].isString()))
				{
					FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "field 'type' not set, or not a string.");
				}

				if (values["type"].asString() == "json")
				{
					if (!(values.isMember("result") /*&& values["result"].isObject()*/))
					{
						FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_PARSE_PROCOTOL_FAILED, "field 'result' not set, or not an object.");
					}

					values = values["result"];

'''
    if has_father:
        fromjson_header += "\t\t\t\tFROMJSON_RESPONSE_FIELD_FATHER(values);\n"
    return fromjson_header

def build_FROMJSON_FOOTER(jsonAPI, type):
    str2 = '''
                    FROMJSON_RESPONSE_FIELD_STRING(values[\"result\"], m_result)
                    if(!IsValid(strError))
					{
						FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_FIELD_NOT_SET, strError);
					}
    ''' if type=="string" else ""
    str4 = '''
                ErrorResponseV4 errorResponseV4;
				ErrorResponseObjectV4 errorResponseObjectV4;
				if(json2cpp::ERR_OK == errorResponseV4.FromJson(strJson, strError))
				{
					errorResponseObjectV4 = errorResponseV4.m_object.GetValue();
					if (errorResponseObjectV4.m_gw_code.IsValueSet())
					{
						m_JSFErrorCode.SetValue(errorResponseObjectV4.m_gw_code.GetValue());
					}

					if (errorResponseObjectV4.m_zh_description.IsValueSet())
					{
						FROMJSON_SET_ERROR_TO_RETURN(dwRet, errorResponseObjectV4.m_zh_description.GetValue());
					}
				}
				else
				{
					FROMJSON_SET_ERROR_TO_RETURN(dwRet, strError);
				}
			}
        }

        return dwRet;
    }
'''

    if jsonAPI == JSON_API_RAPIDJSON:
        str1 =  '''
					if(!IsValid(strError))
					{
						FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_FIELD_NOT_SET, strError);
					}
				}
				else if (values["type"].GetString() == "string")
				{
                '''
        str3 =  '''
				}
				else if (values["type"].GetString() == "null")
				{
					return dwRet;
				}
			}
			else//调用失败
			{//解析错误信息
				dwRet = json2cpp::String2Number<int>(values["code"].GetString());
                '''
        return str1+str2+str3+str4
    elif jsonAPI == JSON_API_JSONCPP:
        str1 =  '''
                    if(!IsValid(strError))
					{
						FROMJSON_SET_ERROR_TO_RETURN(ERR_RESPONSE_FIELD_NOT_SET, strError);
					}
				}
				else if (values["type"].asString() == "string")
				{
				''';
        str3 =  '''
				}
				else if (values["type"].asString() == "null")
				{
					return dwRet;
				}
			}
			else//调用失败
			{//解析错误信息
				dwRet = json2cpp::String2Number<int>(values["code"].asString());
                '''
    return str1+str2+str3+str4

######################################## classes definition ####################################
request_iter_marcos = {"": ""}
request_iter_marcos_file = {"": ""}
response_iter_marcos = {"": ""}
response_iter_marcos_file = {"": ""}

request_iter_marcos_array_only = {"": ""}
request_iter_marcos_file_array_only = {"": ""}
response_iter_marcos_array_only = {"": ""}
response_iter_marcos_file_array_only = {"": ""}


response_number_marcos = {"": ""}
response_number_marcos_file = {"": ""}
response_number_marcos_noname_only = {"": ""}
response_number_marcos_file_noname_only = {"": ""}


def construct_request_iter_marco_rapidjson(vec_type, isArrayOnly):
    # print "construct_request_iter_marco-->" + vec_type
    normal_type = NORMAL_TYPE
    if isArrayOnly:
        common_str_head = "\tif(field.IsValueSet()) \\\n" \
                          "\t{ \\\n" \
                          "\t\trapidjson::Value& value = jsonObject; \\\n"
        common_str_foot = "\t}\n\n"
        request_macro_head = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                             "_ARRAY_ONLY(field, jsonObject, allocator) \\\n"
    else:
        common_str_head = "\tif(field.IsValueSet()) \\\n" \
                          "\t{ \\\n" \
                          "\t\trapidjson::Value value(rapidjson::kArrayType); \\\n"
        common_str_foot = "\t\tjsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), value, allocator); \\\n" \
                          "\t}\n\n"
        request_macro_head = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                             "_ARRAY(field, jsonObject, allocator) \\\n"

    request_macro = ""
    if vec_type in normal_type:    # Normal Type (Numbers)
        # print "Normal"
        request_macro = request_macro_head + \
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
        request_macro = request_macro_head + \
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
        request_macro = request_macro_head + \
                common_str_head + \
                "\t\tfor(std::vector<" + vec_type + ">::const_iterator it = field.GetValue().begin(); \\\n" \
                "\t\t\tit != field.GetValue().end(); \\\n" \
                "\t\t\tit++) \\\n" \
                "\t\t{ \\\n" \
                "\t\t\trapidjson::Value objectValue(rapidjson::kObjectType); \\\n" \
                "\t\t\tit->toJson(objectValue, allocator); \\\n" \
                "\t\t\tvalue.PushBack(objectValue, allocator); \\\n" \
                "\t\t} \\\n" + \
                common_str_foot
    if isArrayOnly:
        request_iter_marcos_file_array_only[vec_type] = request_macro
        request_iter_marcos_array_only[vec_type] = "TOJSON_REQUEST_FIELD_" + vec_type.upper() + "_ARRAY_ONLY"
    else:
        request_iter_marcos_file[vec_type] = request_macro
        request_iter_marcos[vec_type] = "TOJSON_REQUEST_FIELD_" + vec_type.upper() + "_ARRAY"


def construct_request_iter_marco_jsoncpp(vec_type, isArrayOnly):
    # print "construct_request_iter_marco-->" + vec_type
    normal_type = NORMAL_TYPE = ["string", "short", "int", "bool", "uint32_t", "uint64_t", "int64_t", "double"]
    common_str_head = "\tif(field.IsValueSet()) \\\n" \
                      "\t{ \\\n"
    if isArrayOnly:
        request_macro_head = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                             "_ARRAY_ONLY(field, jsonObject) \\\n"
        common_str_foot = "\t\t\tjsonObject.append(temp_value); \\\n" \
                          "\t\t} \\\n" \
                          "\t}\n\n"
    else:
        request_macro_head = "#define TOJSON_REQUEST_FIELD_" + vec_type.upper() + \
                             "_ARRAY(field, jsonObject) \\\n"
        common_str_foot = "\t\t\tjsonObject[field.GetName()].append(temp_value); \\\n" \
                          "\t\t} \\\n" \
                          "\t}\n\n"

    request_macro = ""
    if vec_type in normal_type:    # Normal Type (Bool, Numbers, String)
        # print "Normal"
        request_macro = request_macro_head + \
                common_str_head + \
                "\t\tfor(std::vector<" + vec_type + ">::const_iterator it = field.GetValue().begin(); \\\n" \
                "\t\t\tit != field.GetValue().end(); \\\n" \
                "\t\t\tit++) \\\n" \
                "\t\t{ \\\n" \
                "\t\t\tJson::Value temp_value = *it; \\\n" + \
                common_str_foot
    else:
        # print "Object"
        request_macro = request_macro_head + \
                common_str_head + \
                "\t\tfor(std::vector<" + vec_type + ">::const_iterator it = field.GetValue().begin(); \\\n" \
                "\t\t\tit != field.GetValue().end(); \\\n" \
                "\t\t\tit++) \\\n" \
                "\t\t{ \\\n" \
                "\t\t\tJson::Value temp_value; \\\n" \
                "\t\t\tit->toJson(temp_value); \\\n" + \
                common_str_foot
    if isArrayOnly:
        request_iter_marcos_file_array_only[vec_type] = request_macro
        request_iter_marcos_array_only[vec_type] = "TOJSON_REQUEST_FIELD_" + vec_type.upper() + "_ARRAY_ONLY"
    else:
        request_iter_marcos_file[vec_type] = request_macro
        request_iter_marcos[vec_type] = "TOJSON_REQUEST_FIELD_" + vec_type.upper() + "_ARRAY"


def construct_request_iter_marco(jsonAPI, vector_type, isArrayOnly):
    if jsonAPI == JSON_API_RAPIDJSON:
        return construct_request_iter_marco_rapidjson(vector_type, isArrayOnly)
    elif jsonAPI == JSON_API_JSONCPP:
        return construct_request_iter_marco_jsoncpp(vector_type, isArrayOnly)
    else:
        return ""


def construct_response_iter_marco_rapidjson(vec_type, isArrayOnly):
    # print "construct_request_iter_marco-->" + vec_type
    normal_type = NORMAL_TYPE

    if isArrayOnly:
        response_macro_head = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                              "_ARRAY_ONLY(values, field) \\\n"
        common_str_head = "\tif(values.IsArray()) \\\n" \
                          "\t{ \\\n"
        iter_c_str_head = "\t\tconst rapidjson::Value& val = values; \\\n" \
                          "\t\tfor (rapidjson::Value::ConstValueIterator itr = val.Begin(); itr != val.End(); ++itr) \\\n" \
                          "\t\t{ \\\n"
    else:
        response_macro_head = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                              "_ARRAY(values, field) \\\n"
        common_str_head = "\tif(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()]." \
                          "IsArray()) \\\n" \
                          "\t{ \\\n"
        iter_c_str_head = "\t\tconst rapidjson::Value& val = values[field.GetName().c_str()]; \\\n" \
                          "\t\tfor (rapidjson::Value::ConstValueIterator itr = val.Begin(); itr != val.End(); ++itr) \\\n" \
                          "\t\t{ \\\n"

    iter_c_str_foot = "\t\t} \\\n"
    common_str_foot = "\t\tfield.SetValue(vec); \\\n" \
                      "\t}\n\n"

    response_macro = ""
    if vec_type in normal_type:    # Normal Type (Numbers)
        # print "Normal"
        type_vec_push = ""
        if vec_type in ["short", "int"]:
            type_vec_push = "\t\t\tvec.push_back(itr->GetInt()); \\\n"
        if vec_type == "bool":
            type_vec_push = "\t\t\tvec.push_back(itr->GetBool()); \\\n"
        if vec_type == "double":
            type_vec_push = "\t\t\tvec.push_back(itr->GetDouble()); \\\n"
        if vec_type == "uint32_t":
            type_vec_push = "\t\t\tvec.push_back(itr->GetUint()); \\\n"
        if vec_type == "uint64_t":
            type_vec_push = "\t\t\tvec.push_back(itr->GetUint64()); \\\n"
        if vec_type == "int64_t":
            type_vec_push = "\t\t\tvec.push_back(itr->GetInt64()); \\\n"
        response_macro = response_macro_head + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                type_vec_push + \
                iter_c_str_foot + \
                common_str_foot

    elif vec_type == "string":
        # print "string"
        response_macro = response_macro_head + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\tvec.push_back(itr->GetString()); \\\n" + \
                iter_c_str_foot + \
                common_str_foot
    else:
        # print "Object"
        response_macro = response_macro_head + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\t" + vec_type + " typeVar; \\\n" + \
                "\t\t\ttypeVar.fromJson(*itr); \\\n" + \
                "\t\t\tvec.push_back(typeVar); \\\n" + \
                iter_c_str_foot + \
                common_str_foot
    if isArrayOnly:
        response_iter_marcos_file_array_only[vec_type] = response_macro
        response_iter_marcos_array_only[vec_type] = "FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + "_ARRAY_ONLY"
    else:
        response_iter_marcos_file[vec_type] = response_macro
        response_iter_marcos[vec_type] = "FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + "_ARRAY"


def construct_response_iter_marco_jsoncpp(vec_type, isArrayOnly):
    # print "construct_request_iter_marco-->" + vec_type
    normal_type = NORMAL_TYPE

    if isArrayOnly:
        response_macro_head = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                              "_ARRAY_ONLY(values, field) \\\n"
        common_str_head = "\tif(values.isArray()) \\\n" \
                          "\t{ \\\n"
        iter_c_str_head = "\t\tconst Json::Value& valArray = values; \\\n" \
                          "\t\tfor (int i = 0; i < valArray.size(); i++) \\\n" \
                          "\t\t{ \\\n" \
                          "\t\t\tconst Json::Value& val = valArray[i]; \\\n"
    else:
        response_macro_head = "#define FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + \
                              "_ARRAY(values, field) \\\n"
        common_str_head = "\tif(values.isMember(field.GetName()) && values[field.GetName()].isArray()) \\\n" \
                          "\t{ \\\n"
        iter_c_str_head = "\t\tconst Json::Value& valArray = values[field.GetName()]; \\\n" \
                          "\t\tfor (int i = 0; i < valArray.size(); i++) \\\n" \
                          "\t\t{ \\\n" \
                          "\t\t\tconst Json::Value& val = valArray[i]; \\\n"

    iter_c_str_foot = "\t\t} \\\n"
    common_str_foot = "\t\tfield.SetValue(vec); \\\n" \
                      "\t}\n\n"

    response_macro = ""
    if vec_type in normal_type:    # Normal Type (Numbers)
        # print "Normal"
        type_vec_push = ""
        if vec_type in ["short", "int"]:
            type_vec_push = "\t\t\tvec.push_back(val.asInt()); \\\n"
        if vec_type == "bool":
            type_vec_push = "\t\t\tvec.push_back(val.asBool()); \\\n"
        if vec_type == "double":
            type_vec_push = "\t\t\tvec.push_back(val.asDouble()); \\\n"
        if vec_type == "uint32_t":
            type_vec_push = "\t\t\tvec.push_back(val.asUInt()); \\\n"
        if vec_type == "uint64_t":
            type_vec_push = "\t\t\tvec.push_back(val.asUInt64()); \\\n"
        if vec_type == "int64_t":
            type_vec_push = "\t\t\tvec.push_back(val.asInt64()); \\\n"
        response_macro = response_macro_head + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                type_vec_push + \
                iter_c_str_foot + \
                common_str_foot

    elif vec_type == "string":
        # print "string"
        response_macro = response_macro_head + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\tvec.push_back(val.asString()); \\\n" + \
                iter_c_str_foot + \
                common_str_foot
    else:
        # print "Object"
        response_macro = response_macro_head + \
                common_str_head + \
                "\t\tvector<" + vec_type + "> vec; \\\n" + \
                iter_c_str_head + \
                "\t\t\t" + vec_type + " typeVar; \\\n" + \
                "\t\t\ttypeVar.fromJson(val); \\\n" + \
                "\t\t\tvec.push_back(typeVar); \\\n" + \
                iter_c_str_foot + \
                common_str_foot
    if isArrayOnly:
        response_iter_marcos_file_array_only[vec_type] = response_macro
        response_iter_marcos_array_only[vec_type] = "FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + "_ARRAY_ONLY"
    else:
        response_iter_marcos_file[vec_type] = response_macro
        response_iter_marcos[vec_type] = "FROMJSON_RESPONSE_FIELD_" + vec_type.upper() + "_ARRAY"


def construct_response_iter_marco(jsonAPI, vector_type, isArrayOnly):
    if jsonAPI == JSON_API_RAPIDJSON:
        return construct_response_iter_marco_rapidjson(vector_type, isArrayOnly)
    if jsonAPI == JSON_API_JSONCPP:
        return construct_response_iter_marco_jsoncpp(vector_type, isArrayOnly)
    else:
        return ""


def construct_response_number_marco_rapidjson(num_type, isNoNameOnly):
    condition = ""
    fieldset = ""
    filedHasName = ""
    fieldGetName = ""
    if not isNoNameOnly:
        filedHasName = "values.HasMember(field.GetName().c_str()) && "
        fieldGetName = "[field.GetName().c_str()]"
    if num_type in ["short", "int"]:
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".IsInt()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".GetInt()); \\\n"
    if num_type == "bool":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".IsBool()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".GetBool()); \\\n"
    if num_type == "double":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".IsDouble()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".GetDouble()); \\\n"
    if num_type == "uint32_t":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".IsUint()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".GetUint()); \\\n"
    if num_type == "uint64_t":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".IsUint64()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".GetUint64()); \\\n"
    if num_type == "int64_t":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".IsInt64()) \\\n"
    if isNoNameOnly:
        response_number_marcos_file_noname_only[num_type] = "#define FROMJSON_RESPONSE_FIELD_" + num_type.upper() + \
                                          "_NONAME_ONLY(values, field) \\\n" + \
                                          condition + "\t{ \\\n" + fieldset + "\t} \\\n\n"
        response_number_marcos_noname_only[num_type] = "FROMJSON_RESPONSE_FIELD_" + num_type.upper() + "_NONAME_ONLY"
    else:
        response_number_marcos_file[num_type] = "#define FROMJSON_RESPONSE_FIELD_" + num_type.upper() + \
                                          "(values, field) \\\n" + \
                                          condition + "\t{ \\\n" + fieldset + "\t} \\\n\n"
        response_number_marcos[num_type] = "FROMJSON_RESPONSE_FIELD_" + num_type.upper()


def construct_response_number_marco_jsoncpp(num_type, isNoNameOnly):
    condition = ""
    fieldset = ""
    filedHasName = ""
    fieldGetName = ""
    if not isNoNameOnly:
        filedHasName = "values.isMember(field.GetName()) && "
        fieldGetName = "[field.GetName()]"
    if num_type in ["short", "int"]:
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".isInt()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".asInt()); \\\n"
    if num_type == "bool":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".isBool()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".asBool()); \\\n"
    if num_type == "double":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".isDouble()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".asDouble()); \\\n"
    if num_type == "uint32_t":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".isUInt()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".asUInt()); \\\n"
    if num_type == "uint64_t":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".isUInt64()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".asUInt64()); \\\n"
    if num_type == "int64_t":
        condition = "\tif(" + filedHasName + "values" + fieldGetName + ".isInt64()) \\\n"
        fieldset = "\t\tfield.SetValue(values" + fieldGetName + ".asInt64()); \\\n"
    if isNoNameOnly:
        response_number_marcos_file_noname_only[num_type] = "#define FROMJSON_RESPONSE_FIELD_" + num_type.upper() + \
                                          "_NONAME_ONLY(values, field) \\\n" + \
                                          condition + "\t{ \\\n" + fieldset + "\t} \\\n\n"
        response_number_marcos_noname_only[num_type] = "FROMJSON_RESPONSE_FIELD_" + num_type.upper() + "_NONAME_ONLY"
    else:
        response_number_marcos_file[num_type] = "#define FROMJSON_RESPONSE_FIELD_" + num_type.upper() + \
                                          "(values, field) \\\n" + \
                                          condition + "\t{ \\\n" + fieldset + "\t} \\\n\n"
        response_number_marcos[num_type] = "FROMJSON_RESPONSE_FIELD_" + num_type.upper()


def construct_response_number_marco(jsonAPI, num_type, isNoNameOnly):
    if jsonAPI == JSON_API_RAPIDJSON:
        construct_response_number_marco_rapidjson(num_type, isNoNameOnly)
    if jsonAPI == JSON_API_JSONCPP:
        construct_response_number_marco_jsoncpp(num_type, isNoNameOnly)


class Field:
    def __init__(self):
        self.description = ""
        self.type = ""
        self.name = ""
        self.jsonname = ""
        self.default = ""
        self.default_isset = 0
        self.optional = 0
        self.is_array_only = False

    def is_valid(self):
        # return self.type != "" and self.name != "" and self.jsonname != ""
        return self.type != "" and self.name != ""

    def get_field_type(self):
        if "vector" in self.type:
            return "VectorField<" + self.type + " >"
        else:
            return "Field<" + self.type + ">"

    def get_tojson_method(self):
        normal_type = NORMAL_TYPE
        if self.type in normal_type:
            return "TOJSON_REQUEST_FIELD_NUMBER"
        elif self.type == "string":
            return "TOJSON_REQUEST_FIELD_STRING"
        elif "vector" in self.type:
            vector_type = self.type
            vector_type = vector_type.strip("vector").strip("<").strip(">")
            if self.jsonname == "":
                isArrayOnly = True
                if vector_type not in request_iter_marcos_array_only:
                    construct_request_iter_marco(JSON_API, vector_type, isArrayOnly)
                return request_iter_marcos_array_only[vector_type]
            else:
                isArrayOnly = False
                if vector_type not in request_iter_marcos:
                    construct_request_iter_marco(JSON_API, vector_type, isArrayOnly)
                return request_iter_marcos[vector_type]
        else:
            return "TOJSON_REQUEST_FIELD_OBJECT"

    def get_fromjson_method(self):
        if self.type in NORMAL_TYPE:
            isNoNameOnly = False
            if self.jsonname == "":
                isNoNameOnly = True
                if self.type not in response_number_marcos_noname_only:
                    construct_response_number_marco(JSON_API, self.type, isNoNameOnly)
                return response_number_marcos_noname_only[self.type]
            else:
                if self.type not in response_number_marcos:
                    construct_response_number_marco(JSON_API, self.type, isNoNameOnly)
                return response_number_marcos[self.type]
        elif self.type == "string":
            if self.jsonname == "":
                return "FROMJSON_RESPONSE_FIELD_STRING_NONAME_ONLY"
            else:
                return "FROMJSON_RESPONSE_FIELD_STRING"
        elif "vector" in self.type:
            vector_type = self.type
            vector_type = vector_type.strip("vector").strip("<").strip(">")
            if self.jsonname == "":
                isArrayOnly = True
                if vector_type not in response_iter_marcos_array_only:
                    construct_response_iter_marco(JSON_API, vector_type, isArrayOnly)
                return response_iter_marcos_array_only[vector_type]
            else:
                isArrayOnly = False
                if vector_type not in response_iter_marcos:
                    construct_response_iter_marco(JSON_API, vector_type, isArrayOnly)
                return response_iter_marcos[vector_type]
        else:
            return "FROMJSON_RESPONSE_FIELD_OBJECT"

    def dump_declaration(self):
        str = ""
        if self.is_valid():
            str = "\t" + self.get_field_type() + "\t\t\tm_" + self.name + ";"
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
            if JSON_API == JSON_API_RAPIDJSON:
                str = "\t\t" + self.get_tojson_method() + "(m_" + self.name + ", root, allocator);\n"
            elif JSON_API == JSON_API_JSONCPP:
                str = "\t\t" + self.get_tojson_method() + "(m_" + self.name + ", root);\n"
        return str

    def dump_fromjson(self):
        str = ""
        if self.is_valid():
            str = "\t\t\t\t\t" + self.get_fromjson_method() + "(values, m_" + self.name + ");\n"
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
        self.father = ""

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

    def dump_init(self):
        init_str = ""
        for field in self.fields:
            init_str += field.dump_init()
        init_str += "\n"
        init_str += self.dump_constructor()
        return init_str

    def dump_constructor(self):
        str = u""
        for field in self.fields:
            isquoted = "\"" if field.type == "string" else ""
            if field.default_isset == 1:
                str = str + "\t\tm_" + field.name + ".SetValue(" + isquoted + field.default.decode("gbk").encode("utf-8") + isquoted + ");\n"
        return str

    def is_array_only(self):
        for field in self.fields:
            if field.is_array_only:
                if len(self.fields) == 1:
                    return True
                else:
                    print "Request/Response anonymous Array (jsonname=\"\") MUST be defined once, now there are:" \
                          + len(self.fields)
                    exit(-1)
        return False


class Request(FieldCollector):
    def dump_tojson(self):
        str = ""
        for field in self.fields:
            str += field.dump_tojson()
        return str

    def dump_to_json_header(self):
        return build_TOJSON_HEADER(JSON_API, self.is_array_only(), self.father != "")

    def dump_to_json_func(self):
        to_json_str = self.dump_to_json_header() \
                    + self.dump_tojson() \
                    + TOJSON_FOOTER + "\n"
        return to_json_str

    def dump_request_class_header(self, interface_name):
        header = "class " + interface_name + "Request: public IRequest"
        if self.father != "":
            header = header + ", public " + self.father
        header += "\n{\n"
        return header

    def dump_constructor_header(self, interface_name):
        header = "\npublic:\n" + \
                 "\t" + interface_name + "Request()\n" + \
                 "\t\t:IRequest()"
        if self.father != "":
            header = header + ", " + self.father + "()"
        header += "\n"
        return header

    def dump_request_is_valid(self):
        is_valid_str = ISVALID_HEADER
        if self.father != "":
            is_valid_str = is_valid_str + "\t\tCHECK_FIELD_ISVALID_FATHER(" + self.father + ", strErrMsg);\n"
        is_valid_str = is_valid_str + self.dump_isvalid() + ISVALID_FOOTER
        return is_valid_str


class Response(FieldCollector):
    def __init__(self):
        FieldCollector.__init__(self)
        self.type = "json"

    def dump_fromjson(self):
        str = ""
        for field in self.fields:
            str += field.dump_fromjson()
        return str

    def dump_response_class_header(self, interface_name):
        header = "class " + interface_name + "Response: public IResponse"
        if self.father != "":
            header = header + ", public " + self.father
        header += "\n{\n"
        return header

    def dump_constructor_header(self, interface_name):
        header = "\npublic:\n" + \
                 "\t" + interface_name + "Response()\n" + \
                 "\t\t:IResponse()"
        if self.father != "":
            header = header + ", " + self.father + "()"
        header += "\n"
        return header

    def dump_init_func(self):
        init_str = INIT_HEADER + "\t\tIResponse::Init();\n\n"
        if self.father != "":
            init_str = init_str + "\t\t" + self.father + "::Init();\n"
        init_str = init_str + self.dump_init() + INIT_FOOTER + "\n"
        return init_str

    def dump_response_is_valid(self):
        is_valid_str = ISVALID_HEADER + RESPONSE_INVALID_HEADER + "\n"
        if self.father != "":
            is_valid_str = is_valid_str + "\t\tCHECK_FIELD_ISVALID_FATHER(" + self.father + ", strErrMsg);\n"
        is_valid_str = is_valid_str + self.dump_isvalid() + ISVALID_FOOTER
        return is_valid_str

    def dump_fromjson_func(self):
        from_json_str = build_FROMJSON_HEADER(JSON_API, self.father != "") \
                        + self.dump_fromjson() \
                        + build_FROMJSON_FOOTER(JSON_API, self.type) + "\n"
        return from_json_str


class Class(FieldCollector):
    def __init__(self):
        FieldCollector.__init__(self)
        self.description = ""
        self.name = ""

    def dump_to_json(self):
        str = ""
        for field in self.fields:
            str += field.dump_tojson()
        class_tojson_header = ""
        if JSON_API == JSON_API_RAPIDJSON:
            class_tojson_header = CLASS_TOJSON_HEADER_RAPIDJSON
        elif JSON_API == JSON_API_JSONCPP:
            class_tojson_header = CLASS_TOJSON_HEADER_JSONCPP
        to_json_method = class_tojson_header \
            + str \
            + CLASS_TOJSON_FOOTER

        return to_json_method

    def dump_from_json(self):
        str = ""
        for field in self.fields:
            str += field.dump_fromjson()
        class_fromjson_header = ""
        if JSON_API == JSON_API_RAPIDJSON:
            class_fromjson_header = CLASS_FROMJSON_HEADER_RAPIDJSON
        elif JSON_API == JSON_API_JSONCPP:
            class_fromjson_header = CLASS_FROMJSON_HEADER_JSONCPP
        from_json_method = class_fromjson_header \
            + str \
            + CLASS_FROMJSON_FOOTER
        return from_json_method

    def dump_to_json_header(self):
        return build_TOJSON_HEADER(JSON_API, self.is_array_only(), self.father != "")

    def dump_ToJson_body(self, jsonAPI):
        body = ""
        if jsonAPI == JSON_API_RAPIDJSON:
            body = "\t\tthis->toJson(root, allocator);\n"
        elif jsonAPI == JSON_API_JSONCPP:
            body = "\t\tthis->toJson(root);\n"
        return body

    def dump_ToJson_func(self):
        to_json_str = self.dump_to_json_header() \
                    + self.dump_ToJson_body(JSON_API) \
                    + TOJSON_FOOTER + "\n"
        return to_json_str

    def dump_FromJson_func(self, jsonAPI):
        return build_CLASS_FROMJSON_HEADER(jsonAPI)

    def dump_init_func(self):
        init_str = INIT_HEADER
        if self.father != "":
            init_str = init_str + "\t\t" + self.father + "::Init();\n"
        init_str = init_str + self.dump_init() \
                + INIT_FOOTER + "\n"
        return init_str

    @property
    def dump(self):
        init_list = self.dump_initialize_list()
        init_list = list(init_list)
        init_list[2] = " "
        init_list = "".join(init_list)
        class_str = "//" + self.description.decode("gbk") + "\n"
        class_str = class_str + "class " + self.name + "\n{\n" \
            + self.dump_declaration() \
            + "\npublic:\n" \
            + "\t" + self.name + "() : \n" \
            + init_list \
            + "\t{\n" \
            + self.dump_constructor() \
            + "\t}\n\n" \
            + "\tvirtual ~" + self.name + "(){}\n\n" \
            + self.dump_to_json() \
            + self.dump_from_json() \
            + ISVALID_HEADER \
            + self.dump_isvalid() \
            + ISVALID_FOOTER \
            + self.dump_ToJson_func() \
            + self.dump_FromJson_func(JSON_API) \
            + self.dump_init_func() \
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
        request_str = self.request.dump_request_class_header(self.name) \
            + self.request.dump_declaration() \
            + self.request.dump_constructor_header(self.name) \
            + self.request.dump_initialize_list() \
            + "\t{\n" \
            + self.request.dump_constructor() \
            + "\t}\n\n" \
            + "\tvirtual ~" + self.name + "Request()\n\t{}\n\n" \
            + self.request.dump_to_json_func() \
            + self.request.dump_request_is_valid() \
            + "};"

        response_str = self.response.dump_response_class_header(self.name) \
            + self.response.dump_declaration() \
            + self.response.dump_constructor_header(self.name) \
            + self.response.dump_initialize_list() \
            + "\t{\n" \
            + self.response.dump_constructor() \
            + "\t}\n\n" \
            + "\tvirtual ~" + self.name + "Response()\n\t{}\n\n" \
            + self.response.dump_init_func() \
            + self.response.dump_fromjson_func() \
            + self.response.dump_response_is_valid() \
            + "};"

        return "//" + self.description.decode("gbk") + "\n" + request_str + "\n\n" + response_str


def key_value_field(keyName):
    equal = Suppress("=")
    return Group(keyName + equal + quotedString)


######################################## parse  tokens ####################################
def load_grammar():
    lbrace = Suppress("{")
    rbrace = Suppress("}")
    lbracket = Suppress("(")
    rbracket = Suppress(")")
    semicolon = Suppress(";")
    at = Suppress("@")
    comma = Suppress(",")
    equal = Suppress("=")
    nspace = Suppress("::")
    keyword = Word(alphanums + "_/")
    interface_key = Keyword("Interface")
    class_key = Keyword("class")
    namespace_key = Keyword("namespace")
    request_key = Keyword("Request")
    response_key = Keyword("Response")
    jsonname_key = Keyword("jsonname")
    description_key = Keyword("description")
    optional_key = Keyword("optional")
    default_key = Keyword("default")

    field_type = Word(alphanums + "_/<>")
    namespace = Group(namespace_key + keyword + ZeroOrMore(nspace + keyword) + semicolon)
    description = Group(at + description_key + equal + quotedString)
    jsonname = Group(at + jsonname_key + equal + quotedString)
    comment = Group(jsonname + Optional(comma + key_value_field(description_key)) \
                      + Optional(comma + key_value_field(optional_key)) \
                      + Optional(comma + key_value_field(default_key)))
    field = Group(comment + field_type + keyword + semicolon)
    request_nal = Group(request_key + lbrace + OneOrMore(field) + rbrace + semicolon)
    request_inh = Group(request_key + lbracket + field_type + rbracket + lbrace + ZeroOrMore(field) + rbrace + semicolon)
    request = request_nal | request_inh
    response_nal = Group(response_key + lbrace + OneOrMore(field) + rbrace + semicolon)
    response_inh = Group(response_key + lbracket + field_type + rbracket + lbrace + ZeroOrMore(field) + rbrace + semicolon)
    response_string = Group(response_key + lbracket + rbracket + lbrace + rbrace + semicolon)
    response = response_nal | response_inh | response_string
    interface = Group(Optional(description) \
        + interface_key + keyword + lbrace \
        + request \
        + response\
        + rbrace + semicolon)

    classGram = Group(Optional(description) \
        + class_key + keyword + lbrace \
        + OneOrMore(field) \
        + rbrace + semicolon)

    grammar = ZeroOrMore(namespace) + ZeroOrMore(classGram) + OneOrMore(interface)
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
            print "[error] Parsing Class token failed: class key word not found!"
    else:
        classField.description = parse_description(class_token[0])
        description_dis = 1

    # class name
    class_name = class_token[description_dis + 1]
    if type(class_name) != str:
        print u"[error] class name <" + class_name + u">should be str type, but now: " + type(class_name)
        return
    classField.name = class_name

    # class fields
    for i in range(class_token_len):
        if i <= description_dis + 1:
            # class keyword & class name
            pass
        else:
            field = parse_field(class_token[i])
            if isinstance(field, Field) and field.is_valid():
                classField.fields.append(field)
    return classField


def parse_interface(interface_token):
    if type(interface_token) != list:
        print u"[error] Unsupported interface_token type:<" + type(interface_token) + u">"
        print interface_token

    interface = Interface()
    interface_token_len = len(interface_token)

    # interface description
    description_dis = 0
    if 5 == interface_token_len:    # Have Comments here
        interface.description = parse_description(interface_token[0])
        description_dis = 1
    elif interface_token_len != 4:
        print u"[error] Expected interface_token_len is [4-5], actually is: " + str(interface_token_len)
        print interface_token
        return

    # interface keyword
    # interface_token[description_dis]

    # interface name
    interface_name = interface_token[description_dis + 1]
    if type(interface_name) != str:
        print u"[error] Interface name <" + interface_name + u">should be str type, but now: " + type(interface_name)
        return
    interface.name = interface_name

    # interface request
    interface_request = interface_token[description_dis + 2]
    interface.request = parse_request(interface_request)

    # interface response
    interface_response = interface_token[description_dis + 3]
    if type(interface_response) != list:
        print u"[error] Invalid response type." + type(interface_response)
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
        keyName = tokens[m][0]
        if keyName == "jsonname":
            key_value["jsonname"] = parse_key_value_field(tokens[m])
        elif keyName == "description":
            key_value["description"] = parse_key_value_field(tokens[m])
        elif keyName == "optional":
            key_value["optional"] = parse_key_value_field(tokens[m])
        elif keyName == "default":
            key_value["default"] = parse_key_value_field(tokens[m])
        else:
            print u"[warn] Invalid comment filed:" + keyName +", ignored!"
    return key_value


def parse_request(request_tokens):
    if type(request_tokens) != list:
        print u"[error] Wrong request/response type define: " + str(type(request_tokens))
        print request_tokens
        return

    request_token_len = len(request_tokens)
    if request_token_len < 2:
        print u"[error] Unexpected end field of request/response, expected:[>=2], actual:" + str(request_token_len)
        print request_tokens
        return

    request = Request()
    for i in range(request_token_len):
        if i == 0:
            # request/response keyword
            pass
        elif type(request_tokens[i]) == str and i == 1:
            request.father = request_tokens[i]
        else:
            field = parse_field(request_tokens[i])
            if isinstance(field, Field) and field.is_valid():
                request.fields.append(field)
    return request


def parse_response(response_tokens):
    if type(response_tokens) != list:
        print u"[error] Wrong request/response type define: " + str(type(response_tokens))
        print response_tokens
        return

    response_token_len = len(response_tokens)
    if response_token_len < 2:
        print u"[error] Unexpected end field of request/response, expected:[>=2], actual:" + str(response_token_len)
        print response_tokens
        return

    response = Response()
    for i in range(response_token_len):
        if i == 0:
            # request/response keyword
            pass
        elif type(response_tokens[i]) == str and i == 1:
            if response_tokens[i] == "string":#特殊处理：继承自string,表示服务器返回的是匿名string，对应的为该response自动添加一个匿名的string类型字段
                field = Field()
                field.name = "result"
                field.type = "string"
                field.description = u"自动添加的字段，用来接收服务器返回的string类型结果,用户可根据实际需要转成其他类型(int等)".decode("utf8").encode("gbk")
                field.jsonname = "result"
                field.optional = "false"
                response.fields.append(field)
                response.type  = "string"
            else:#继承自其他类
                response.father = response_tokens[i]
        else:
            field = parse_field(response_tokens[i])
            if isinstance(field, Field) and field.is_valid():
                response.fields.append(field)
    return response


def parse_field(field_tokens):
    if type(field_tokens) != list:
        print u"[error] Wrong field type, field_tokens is not list: " + str(type(field_tokens))
        print field_tokens
        return

    field_token_len = len(field_tokens)
    if field_token_len != 3:
        print u"[error]expected field_token_len should be 3, actually is: " + str(field_token_len)
        print field_tokens
        return

    field = Field()

    # comment
    jsonname_field_tokens = field_tokens[0]
    if type(jsonname_field_tokens) != list:
        print u"[error] Wrong jsonname_field_tokens type: " + str(type(jsonname_field_tokens))
        print jsonname_field_tokens
        return

    key_values = parse_to_key_value_field_arrays(jsonname_field_tokens)
    # Allow jsonname to be "" for Array Only
    # if key_values["jsonname"] == "":
    #     print u"[error] jsonname field is NULL!"
    #     print jsonname_field_tokens
    #     return
    field.jsonname = key_values["jsonname"]
    if field.jsonname == "":
        field.is_array_only = True

    if "description" in key_values and key_values["description"] != "":
        field.description = key_values["description"]

    if "optional" in key_values and key_values["optional"] == "true":
        field.optional = 1

    # if "default" in key_values and key_values["default"] != "":
    if "default" in key_values:
        field.default = key_values["default"]
        field.default_isset = 1

    # field type
    field_type_token = field_tokens[1]
    if type(field_type_token) != str:
        print u"[error] Wrong field type, NOT str: " + str(type(field_type_token))
        print field_type_token
        return
    field.type = field_type_token
    if field.jsonname == "" and (field.type not in NORMAL_TYPE and field.type != "string" and "vector" not in field.type):
        print u"[error] jsonname == \"\" only when type is not an Object! but now type is: " + field.type
        exit(-1)

    # field name
    field_name_token = field_tokens[2]
    if type(field_name_token) != str:
        print u"[error] Wrong field_name type: " + str(type(field_name_token))
        print field_name_token
        return
    field.name = field_name_token

    return field


'''
################################ generate c++ files ####################################
'''
def get_namespace_str():
    str = ""
    return str


def write_file(file_name, content):
    print "Generating " + file_name + "..."

    #vs2010 can not read files encoded with utf-8(without BOM)
    #fuck
    file = codecs.open(file_name, "w", "utf_8_sig") if platform.system() == "Windows" else open(file_name, "w")
    file.write(content.encode("utf-8"))
    file.close()


def generate_base(base_directory, class_objects):
    #base.h
    BASE_H = build_BASE_H(JSON_API)
    write_file(base_directory + os.sep + "base.h", BASE_H)

    #macro.h
    # macros for tojson/fromjson array handling
    macros = build_MACRO_H_BASE(JSON_API)
    for req_macros in request_iter_marcos_file:
        macros += request_iter_marcos_file[req_macros]
    for res_macros in response_iter_marcos_file:
        macros += response_iter_marcos_file[res_macros]
    for req_macros_al in request_iter_marcos_file_array_only:
        macros += request_iter_marcos_file_array_only[req_macros_al]
    for res_macros_al in response_iter_marcos_file_array_only:
        macros += response_iter_marcos_file_array_only[res_macros_al]
    for res_num_macros in response_number_marcos_file:
        macros += response_number_marcos_file[res_num_macros]
    for res_num_macros in response_number_marcos_file_noname_only:
        macros += response_number_marcos_file_noname_only[res_num_macros]
    macros += "\n#endif	/* JSON2CPP_MACRO_H */\n"
    write_file(base_directory + os.sep + "macro.h", macros)

    #json2cpp.h
    include_str = """
#include "base.h"
#include "macro.h"

"""

    for object in class_objects:
        include_str += "#include \"" + object.name + ".h\"\n"

    write_file(base_directory + os.sep + "json2cpp.h", include_str)

    if JSON_API == JSON_API_RAPIDJSON:
        # rapidjson library
        if not os.path.exists(rapidjson_path):
            print u"[Warning] rapidjson lirary dose not exist. Please download from https://github.com/miloyip/rapidjson"
            return
        if not os.path.isdir(rapidjson_path):
            print u"[error] rapidjson path is not directory." + os.path.abspath(rapidjson_path)
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


#generate and interface(a type of class)
def generate_class(base_directory, namespace, object):
    namespace_str = ""
    file_footer = "\n"

    # handle namespace
    if namespace:
        for name in namespace:
            namespace_str = namespace_str + "namespace " + name + " { "
            file_footer += "} "
        namespace_str += "\n\n"
        file_footer += "\n"

    # Construct Header #define
    file_header = FILE_HEADER
    file_header = "/*\n" + \
                " * File:   " + object.name + ".h\n" + \
                " * Author: json2cpp\n" + \
                " *\n" + \
                " * Created on " + current_time + "\n" + \
                " */\n\n" + \
                "#ifndef JSON2CPP_" + object.name.upper() + "_H\n" + \
                "#define JSON2CPP_" + object.name.upper() + "_H\n\n" + \
                file_header
    file_footer += "#endif	/* JSON2CPP_" + object.name.upper() + "_H */\n"

    content = file_header + namespace_str + object.dump + file_footer
    write_file(base_directory + os.sep + object.name + ".h", content)


def generate_files(tokens, base_dir):
    if type(tokens) != list or len(tokens) < 1:
        print u"[error] Invalid tokens. type:" + type(tokens) + ", len:" + len(tokens)
        print tokens
        return

    class_objects = []
    interface_objects = []

    namespace_str = ""
    base_directory = base_dir

    # for token in tokens:
    for i in range(len(tokens)):
        token = tokens[i]
        # print token
        if (type(token[0]) == list and token[1] == "class") or token[0] == "class":
            class_object = parse_class(token)
            class_objects.append(class_object)
        elif (type(token[0]) == list and token[1] == "Interface") or token[0] == "Interface":
            interface = parse_interface(token)
            interface_objects.append(interface)
        elif token[0] == "namespace":
            if i != 0:
                print "[error] Namespace must be first token!"
                exit(-1)
            namespace = parse_namespace(token, base_dir)
            if namespace != "":
                namespace_str = namespace[0]
                base_directory = namespace[1]
        else:
            print "[error] Parsing token failed! No class or Interface key word find!"
            exit(-1)

    # Create dir by namespace
    if not os.path.exists(base_directory):
        try:
            os.makedirs(base_directory)
        except OSError, why:
            print u"[error] Failed to create directory:" + os.path.abspath(base_directory)
            exit(-1)
    print "Generating code in directory: \"" + base_directory + "\""

    for object in class_objects + interface_objects:
        generate_class(base_directory, namespace_str, object)

    # base files
    generate_base(base_directory, class_objects + interface_objects)


'''
##################################      main           ####################################
'''
def usage():
    print "json2cpp {rapidjson/jsoncpp} {grammar_file} {generated_directory}"


def parse_param(argv):
    grammar_file = argv[2]
    base_directory = argv[3]

    if not os.path.exists(grammar_file):
        print u"[error]file dose not exist:" + os.path.abspath(grammar_file)
        exit(-1)

        if not os.path.isfile(grammar_file):
            print u"[erorr]" + os.path.abspath(grammar_file) + u" is not a valid file."
            exit(-1)

    return os.path.abspath(grammar_file)


def parse_jsonapi(argv):
    api = argv[1]
    if api == JSON_API_RAPIDJSON:
        return JSON_API_RAPIDJSON
    elif api == JSON_API_JSONCPP:
        return JSON_API_JSONCPP
    else:
        print "[error] Json API should be \"rapidjson\" or \"jsoncpp\""
        exit(-1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()
        exit(-1)

    file_path = parse_param(sys.argv)
    JSON_API = parse_jsonapi(sys.argv)
    grammar = load_grammar()
    tokens = grammar.parseFile(file_path).asList()
    generate_files(tokens, sys.argv[3])
    print current_time
