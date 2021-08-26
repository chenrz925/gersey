//
// Created by 陈润泽 on 2021/8/26.
//

#include "profile.h"
#include "rapidjson/filereadstream.h"
#include <cstdio>
#include <fstream>

void geyser::Profile::bind(py::class_<Profile> &&clazz) {
    clazz.def_static("parse", &Profile::parse);
}

std::shared_ptr<geyser::Profile> geyser::Profile::get(const std::string &filename) {
    auto last_dot = filename.find_last_of('.');
    if (last_dot != std::string::npos) {
        auto suffix = filename.substr(last_dot);
        if (suffix == ".json") {
            return std::shared_ptr<Profile>(dynamic_cast<Profile *>(new JSONProfile(filename)));
        } else if (suffix == ".yaml" || suffix == ".yml") {
            return std::shared_ptr<Profile>(dynamic_cast<Profile *>(new YAMLProfile(filename)));
        } else if (suffix == ".toml" || suffix == ".tml") {}
        else {
            throw py::value_error(fmt::format("Unsupported suffix {}", suffix));
        }
    } else
        throw py::value_error(fmt::format("File name without suffix is NOT supported"));
}

py::dict geyser::Profile::parse(const std::string &filename) {
    return Profile::get(filename)->dict();
}

geyser::JSONProfile::JSONProfile(const std::string &filename) : dom(new json::Document) {
#ifdef _WIN32
    FILE *fp = fopen(filename.c_str(), "rb");
#else
    FILE *fp = fopen(filename.c_str(), "r");
#endif
    char read_buffer[0x10000];
    auto stream = json::FileReadStream(fp, read_buffer, 0x10000);
    this->dom->ParseStream(stream);
    fclose(fp);
}

py::dict geyser::JSONProfile::dict() {
    py::dict root;
    for (auto it = this->dom->MemberBegin(); it != this->dom->MemberEnd(); ++it)
        root[it->name.GetString()] = this->map_value(it->value);
    return root;
}

py::object geyser::JSONProfile::map_value(const json::Value &value) {
    if (value.IsArray()) {
        py::list pyvalue;
        for (const auto &it: value.GetArray())
            pyvalue.append(map_value(it));
        return pyvalue;
    } else if (value.IsBool()) return py::bool_(value.GetBool());
    else if (value.IsDouble() || value.IsLosslessDouble()) return py::float_(value.GetDouble());
    else if (value.IsFloat() || value.IsLosslessFloat()) return py::float_(value.GetFloat());
    else if (value.IsFloat()) return py::float_(value.GetFloat());
    else if (value.IsUint64()) return py::int_(value.GetUint64());
    else if (value.IsInt64()) return py::int_(value.GetInt64());
    else if (value.IsUint()) return py::int_(value.GetUint());
    else if (value.IsNull()) return py::none();
    else if (value.IsString()) return py::str(value.GetString());
    else {
        py::dict pyvalue;
        for (auto it = value.MemberBegin(); it != value.MemberEnd(); ++it)
            pyvalue[it->name.GetString()] = map_value(it->value);
        return pyvalue;
    }
}

geyser::YAMLProfile::YAMLProfile(const std::string &filename) {
    std::ifstream ifs(filename);
    auto parser = yaml::Parser(ifs);
    this->dom = std::make_shared<yaml::Node>(yaml::LoadFile(filename));
}

py::dict geyser::YAMLProfile::dict() {
    py::dict root;
    auto eval = py::module_::import("builtins").attr("eval").cast<py::function>();
    for (auto it : *this->dom)
        root[it.first.as<std::string>().c_str()] = this->map_value(it.second, eval);
    return root;
}

py::object geyser::YAMLProfile::map_value(const yaml::Node &node, py::function &eval) {
    switch (node.Type()) {
        case yaml::NodeType::Null:
            return py::none();
        case yaml::NodeType::Scalar: {
            try {
                return eval(node.Scalar().c_str());
            } catch (const py::error_already_set &e) {
                return py::str(node.Scalar());
            }
        }
        case yaml::NodeType::Map: {
            py::dict pyvalue;
            for (auto it : node)
                pyvalue[it.first.as<std::string>().c_str()] = this->map_value(it.second, eval);
            return pyvalue;
        }
        case yaml::NodeType::Sequence: {
            py::list pyvalue;
            for (auto it : node)
                pyvalue.append(this->map_value(it, eval));
            return pyvalue;
        }
        case yaml::NodeType::Undefined:
        default: {
            throw py::value_error(fmt::format("Undefined value in YAML profile"));
        }
    }
}