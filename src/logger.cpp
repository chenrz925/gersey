//
// Created by 陈润泽 on 2021/8/25.
//

#include "logger.h"
#include "spdlog/sinks/stdout_color_sinks.h"

std::map<std::string, std::shared_ptr<geyser::Logger>> geyser::Logger::cache;

void geyser::Logger::bind(py::class_<Logger> &&clazz) {
    clazz.def_static("configure", &Logger::configure);
    clazz.def_static("get", py::overload_cast<const std::string &>(&Logger::get));
    clazz.def_static("get", py::overload_cast<const std::string &, bool>(&Logger::get));
    clazz.def_property_readonly("name", &Logger::name);
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

void geyser::Logger::configure(const py::dict& profile) {
    if (profile.contains("__format__"))
        logging::set_pattern(py::str(profile["__format__"]).cast<std::string>());
    else
        logging::set_pattern("%^(%Y-%m-%d %H:%M%S,%e)[%L][%P][%t][%n]%$: %v");
    if (profile.contains("__stream__")) {
        auto stream_profiles = profile["__stream__"].cast<py::list>();
        for (auto stream_profile : stream_profiles) {

        }
    }
}

geyser::Logger &geyser::Logger::get(const std::string &name, bool multi_thread) {
    if (Logger::cache.find(name) == Logger::cache.end())
        Logger::cache.insert({name, std::make_shared<Logger>(Logger(name))});
    return *Logger::cache.at(name);
}

geyser::Logger &geyser::Logger::get(const std::string &name) {
    return geyser::Logger::get(name, false);
}

geyser::Logger::Logger(const std::string &name, bool multi_thread) {
    if (multi_thread)
        this->logger = logging::stdout_color_mt(name);
    else
        this->logger = logging::stdout_color_st(name);
}

const std::string &geyser::Logger::name() {
    return this->logger->name();
}

std::string geyser::Logger::make_message(const py::args &args, const py::kwargs &kwargs) {
    std::vector<std::string> texts;
    for (auto &it : args) {
        texts.push_back(std::move(py::str(it).cast<std::string>()));
    }
    for (auto &it : kwargs) {
        texts.push_back(
                std::move(fmt::format(
                        "{}={}",
                        std::move(py::str(it.first).cast<std::string>()),
                        std::move(py::str(it.second).cast<std::string>())
                ))
        );
    }
    return fmt::format("{}", fmt::join(texts.begin(), texts.end(), " "));
}


void geyser::Logger::debug(const std::string &message) {
    this->logger->debug(message);
}

void geyser::Logger::debug(const py::args &args, const py::kwargs &kwargs) {
    this->logger->debug(this->make_message(args, kwargs));
}

void geyser::Logger::info(const std::string &message) {
    this->logger->info(message);
}

void geyser::Logger::info(const py::args &args, const py::kwargs &kwargs) {
    this->logger->info(this->make_message(args, kwargs));
}

void geyser::Logger::warning(const std::string &message) {
    this->logger->warn(message);
}

void geyser::Logger::warning(const py::args &args, const py::kwargs &kwargs) {
    this->logger->warn(this->make_message(args, kwargs));
}

void geyser::Logger::error(const std::string &message) {
    this->logger->error(message);
}

void geyser::Logger::error(const py::args &args, const py::kwargs &kwargs) {
    this->logger->error(this->make_message(args, kwargs));
}

void geyser::Logger::critical(const std::string &message) {
    this->logger->critical(message);
}

void geyser::Logger::critical(const py::args &args, const py::kwargs &kwargs) {
    this->logger->critical(this->make_message(args, kwargs));
}
