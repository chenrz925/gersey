//
// Created by 陈润泽 on 2021/8/25.
//

#ifndef GEYSER_LOGGER_H
#define GEYSER_LOGGER_H

#include <map>
#include <vector>
#include <memory>
#include "pybind11/pybind11.h"
#include "spdlog/spdlog.h"
#include "fmt/format.h"

namespace py = pybind11;
namespace logging = spdlog;

namespace geyser {
    class Logger {
    private:
        static std::map<std::string, std::shared_ptr<Logger>> cache;

        static std::vector<logging::sink_ptr> sinks;

        static std::string pattern;

        explicit Logger(const std::string &name);

        std::shared_ptr<logging::logger> logger = nullptr;

        std::string make_message(const py::args &args, const py::kwargs &kwargs);

    public:
        static void init();

        static void bind(py::class_<Logger> &&clazz);

        static void configure();

        static void configure(const py::dict &profile);

        static void configure_sink(const py::dict &profile);

        static Logger &get(const std::string &name);

        const std::string &name();

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
