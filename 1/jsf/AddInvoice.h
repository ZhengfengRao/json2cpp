#include "base.h"
namespace json2cpp{

class AddInvoiceRequest: public IRequest
{
public:
	Field<int>			m_source;			//"来源"
	Field<int>			m_organizationId;			//"开票机构"
	Field<int>			m_invoiceType;			//"开票类型"
	Field<std::string>			m_requestNo;			//"申请单号"
	Field<std::string>			m_payNo;			//"付款方识别号"
	Field<std::string>			m_receiverNo;			//"收款方识别号"
	VectorField<std::vector<std::string> >			m_bussinessIds;			//"订单列表"

public:
	AddInvoiceRequest()
		:IRequest()
		,m_source("sourceId", true)
		,m_organizationId("orgId", true)
		,m_invoiceType("ivcType", true)
		,m_requestNo("reqNo", true)
		,m_payNo("payerNo", true)
		,m_receiverNo("receiverNo", false)
		,m_bussinessIds("businessIds", true)
	{}

	~AddInvoiceRequest()
	{}

     virtual uint32_t ToJson(std::string& strJson, std::string& strErrMsg) const
    {
        strJson = "";
        if(IsValid(strErrMsg) == false)
        {
            return ERR_REQUEST_FIELD_NOT_SET;
        }

        rapidjson::Document doc;
        rapidjson::Document::AllocatorType& allocator = doc.GetAllocator();
        rapidjson::Value root(rapidjson::kObjectType);

		TOJSON_REQUEST_FIELD_INT(m_source, root, allocator);
		TOJSON_REQUEST_FIELD_INT(m_organizationId, root, allocator);
		TOJSON_REQUEST_FIELD_INT(m_invoiceType, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_requestNo, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_payNo, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_receiverNo, root, allocator);
		TOJSON_REQUEST_FIELD_ARRAY(m_bussinessIds, root, allocator);

        JSONVALUE_TOSTRING(root, strJson);
        return ERR_OK;
    }

    virtual bool IsValid(std::string& strErrMsg) const
    {
		CHECK_REQUEST_FIELD(m_source, strErrMsg);
		CHECK_REQUEST_FIELD(m_organizationId, strErrMsg);
		CHECK_REQUEST_FIELD(m_invoiceType, strErrMsg);
		CHECK_REQUEST_FIELD(m_requestNo, strErrMsg);
		CHECK_REQUEST_FIELD(m_payNo, strErrMsg);
		CHECK_REQUEST_FIELD(m_receiverNo, strErrMsg);
		CHECK_REQUEST_FIELD(m_bussinessIds, strErrMsg);

        return true;
    }
};

class AddInvoiceResponse: public IResponse
{
public:
	Field<std::string>			m_code;			//"业务返回代码"
	Field<std::string>			m_message;			//"业务返回信息"
	Field<std::string>			m_requestNo;			//"申请单号"

public:
	AddInvoiceResponse()
		:IResponse()
		,m_code("code", true)
		,m_message("msg", true)
		,m_requestNo("reqNo", true)
	{}

	~AddInvoiceResponse()
	{}

   virtual void Init()
    {
        IResponse::Init();

		m_code.Clear();
		m_message.Clear();
		m_requestNo.Clear();
   }

   virtual uint32_t FromJson(const std::string& strJson, int status)
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
			FROMJSON_RESPONSE_FIELD_STRING(doc, m_code);
			FROMJSON_RESPONSE_FIELD_STRING(doc, m_message);
			FROMJSON_RESPONSE_FIELD_STRING(doc, m_requestNo);

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

    virtual bool IsValid(std::string& strErrMsg) const
    {
       if(!IResponse::IsValid(strErrMsg))
        {
            return false;
        }

		CHECK_REQUEST_FIELD(m_code, strErrMsg);
		CHECK_REQUEST_FIELD(m_message, strErrMsg);
		CHECK_REQUEST_FIELD(m_requestNo, strErrMsg);

        return true;
    }
};

}
