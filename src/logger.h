//
// Created by 陈润泽 on 2021/8/25.
//

#ifndef GEYSER_LOGGER_H
#define GEYSER_LOGGER_H

#include <map>
#include <memory>
#include "pybind11/pybind11.h"

namespace py = pybind11;

namespace geyser {
    class Logger {
    private:
        static std::map<std::string, std::shared_ptr<Logger>> logger_cache;
        static py::module_ logging_module;

        explicit Logger(py::object logger_);

        Logger() = default;

        py::object logger;
    public:
        static void bind(py::class_<Logger> &&clazz);

        static Logger &get(const std::string &name);

        void debug(const py::args &args, const py::kwargs &kwargs);

        void debug(const std::string &message);

        void info(const py::args &args, const py::kwargs &kwargs);

        void info(const std::string &message);

        void warning(const py::args &args, const py::kwargs &kwargs);

        void warning(const std::string &message);

        void error(const py::args &args, const py::kwargs &kwargs);

        void error(const std::string &message);

        void critical(const py::args &args, const py::kwargs &kwargs);

        void critical(const std::string &message);
    };
}

#endif //GEYSER_LOGGER_H
