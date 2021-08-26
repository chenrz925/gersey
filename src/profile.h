//
// Created by 陈润泽 on 2021/8/26.
//

#ifndef GEYSER_PROFILE_H
#define GEYSER_PROFILE_H

#include <string>
#include <memory>
#include "pybind11/pybind11.h"
#include "fmt/format.h"
#include "rapidjson/document.h"
#include "yaml-cpp/yaml.h"

namespace py = pybind11;
namespace json = rapidjson;
namespace yaml = YAML;


namespace geyser {
    class Profile {
    public:
        static void bind(py::class_<Profile> &&clazz);

        static std::shared_ptr<Profile> get(const std::string &filename);

        static py::dict parse(const std::string &filename);

        virtual py::dict dict() = 0;
    };

    class JSONProfile : protected Profile {
    private:
        friend class Profile;

        std::shared_ptr<json::Document> dom;

        explicit JSONProfile(const std::string &filename);

        py::object map_value(const json::Value &value);

    public:
        py::dict dict() override;
    };

    class YAMLProfile : protected Profile {
    private:
        friend class Profile;

        explicit YAMLProfile(const std::string &filename);

        std::shared_ptr<yaml::Node> dom;

        py::object map_value(const yaml::Node &node, py::function &eval);
    public:
        ~YAMLProfile() = default;

        py::dict dict() override;
    };
}

#endif //GEYSER_PROFILE_H
