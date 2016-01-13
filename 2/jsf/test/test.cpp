#include <iostream>
#include "AddInvoice.h"

void test_AddInvoiceRequest()
{
	std::cout << "--- test_AddInvoiceRequest [START]---" << std::endl;
	json2cpp::AddInvoiceRequest request;
	request.m_source.SetValue(1);

    request.m_organizationId.SetValue(10);
    request.m_invoiceType.SetValue(100);
    request.m_requestNo.SetValue("asd");
    request.m_payNo.SetValue("10032-11");

    std::vector<std::string> bid;
    bid.push_back("saddd");
    bid.push_back("xxxx");
    request.m_bussinessIds.SetValue(bid);

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
