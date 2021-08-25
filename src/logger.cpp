//
// Created by 陈润泽 on 2021/8/25.
//

#include "logger.h"

std::map<std::string, std::shared_ptr<geyser::Logger>> geyser::Logger::logger_cache;
py::module_ geyser::Logger::logging_module = py::module_::import("logging");

void geyser::Logger::bind(py::class_<Logger> &&clazz) {
    clazz.def_static("get", &Logger::get);
    clazz.def("debug", py::overload_cast<const py::args &, const py::kwargs &>(&Logger::debug));
    clazz.def("debug", py::overload_cast<const std::string &>(&Logger::debug));
    clazz.def("info", py::overload_cast<const py::args &, const py::kwargs &>(&Logger::info));
    clazz.def("info", py::overload_cast<const std::string &>(&Logger::info));
    clazz.def("warning", py::overload_cast<const py::args &, const py::kwargs &>(&Logger::warning));
    clazz.def("warning", py::overload_cast<const std::string &>(&Logger::warning));
    clazz.def("error", py::overload_cast<const py::args &, const py::kwargs &>(&Logger::error));
    clazz.def("error", py::overload_cast<const std::string &>(&Logger::error));
    clazz.def("critical", py::overload_cast<const py::args &, const py::kwargs &>(&Logger::critical));
    clazz.def("critical", py::overload_cast<const std::string &>(&Logger::critical));
}

geyser::Logger::Logger(py::object logger_) {
    this->logger = std::move(logger_);
}

geyser::Logger &geyser::Logger::get(const std::string& name) {
    if (Logger::logger_cache.find(name) == Logger::logger_cache.end()) {
        auto logger = logging_module.attr("getLogger")(name).cast<py::object>();
        Logger::logger_cache.insert({name, std::make_shared<Logger>(Logger(logger))});
    }
    return *Logger::logger_cache.at(name);
}

void geyser::Logger::debug(const py::args &args, const py::kwargs &kwargs) {
    this->logger.attr("debug")(*args, **kwargs);
}

void geyser::Logger::debug(const std::string& message) {
    this->logger.attr("debug")(message);
}

void geyser::Logger::info(const py::args &args, const py::kwargs &kwargs) {
    this->logger.attr("info")(*args, **kwargs);
}

void geyser::Logger::info(const std::string& message) {
    this->logger.attr("info")(message);
}

void geyser::Logger::warning(const py::args &args, const py::kwargs &kwargs) {
    this->logger.attr("warning")(*args, **kwargs);
}

void geyser::Logger::warning(const std::string& message) {
    this->logger.attr("warning")(message);
}

void geyser::Logger::error(const py::args &args, const py::kwargs &kwargs) {
    this->logger.attr("error")(*args, **kwargs);
}

void geyser::Logger::error(const std::string& message) {
    this->logger.attr("error")(message);
}

void geyser::Logger::critical(const py::args &args, const py::kwargs &kwargs) {
    this->logger.attr("error")(*args, **kwargs);
}

void geyser::Logger::critical(const std::string& message) {
    this->logger.attr("error")(message);
}


