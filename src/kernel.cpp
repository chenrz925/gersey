#include "kernel.h"
#include "taskflow/taskflow.hpp"
#include "pybind11/pybind11.h"
#include <thread>


std::map<std::string, py::type> geyser::Kernel::classes;

void geyser::Kernel::register_class(std::string name, py::object clazz) {
    if (py::isinstance<py::type>(clazz)) {
        if (name == "")
            name = clazz.attr("__name__").cast<std::string>();
        auto clazz_t = clazz.cast<py::type>();
        auto reference = fmt::format("{}.{}", py::str(clazz.attr("__module__")).cast<std::string>(), name);
        logger.debug(reference);
        if (classes.find(reference) == classes.end())
            classes.insert({reference, clazz_t});
        else
            logger.warning(fmt::format("Composable {} has been already registered"));
    } else
        logger.error(fmt::format("Object {} is NOT a class", py::repr(clazz).cast<std::string>()));
}

py::type geyser::Kernel::access(const std::string &reference) {
    auto module = extract_module(reference);
    if (classes.find(reference) == classes.end())
        try {
            py::module_::import(module.c_str());
        } catch (py::error_already_set &e) {
            logger.error(e.value().cast<py::str>().cast<std::string>());
        }
    if (classes.find(reference) != classes.end())
        return classes.at(reference);
    else
        throw py::import_error(fmt::format("Class {} is NOT found", reference));
}

py::object geyser::Kernel::compose(const std::string &name, py::dict profile) {
    py::kwargs kwargs;
    auto item_profile = profile[name.c_str()].cast<py::dict>();
    auto reference = item_profile["__reference__"].cast<std::string>();
    if (item_profile.contains("__compose__")) {
        auto composes = item_profile["__compose__"].cast<py::list>();
        for (auto key: composes) {
            item_profile[key] = py::str("__compose__");
        }
    }
    auto type_t = access(reference);
    for (auto it : item_profile) {
        auto key = it.first.cast<std::string>();
        auto value = it.second;
        if (key.size() < 4 || (!(key.substr(0, 2) == "__") && !(key.substr(key.size() - 2, 2) == "__"))) {
            fill_kwargs(item_profile, kwargs, key, value);
        }
    }
    if (context.find(name) != context.end())
        logger.warning(fmt::format("Name \"{}\" is composed twice, old instance will be replaced"));
    auto item_logger = Logger::get(reference);
    kwargs["logger"] = py::cast(&item_logger);
    context.insert({name, type_t(**kwargs)});
    return context.at(name);
}

void
geyser::Kernel::fill_kwargs(py::dict &profile, py::kwargs &kwargs, const std::string &key, pybind11::handle &value) {
    std::string mirrored_key = mirror_key(key, profile);
    if (pybind11::isinstance<py::str>(value) && value.cast<py::str>().cast<std::string>() == "__compose__") {
        if (context.find(key) != context.end()) {
            kwargs[py::str(mirrored_key.c_str())] = context.at(key);
        } else {
            throw py::import_error(fmt::format("Composable attribute \"{}\" is undefined", key));
        }
    } else {
        kwargs[py::str(mirrored_key.c_str())] = value;
    }
}

std::string geyser::Kernel::mirror_key(const std::string &key, py::dict &profile) const {
    py::dict mirrors;
    if (profile.contains("__mirror__"))
        mirrors = profile["__mirror__"].cast<py::dict>();
    if (mirrors.contains(key)) {
        return mirrors[key.c_str()].cast<py::str>().cast<std::string>();
    } else {
        return key;
    }
}

std::string geyser::Kernel::extract_module(const std::string &reference) {
    auto last_point = reference.find_last_of('.');
    if (last_point != std::string::npos)
        return reference.substr(0, last_point);
    else
        throw py::import_error(fmt::format("Wrong reference \"{}\" without a module", reference));

}

int geyser::Kernel::class_count() const {
    return classes.size();
}

int geyser::Kernel::object_count() const {
    return context.size();
}

std::vector<std::string> geyser::Kernel::references() const {
    std::vector<std::string> references;
    for (auto[key, value] : this->classes)
        references.push_back(key);
    std::sort(references.begin(), references.end());
    return references;
}

void geyser::Kernel::compose_all(py::dict profile) {
    tf::Taskflow flow;
    tf::Executor executor(std::thread::hardware_concurrency());
    std::map<std::string, std::shared_ptr<tf::Task>> tasks;
    std::map<std::string, std::vector<std::string>> task_dependencies;
    for (auto[key, value] : profile) {
        auto name = key.cast<py::str>().cast<std::string>();
        task_dependencies.insert({name, this->get_dependencies(value.cast<py::dict>())});
        tasks[name] = std::make_shared<tf::Task>(flow.emplace([&]() {
            this->logger.debug(fmt::format("Compose {}", name));
            this->context[name] = this->compose(name, profile);
        }).name(name));
    }
    for (auto &[name, dependencies] : task_dependencies) {
        for (auto it : dependencies)
            tasks[it]->precede(*tasks[name]);
    }
    logger.debug(fmt::format("Compose in this flow: \n{}", flow.dump()));
    executor.run(flow).wait();
}

std::vector<std::string> geyser::Kernel::get_dependencies(py::dict profile) {
    std::vector<std::string> dependencies;
    if (profile.contains("__compose__")) {
        for (auto it : profile["__compose__"])
            dependencies.push_back(it.cast<py::str>().cast<std::string>());
    }
    for (auto[akey, avalue] : profile.cast<py::dict>()) {
        if (py::isinstance<py::str>(avalue) && avalue.cast<py::str>().cast<std::string>() == "__compose__")
            dependencies.push_back(akey.cast<py::str>().cast<std::string>());
    }
    return dependencies;
}

