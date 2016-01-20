json2cpp
=======
![](https://img.shields.io/badge/release-0.01-blue.svg)
##A tool for Modelling JSON to C++
Copyright (C) 2016, ICSON company, ZhengFeng Rao, NASaCJ. All rights reserved.

## Build Status
|Platfrom| [Linux][lin-link] |
|:------:| :---------------: |
|Status  |[![Build Status](https://travis-ci.org/nasacj/json2cpp.svg?branch=master)](https://travis-ci.org/nasacj/json2cpp)|
[lin-link]: https://travis-ci.org/nasacj/json2cpp

## Introduction
[pyparsing-link]:http://pyparsing.wikispaces.com/
[rapidjson-link]:https://github.com/miloyip/rapidjson
[jsoncpp-link]:https://github.com/open-source-parsers/jsoncpp
[python-link]:https://www.python.org/
[setuptools-link]:https://pypi.python.org/pypi/setuptools

JSON is a kind of **Object** notation. When programmers deal with the json strings by C++ json APIs (eg, [RapidJSON][rapidjson-link], [jsoncpp][jsoncpp-link]) they have to write codes for parsing each different Class, which there may be a lot of similar repeated API calling codes.
So json2cpp can help programmer to auto-generate the C++ codes for transferring form JSON to C++ and conversely.
json2cpp is a script tool written in python language. It uses [pyparsing][pyparsing-link] to parse a Modeling file to C++ files and [RapidJSON][rapidjson-link], [jsoncpp][jsoncpp-link] for C++ to parse the JSON.

##Installation before use
* json2cpp depends on Python and pyparsing, so make sure that [Python][python-link] has been installed on your System
* For installing  [pyparsing][pyparsing-link], use "[easy_install][setuptools-link]" to install it through command line:
``` shell
user@localhost $ sudo easy_install pyparsing
```
##Download & Run Sample
Thie simple instruction shows a common running command of json2cpp
``` shell
git clone https://github.com/nasacj/json2cpp
cd json2cpp
./json2cpp.py rapidjson sample.jsf test
cd test/test
make
./test
```

##Usage
Before use json2cpp, a definition file is required:
###Define the class
As sample.jsf file shows, user can define the class structure as C++ sytle. The classes are according to the JSON objects:

####Sample JSON Object for Request
``` json
{
    "sourceId": 1,
    "orgId": 10,
    "ivcType": 100,
    "reqNo": "asd",
    "payerNo": "10032-11",
    "businessIds": [
        "saddd",
        "xxxx"
    ],
    "invoiceTicket": {
        "invoiceType": "Normal",
        "invoiceCode": "200001",
        "invoiceAddress": {
            "provinceNo": 10001,
            "provinceStr": "New York",
        },
        "optionalAddress": [
            {
                "provinceNo": 10002,
                "provinceStr": "Shanghi",
            },
            {
                "provinceNo": 10003,
                "provinceStr": "Beijing",
            }
        ]
    }
}
```
####Sample JSON Object for Response:
``` json
{
    "code": "200",
    "msg": "This is msg",
    "reqNo": "100200012",
    "businessIds": [
        "111asd",
        "2cde2"
    ],
    "invoiceTicket": {
        "invoiceType": "Normal",
        "invoiceCode": "200001",
        "invoiceAddress": {
            "provinceNo": 10001,
            "provinceStr": "Shanghai",
        },
        "optionalAddress": [
            {
                "provinceNo": 10002,
                "provinceStr": "Beijing",
            },
            {
                "provinceNo": 10003,
                "provinceStr": "Hong Kong",
            }
        ]
    }
}
```
####Definitation of Class, Request and Response:
``` cpp
//namespace Definition
namespace jsf;

//Class Definition
@description="Address Structure"  //@descpription is optional
class Address
{
    @jsonname="provinceNo", description="Province ID" //@descpription is optional
    int provinceNo;	
	
    @jsonname="provinceStr", description="Province"
    string province;
};

//@descpription is optional
class InvoiceTicket
{
    @jsonname="invoiceType" //@descpription is optional
    string invoiceType;
	
    @jsonname="invoiceCode", description="Invoice Code"
    string invoiceCode;

    @jsonname="invoiceAddress", description="Inoice Address"
    Address address;

    @jsonname="optionalAddress"
    vector<Address> optionalAddress; //Only use vector for list handling
};

//The Interface which handles the serialization of JSON
@description="Add Invoice Interface"
Interface AddInvoice {
    Request {
        @jsonname="sourceId", description="Source"
        int source;

        @jsonname="orgId", description="Organization"
        int organizationId;

        @jsonname="ivcType",description="Type"
        int invoiceType;

        @jsonname="reqNo", description="Rquest Number"
        string requestNo;

        @jsonname="payerNo", description="Payer No"
        string payNo;

        @jsonname="receiverNo", description="ReceiverNo", optional="true" //Optional member
        string receiverNo ;

        @jsonname="businessIds", description="Business ID List"
        vector<string> bussinessIds;
		
        @jsonname="invoiceTicket", description="Invoice Ticket"
        InvoiceTicket invoiceTicket;
	};

	Response {
        @jsonname="code", description="Return Code"
        string code;

        @jsonname="msg", description="Message"
        string message;

        @jsonname="reqNo", description="Require Number"
        string requestNo;

        @jsonname="businessIds", description="BusinessID", optional="true"
        vector<string> bussinessIds ;
		
        @jsonname="invoiceTicket", description="Invoice Ticket"
        InvoiceTicket invoiceTicket;
	};
};
```
###Generate the C++ Class files
``` shell
./json2cpp.py sample.jsf dir_test
```
Command *json2cpp* takes 2 arguements: *{Class definitation File}* *{Directory}*
Outputs in *dir_test* path is organized by the namespace defined in *sample.jsf*:
``` plain
dir_test
├── jsf
     ├── AddInvoice.h
     ├── AddWare.h
     ├── Address.h
     ├── InvoiceTicket.h
     ├── json2cpp.h
     ├── base.h
     ├── macro.h
     └── rapidjson
                ├──
                 ......
```

###Class Usage
base.h: defines the basic object access:
>* Field<>:     Every json object in interface class are all Field type. It has Get/SetVaule()
>* IRequest:  *ToJson()* serialize C++ Object to JSON string
>* IResponse: *FromJson()* unserialize JSON string to C++ Object
macro.h: defines some marcos for internel use.
json2cpp.h: include all header files, provide for other to use.

json2cpp will generate a hpp file each user defined class and interface.
AddInvoice.h: interface AddInvoice implemention.
AddWare.h: interface AddWare implemention.
Address.h: user define class Address implemention.
InvoiceTicket.h: user define class InvoiceTicket implemetion.

all you have to do is include header file "json2cpp.h", and use the classes generated.

####C++ Sample Code:
``` cpp
#include "json2cpp.h"

/**** Request Sample ****/
AddInvoiceRequest request;
Address address;
Address address1;
InvoiceTicket invoTic;

address.m_provinceNo.SetValue(10001);
... //set address and address1 members
invoTic.m_invoiceType.SetValue("Normal");
... //set invoTic members

vector<Address> v_addr;
v_addr.push_back(address1);
invoTic.m_optionalAddress.SetValue(v_addr);

//Set the Request values:
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

/**** Response Sample ****/
ifstream fin("json.txt");
getline(fin,str);
uint32_t status = 200;
AddInvoiceResponse response;
uint32_t ret = response.FromJson(str, status);
if(ret != json2cpp::ERR_OK)
{
    std::cout<<"error:"<<ret<<", "<<response.m_JSFMessage.GetValue()<<std::endl;
    return;
}
```

###Grammar

``` cpp
//namespace, allow 0 or more
(namespace {name_space};)

//user define class, allow 0 or more
(
(@description="{description_str}")
class {class_name}{
	@jsonname={json_filed_name}(,description="{description_str}", optional=["true","false"], default="{default_value_str}")
	[field_type] {field_name}; 
};
)
 
 //interface, allow 1 or more
(@description="{description_str}")
Interface {interface_name}{
	//request, must have only 1 for every interface
	Request{
		@jsonname={json_filed_name}(,description="{description_str}", optional=["true","false"], default="{default_value_str}")
		[field_type] {field_name} (optional); 
	};
	
	//response, must have only 1 for every interface
	Response{
		@jsonname={json_filed_name}(,description="{description_str}", optional=["true","false"], default="{default_value_str}")
		[field_type] {field_name} (optional); 
	};
};


```
####Conventions：
1. **()** means the grammar token is optional, it can be defined 0 or 1
2. **{}** means variable name
3. **@** means comments
4. **[]** means specified value of the set

####Details：
0. **{name_space}** means C++ style namespace
1. **{class_name}**, **{interface_name}**, **{field_name}**, **{json_filed_name}** means self-defined struct/class, Interface, Field Name, JSON Field name. They can be any valid string
2. User can define 1 or more **class**, the definitation sequence should follow the C++ style
3. User can define 1 or more **Interface**，each Interface MUST have a pair of request/response objects
4. **@** means comments，now it supports **jsonname**, **description**, **optional**, **default** key-words:

	|Key-Word| Description |
	|:------:| :---------------: |
	|jsonname| JSON Field Name [It MUST be specified] |
	|description| It will be generated into C++ code for comments [Optional]|
	|optional|Specifies the JSON field is optional，value should be "true" or "false"，default is"false" [Optional]|
	|default|Specifies the default value of C++ member feild [Optional]|
	
6. **[field_type]** Filed Type. Now supporting *short*, *int*, *bool*, *uint32_t*, *uint64_t*, *int64_t*, *double*, self-define class *T* and *vector<**T**>*.

7. Supports C++ sytle comments like ```//comments``` and ```/*comments*/``` , the commots will be ignored when being parsing.

