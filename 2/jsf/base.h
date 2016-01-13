/*
 * File:   base.h
 * Author: raozf
 *
 * Created on 2015年5月20日, 下午4:26
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
