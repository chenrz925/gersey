#include "core.h"
#include <pybind11/pybind11.h>

geyser::Core::Core() {
    auto logging = py::module_::import("logging");
    py::kwargs basic_config;
    basic_config["level"] = "INFO";
    basic_config["format"] = "(%(asctime)s)[%(levelname)s][%(process)d][%(thread)d][%(name)s]: %(message)s";
    logging.attr("basicConfig")(**basic_config);
    auto get_logger = logging.attr("getLogger");
    logger = std::make_unique<py::object>(get_logger(__FUNCTION__));
}

void geyser::Core::register_class(std::string name, py::object clazz) {
    if (py::isinstance<py::type>(clazz)) {
        if (name == "") {
            name = clazz.attr("__name__").cast<std::string>();
        }
        register_class_debug(name, clazz);
        auto clazz_t = clazz.cast<py::type>();
        std::ostringstream reference_s;
        reference_s << clazz.attr("__module__").cast<std::string>() << "." << name;
        std::ostringstream log_content;
        log_content << "Cast " << reference_s.str() << "to type.";
        logger->attr("debug")(log_content.str());
        if (classes.find(reference_s.str()) == classes.end())
            classes.insert({reference_s.str(), clazz_t});
        else {
            std::stringstream error_info;
            error_info << "Composable \"" << reference_s.str() << "\" has been already registered.";
            logger->attr("debug")(error_info.str());
        }
    } else {
        std::ostringstream log_content;
        log_content << "Object " << py::repr(clazz).cast<std::string>() << " is NOT a class";
        logger->attr("warning")(log_content.str());
    }
}

void geyser::Core::register_class_debug(std::string name, py::object clazz) {
    std::ostringstream log_stream;
    log_stream << "Register " << __FILE__ << ": "
               << clazz.attr("__module__").cast<std::string>() << "."
               << name << ".";
    logger->attr("debug")(log_stream.str());
}

int geyser::Core::concurrency() {
    return static_cast<int>(std::thread::hardware_concurrency());
}

py::type geyser::Core::access(const std::string &reference) {
    auto module = extract_module(reference);
    if (classes.find(reference) == classes.end())
        py::module_::import(module.c_str());
    return classes.at(reference);
}

py::object geyser::Core::compose(const std::string &name, py::dict profile) {
    py::kwargs kwargs;
    auto item_profile = profile[name.c_str()].cast<py::dict>();
    auto reference = item_profile["__reference__"].cast<std::string>();
    auto type_t = access(reference);
    for (auto &it : item_profile) {
        auto key = it.first.cast<std::string>();
        auto value = it.second;
        if (key.size() < 4 || (!(key.substr(0, 2) == "__") && !(key.substr(key.size() - 2, 2) == "__"))) {
            if (py::isinstance<py::str>(value) && value.cast<py::str>().cast<std::string>() == "__compose__") {
                if (context.find(key) != context.end()) {
                    kwargs[py::str(key.c_str())] = context.at(key);
                } else {
                    kwargs[py::str(key.c_str())] = compose(key, profile);
                }
            } else {
                kwargs[py::str(key.c_str())] = value;
            }
        }
    }
    if (context.find(name) != context.end()) {
        std::ostringstream error_info;
        error_info << "Name \"" << name << "\" is composed twice, old instance will be replaced.";
        logger->attr("warning")(error_info.str());
    }
    auto item_logger = py::module_::import("logging").attr("getLogger")(reference);
    kwargs["logger"] = item_logger;
    context.insert({name, type_t(**kwargs)});
    return context.at(name);
}

std::string geyser::Core::extract_module(const std::string &reference) {
    auto last_point = reference.find_last_of('.');
    if (last_point != std::string::npos) {
        return reference.substr(0, last_point);
    } else {
        std::ostringstream error_info;
        error_info << "Wrong reference \"" << reference << "\" without a module.";
        throw py::import_error(error_info.str());
    }
}

void geyser::Core::execute(py::dict profile) {
    auto schedule_rule = profile["__rule__"].cast<py::str>().cast<std::string>();
    auto schedule_action = profile["__action__"].cast<py::list>();
    if (schedule_rule == "linear" or schedule_rule == "default") {
        auto scheduler = geyser::LinearSchedule();
        scheduler(context, schedule_action);
    } else {
        std::ostringstream error_info;
        error_info << "Please select a schedule rule in linear (or default).";
        throw py::import_error(error_info.str());
    }
}

std::string geyser::Core::compiler() const {
    std::ostringstream info;
    info << __VERSION__ << " " << __DATE__ << " " << __TIME__;
    return info.str();
}


