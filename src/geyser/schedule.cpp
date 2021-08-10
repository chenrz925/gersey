//
// Created by 陈润泽 on 2021/8/3.
//

#include "schedule.h"


void geyser::LinearSchedule::operator()(std::map<const std::string, py::object> &context, py::list profile) {
    for (auto &execute: profile) {
        auto execute_profile = execute.cast<py::dict>();
        auto name = execute_profile["__name__"].cast<std::string>();
        auto enable = execute_profile["__enable__"].cast<py::bool_>();
        if (enable) {
            if (context.find(name) == context.end()) {
                std::ostringstream error_info;
                error_info << "Please compose \"" << name << "\" before execute it.";
                throw py::import_error(error_info.str());
            } else {
                auto executable = context.at(name);
                if (hasattr(executable.get_type().cast<py::type>(), "__call__")) {
                    executable();
                } else {
                    std::ostringstream error_info;
                    error_info << "Composed \"" << name << "\" is not a executable, mro: ";
                    for (auto &item : executable.get_type().attr("mro")()) {
                        error_info << py::str(item).cast<std::string>() << " ";
                    }
                    throw py::value_error(error_info.str());
                }
            }
        }
    }
}
