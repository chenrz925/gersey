//
// Created by waterch on 2021/7/29.
//

#ifndef GEYSER_KERNEL_H
#define GEYSER_KERNEL_H

#include <memory>
#include <map>
#include <thread>
#include <sstream>
#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

#include "logger.h"

namespace py = pybind11;

namespace geyser {
    class Kernel {
    private:
        static std::map<std::string, py::type> classes;
        std::map<std::string, py::object> context;
        static Logger &logger;

        std::string extract_module(const std::string &reference);

        void fill_kwargs(py::dict &profile, py::kwargs &kwargs, const std::string &key, pybind11::handle &value);

        std::string mirror_key(const std::string &key, py::dict &profile) const;

    public:
        static void register_class(std::string name, py::object clazz);

        py::type access(const std::string &reference);

        py::object compose(const std::string &name, py::dict profile);

        void compose_all(py::dict profile);

        std::vector<std::string> get_dependencies(py::dict profile);

        int class_count() const;

        int object_count() const;

        std::vector<std::string> references() const;
    };
}

#endif //GEYSER_KERNEL_H
