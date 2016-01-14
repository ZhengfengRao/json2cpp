/*
 * File:   macro.h
 * Author: raozf
 *
 * Created on 2015年5月20日, 下午4:26
 */

#ifndef JSON2CPP_MACRO_H
#define	JSON2CPP_MACRO_H

namespace json2cpp{

#define CHECK_REQUEST_FIELD(field, strErrMsg)     \
    if(!field.IsValid()) \
    {   \
        strErrMsg.clear(); \
        strErrMsg.append("field["); \
        strErrMsg.append(field.GetName()); \
        strErrMsg.append("] not set."); \
        return false;   \
    }

#define TOJSON_REQUEST_FIELD_INT(field, jsonObject, allocator) \
    if(field.IsValueSet()) \
    { \
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), field.GetValue(), allocator);\
    }

//使用const-string，不复制字符串
//http://miloyip.github.io/rapidjson/zh-cn/md_doc_tutorial_8zh-cn.html#CreateModifyValues
#define TOJSON_REQUEST_FIELD_STRING(field, jsonObject, allocator) \
    if(field.IsValueSet()) \
    { \
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), rapidjson::StringRef(field.GetValue().c_str()), allocator);\
    }

#define TOJSON_REQUEST_FIELD_STRING_SETVALUE(field, jsonObject) \
    if(field.IsValueSet()) \
    { \
        jsonObject.SetString(rapidjson::StringRef(field.GetValue().c_str())); \
    }

#define TOJSON_REQUEST_FIELD_OBJECT(field, jsonObject, allocator) \
    if(field.IsValueSet()) \
    { \
        rapidjson::Value objectValue(rapidjson::kObjectType); \
        field.GetValue().ToJson(objectValue, allocator); \
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), objectValue, allocator); \
    }

#define TOJSON_REQUEST_FIELD_STR_ARRAY(field, jsonObject, allocator) \
    if(field.IsValueSet()) \
    { \
        rapidjson::Value value(rapidjson::kArrayType); \
        for(std::vector<std::string>::const_iterator it = field.GetValue().begin(); \
            it != field.GetValue().end(); \
            it++) \
        { \
            value.PushBack(rapidjson::StringRef(it->c_str()), allocator); \
        } \
        jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), value, allocator); \
    }

#define FROMJSON_RESPONSE_FIELD_NUMBER(values, field) \
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsNumber()) \
    { \
        field.SetValue(values[field.GetName().c_str()].GetInt()); \
    }

#define FROMJSON_RESPONSE_FIELD_STRING(values, field) \
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsString()) \
    { \
        field.SetValue(values[field.GetName().c_str()].GetString()); \
    }

#define FROMJSON_RESPONSE_FIELD_OBJECT(values, field) \
    if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsObject()) \
    { \
        const rapidjson::Value& val = values[field.GetName().c_str()]; \
        field.GetValue().FromJson(val); \
        field.SetValue(field.GetValue()); \
    }

#define JSONVALUE_TOSTRING(json, str) \
    rapidjson::StringBuffer buffer; \
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer); \
    json.Accept(writer); \
    str= buffer.GetString();

}

#define TOJSON_REQUEST_FIELD_STRING_ARRAY(field, jsonObject, allocator) \
	if(field.IsValueSet()) \
	{ \
		rapidjson::Value value(rapidjson::kArrayType); \
		for(std::vector<string>::const_iterator it = field.GetValue().begin(); \
			it != field.GetValue().end(); \
			it++) \
		{ \
			value.PushBack(rapidjson::StringRef(it->c_str()), allocator); \
		} \
		jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), value, allocator); \
	}

#define TOJSON_REQUEST_FIELD_ADDRESS_ARRAY(field, jsonObject, allocator) \
	if(field.IsValueSet()) \
	{ \
		rapidjson::Value value(rapidjson::kArrayType); \
		for(std::vector<Address>::const_iterator it = field.GetValue().begin(); \
			it != field.GetValue().end(); \
			it++) \
		{ \
			rapidjson::Value objectValue(rapidjson::kObjectType); \
			it->ToJson(objectValue, allocator); \
			value.PushBack(objectValue, allocator); \
		} \
		jsonObject.AddMember(rapidjson::StringRef(field.GetName().c_str()), value, allocator); \
	}

#define FROMJSON_RESPONSE_FIELD_STRING_ARRAY(values, field) \
	if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsArray()) \
	{ \
		vector<string> vec; \
		const rapidjson::Value& val = values[field.GetName().c_str()]; \
		for (rapidjson::Value::ConstValueIterator itr = val.Begin(); itr != val.End(); ++itr) \
		{ \
			vec.push_back(itr->GetString()); \
		} \
		field.SetValue(vec); \
	}

#define FROMJSON_RESPONSE_FIELD_ADDRESS_ARRAY(values, field) \
	if(values.HasMember(field.GetName().c_str()) && values[field.GetName().c_str()].IsArray()) \
	{ \
		vector<Address> vec; \
		const rapidjson::Value& val = values[field.GetName().c_str()]; \
		for (rapidjson::Value::ConstValueIterator itr = val.Begin(); itr != val.End(); ++itr) \
		{ \
			Address typeVar; \
			typeVar.FromJson(*itr); \
			vec.push_back(typeVar); \
		} \
		field.SetValue(vec); \
	}


#endif	/* JSON2CPP_MACRO_H */
