//
// Created by 陈润泽 on 2021/8/3.
//

#include "schedule.h"


void geyser::LinearSchedule::operator()(std::map<const std::string, py::object> &context, py::list profile) {
    for (auto execute: profile) {
        auto execute_profile = execute.cast<py::dict>();
        auto name = execute_profile["__name__"].cast<std::string>();
        auto enable = execute_profile["__enable__"].cast<py::bool_>();
        if (enable) {
            if (context.find(name) == context.end()) {
                raise_not_composed(name);
            } else {
                auto executable = context.at(name);
                if (hasattr(executable.get_type().cast<py::type>(), "__call__")) {
                    execute_once(executable);
                } else {
                    raise_not_executable(name, executable);
                }
            }
        }
    }
}

void geyser::LinearSchedule::raise_not_composed(const std::string &name) const {
    std::ostringstream error_info;
    error_info << "Please compose \"" << name << "\" before execute it.";
    throw py::import_error(error_info.str());
}

void geyser::LinearSchedule::execute_once(const pybind11::object &executable) const {
    py::object proxy = executable();
    if (!proxy.is(py::none())) {
        if (py::isinstance<py::dict>(proxy)) {
            auto proxy_dict = proxy.cast<py::dict>();
            for (auto item : proxy_dict) {
                executable.attr("__dict__").cast<py::dict>()[item.first] = item.second;
            }
        } else {
            executable.attr("__dict__").cast<py::dict>()["__return__"] = proxy;
        }
    }
}

void geyser::LinearSchedule::raise_not_executable(const std::string &name, const pybind11::object &executable) const {
    std::ostringstream error_info;
    error_info << "Composed \"" << name << "\" is not a executable, mro: ";
    for (auto &item : executable.get_type().attr("mro")()) {
        error_info << py::str(item).cast<std::string>() << " ";
    }
    throw py::value_error(error_info.str());
}
