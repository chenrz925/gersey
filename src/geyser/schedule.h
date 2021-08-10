//
// Created by 陈润泽 on 2021/8/3.
//

#ifndef GEYSER_SCHEDULE_H
#define GEYSER_SCHEDULE_H

#include <map>
#include <sstream>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace geyser {
    class Schedule {
    public:
        virtual void operator()(std::map<const std::string, py::object> &context, py::list profile) = 0;
    };

    class LinearSchedule : Schedule {
    public:
        virtual void operator()(std::map<const std::string, py::object> &context, py::list profile);

        void raise_not_executable(const std::string &name, const pybind11::object &executable) const;

        void execute_once(const pybind11::object &executable) const;

        void raise_not_composed(const std::string &name) const;
    };
}

#endif //GEYSER_SCHEDULE_H
