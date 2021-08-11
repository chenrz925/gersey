//
// Created by waterch on 2021/7/29.
//

#ifndef GEYSER_CORE_H
#define GEYSER_CORE_H

#include <memory>
#include <map>
#include <thread>
#include <sstream>
#include <pybind11/pybind11.h>

#include "schedule.h"

namespace py = pybind11;

namespace geyser {
    class Core {
    private:
        std::unique_ptr<py::object> logger;
        std::map<const std::string, py::type> classes;
        std::map<const std::string, py::object> context;

        void register_class_debug(std::string name, py::object clazz);

        std::string extract_module(const std::string &reference);

        void fill_kwargs(py::dict &profile, py::kwargs &kwargs, const std::string &key, pybind11::handle &value);

    public:
        Core();

        int concurrency();

        void register_class(std::string name, py::object clazz);

        py::type access(const std::string &reference);

        py::object compose(const std::string &name, py::dict profile);

        std::string compiler() const;

        void execute(py::dict profile);

        void mirror_key(const std::string &key, py::dict &profile, std::string &mirrored_key) const;
    };
}

#endif //GEYSER_CORE_H
