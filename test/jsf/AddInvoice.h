#include "base.h"
namespace json2cpp{

class Address
{
public:
	Field<int>			m_provinceNo;				//地址编号
	Field<string>			m_province;				//省
	Field<string>			m_city;				//市
	Field<string>			m_town;				//区县镇
	Field<string>			m_address;				//详细地址

public:
	Address() : 
		 m_provinceNo("provinceNo", true)
		,m_province("provinceStr", true)
		,m_city("city", true)
		,m_town("town", true)
		,m_address("address", true)
	{}

	~Address(){}

	void ToJson(rapidjson::Value& root, rapidjson::Document::AllocatorType& allocator) const
    {

		TOJSON_REQUEST_FIELD_INT(m_provinceNo, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_province, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_city, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_town, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_address, root, allocator);

    }

    void FromJson(const rapidjson::Value& values)
    {

			FROMJSON_RESPONSE_FIELD_NUMBER(values, m_provinceNo);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_province);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_city);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_town);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_address);

    }

};

class InvoiceTicket
{
public:
	Field<string>			m_invoiceType;				//发票类型
	Field<string>			m_invoiceCode;				//发票代码
	Field<string>			m_invoiceNo;				//发票号码
	Field<string>			m_amount;				//开票金额
	Field<string>			m_invoiceTime;				//开票时间
	Field<string>			m_state;				//状态
	Field<string>			m_bussinessId;				//订单号
	Field<string>			m_operatorCode;				//开票人
	Field<string>			m_operatorName;				//开票人名称
	Field<Address>			m_address;				//发票地址
	VectorField<vector<Address> >			m_optionalAddress;				//备选发票地址

public:
	InvoiceTicket() : 
		 m_invoiceType("invoiceType", true)
		,m_invoiceCode("invoiceCode", true)
		,m_invoiceNo("invoiceNo", true)
		,m_amount("amount", true)
		,m_invoiceTime("invoiceTime", true)
		,m_state("state", true)
		,m_bussinessId("bussinessId", true)
		,m_operatorCode("operatorCode", true)
		,m_operatorName("operatorName", true)
		,m_address("invoiceAddress", true)
		,m_optionalAddress("optionalAddress", true)
	{}

	~InvoiceTicket(){}

	void ToJson(rapidjson::Value& root, rapidjson::Document::AllocatorType& allocator) const
    {

		TOJSON_REQUEST_FIELD_STRING(m_invoiceType, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_invoiceCode, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_invoiceNo, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_amount, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_invoiceTime, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_state, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_bussinessId, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_operatorCode, root, allocator);
		TOJSON_REQUEST_FIELD_STRING(m_operatorName, root, allocator);
		TOJSON_REQUEST_FIELD_OBJECT(m_address, root, allocator);
		TOJSON_REQUEST_FIELD_ADDRESS_ARRAY(m_optionalAddress, root, allocator);

    }

    void FromJson(const rapidjson::Value& values)
    {

			FROMJSON_RESPONSE_FIELD_STRING(values, m_invoiceType);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_invoiceCode);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_invoiceNo);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_amount);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_invoiceTime);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_state);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_bussinessId);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_operatorCode);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_operatorName);
			FROMJSON_RESPONSE_FIELD_OBJECT(values, m_address);
			FROMJSON_RESPONSE_FIELD_ADDRESS_ARRAY(values, m_optionalAddress);

    }

};

class AddInvoiceRequest: public IRequest
{
public:
	Field<int>			m_source;				//来源
	Field<int>			m_organizationId;				//开票机构
	Field<int>			m_invoiceType;				//开票类型
	Field<string>			m_requestNo;				//申请单号
	Field<string>			m_payNo;				//付款方识别号
	Field<string>			m_receiverNo;				//收款方识别号
	VectorField<vector<string> >			m_bussinessIds;				//订单列表
	Field<InvoiceTicket>			m_invoiceTicket;				//发票

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
		,m_invoiceTicket("invoiceTicket", true)
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
		TOJSON_REQUEST_FIELD_STRING_ARRAY(m_bussinessIds, root, allocator);
		TOJSON_REQUEST_FIELD_OBJECT(m_invoiceTicket, root, allocator);

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
		CHECK_REQUEST_FIELD(m_invoiceTicket, strErrMsg);

        return true;
    }
};

class AddInvoiceResponse: public IResponse
{
public:
	Field<string>			m_code;				//业务返回代码
	Field<string>			m_message;				//业务返回信息
	Field<string>			m_requestNo;				//申请单号
	VectorField<vector<string> >			m_bussinessIds;				//订单列表
	Field<InvoiceTicket>			m_invoiceTicket;				//发票

public:
	AddInvoiceResponse()
		:IResponse()
		,m_code("code", true)
		,m_message("msg", true)
		,m_requestNo("reqNo", true)
		,m_bussinessIds("businessIds", false)
		,m_invoiceTicket("invoiceTicket", true)
	{}

	~AddInvoiceResponse()
	{}

   virtual void Init()
    {
        IResponse::Init();

		m_code.Clear();
		m_message.Clear();
		m_requestNo.Clear();
		m_bussinessIds.Clear();
		m_invoiceTicket.Clear();
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
            const rapidjson::Value& values = doc;
			FROMJSON_RESPONSE_FIELD_STRING(values, m_code);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_message);
			FROMJSON_RESPONSE_FIELD_STRING(values, m_requestNo);
			FROMJSON_RESPONSE_FIELD_STRING_ARRAY(values, m_bussinessIds);
			FROMJSON_RESPONSE_FIELD_OBJECT(values, m_invoiceTicket);

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
		CHECK_REQUEST_FIELD(m_bussinessIds, strErrMsg);
		CHECK_REQUEST_FIELD(m_invoiceTicket, strErrMsg);

        return true;
    }
};

}
