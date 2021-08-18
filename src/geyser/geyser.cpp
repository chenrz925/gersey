//
// Created by 陈润泽 on 2021/8/17.
//

#include "geyser.h"
#include <sstream>

std::unique_ptr<geyser::Core> geyser::Geyser::core;

void geyser::Geyser::register_class(std::string name, py::type clazz, bool auto_compose) {
    if (auto_compose) {

    }
}

void geyser::Geyser::register_class(std::string name, py::type clazz) {

}

void geyser::Geyser::register_class(py::type clazz, bool auto_compose) {

}

void geyser::Geyser::register_class(py::type clazz) {

}

void geyser::Bucket::define(py::class_<Bucket> &&clazz) {
    clazz.def(py::init([](const py::kwargs &kwargs) {
                return geyser::Bucket(kwargs);
            }))
            .def("__getattr__", &Bucket::dot_get)
            .def("__dir__", &Bucket::dir);
}

geyser::Bucket::Bucket(const py::kwargs &kwargs) {
    for (auto it : kwargs) {
        this->objects.insert({it.first.cast<py::str>().cast<std::string>(), it.second.cast<py::object>()});
    }
}

py::object geyser::Bucket::dot_get(std::string name) {
    return this->objects[name];
}

py::list geyser::Bucket::dir() {
//    auto dir = py::module_::import("builtins").attr("object").attr("__dir__");
    py::list attrs;
//    attrs += dir();
    for (const auto &it: this->objects) {
        attrs.append(py::str(py::str(it.first)));
    }
    return attrs;
}
