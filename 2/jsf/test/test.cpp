#include <iostream>
#include "AddInvoice.h"

void test_AddInvoiceRequest()
{
	std::cout << "--- test_AddInvoiceRequest [START]---" << std::endl;
	json2cpp::AddInvoiceRequest request;
	json2cpp::Address address;
	json2cpp::Address address1;
	json2cpp::Address address2;
	json2cpp::InvoiceTicket invoTic;
	
	address.m_provinceNo.SetValue(10001);
	address.m_province.SetValue("上海市");
	address.m_city.SetValue("上海");
	address.m_town.SetValue("徐汇区");
	address.m_address.SetValue("古美路1515号，凤凰大厦");

	address1.m_provinceNo.SetValue(10002);
	address1.m_province.SetValue("上海市");
	address1.m_city.SetValue("上海");
	address1.m_town.SetValue("青浦区");
	address1.m_address.SetValue("公园路100号");
	
	address2.m_provinceNo.SetValue(10003);
	address2.m_province.SetValue("四川省");
	address2.m_city.SetValue("成都市");
	address2.m_town.SetValue("双流区");
	address2.m_address.SetValue("双流机场");
	
	invoTic.m_invoiceType.SetValue("Normal");
	invoTic.m_invoiceCode.SetValue("200001");				//发票代码
	invoTic.m_invoiceNo.SetValue("13402512125");				//发票号码
	invoTic.m_amount.SetValue("400.00");				//开票金额
	invoTic.m_invoiceTime.SetValue("2016年1月14日");				//开票时间
	invoTic.m_state.SetValue("已开");				//状态
	invoTic.m_bussinessId.SetValue("100020003");				//订单号
	invoTic.m_operatorCode.SetValue("某人");				//开票人
	invoTic.m_operatorName.SetValue("某某人");				//开票人名称
	invoTic.m_address.SetValue(address);				//发票地址
	vector<json2cpp::Address> v_addr;
	v_addr.push_back(address1);
	v_addr.push_back(address2);
	invoTic.m_optionalAddress.SetValue(v_addr);
	
	request.m_source.SetValue(1);
    request.m_organizationId.SetValue(10);
    request.m_invoiceType.SetValue(100);
    request.m_requestNo.SetValue("asd");
    request.m_payNo.SetValue("10032-11");
    std::vector<std::string> bid;
    bid.push_back("saddd");
    bid.push_back("xxxx");
    request.m_bussinessIds.SetValue(bid);
	request.m_invoiceTicket.SetValue(invoTic);

	std::string str;
	std::string error;
    uint32_t ret = request.ToJson(str, error);

	if (json2cpp::ERR_OK != ret)
	{
		std::cout<<"error:"<<ret<<", "<<error<<std::endl;
		return;
	}
	
	std::cout << "result --->" << std::endl;
	std::cout<<str<<std::endl;
	std::cout << "--- test_AddInvoiceRequest [END]---" << std::endl << std::endl;
}

void test_AddInvoiceResponse()
{
    std::string str = "{\"code\":\"123\",\"msg\":\"fuck\",\"reqNo\":\"1029999\"}";
    uint32_t status = 200;

    json2cpp::AddInvoiceResponse response;
    uint32_t ret = response.FromJson(str, status);
    if(ret != json2cpp::ERR_OK)
    {
		std::cout<<"error:"<<ret<<", "<<response.m_JSFMessage.GetValue()<<std::endl;
		return;
	}

	std::cout<<response.m_code.GetValue()<<std::endl;
	std::cout<<response.m_message.GetValue()<<std::endl;
	std::cout<<response.m_requestNo.GetValue()<<std::endl;
}

int main()
{
    test_AddInvoiceRequest();
    test_AddInvoiceResponse();
}
