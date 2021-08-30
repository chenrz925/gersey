//
// Created by 陈润泽 on 2021/8/25.
//

#ifndef CMAKE_EXAMPLE_GEYSER_H
#define CMAKE_EXAMPLE_GEYSER_H

#define GEYSER_STRINGIFY(x) #x
#define GEYSER_MACRO_STRINGIFY(x) GEYSER_STRINGIFY(x)

#include "pybind11/pybind11.h"
#include "pybind11/functional.h"
#include "logger.h"
#include "profile.h"
#include "kernel.h"
#include "argh.h"

namespace py = pybind11;

namespace geyser {
    class Geyser {
    private:
        static void print_runtime_info(Logger &logger);

        static bool python_mode;

        static py::module_ sys;

        static py::type Bucket;

        static argh::parser build_parser(int argc, const char *argv[]);

        static void define_parser(argh::parser &parser);

        static std::vector<std::string> get_profile_paths(argh::parser &parser);

    public:
        static void init();

        static void bind(py::class_<Geyser> &&clazz);

        static int entry();

        static int entry(int argc, const char *argv[], const char *envp[]);

        static std::function<py::object(py::object)> composable(const std::string &name, bool auto_compose);

        static void composable(py::object clazz, const std::string &name);

        static std::function<py::object(py::object)> composable(bool auto_compose);

        static void composable(py::object clazz);

        static std::function<py::object(py::object)> composable();

        static std::function<py::object(py::object)> executable();

        static std::function<py::object(py::object)> executable(const std::string &name);

        static void executable(py::object func, const std::string &name);
    };
}

#endif //CMAKE_EXAMPLE_GEYSER_H
