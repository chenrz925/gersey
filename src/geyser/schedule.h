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
    };
}

#endif //GEYSER_SCHEDULE_H
