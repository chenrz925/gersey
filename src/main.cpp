//
// Created by 陈润泽 on 2021/8/26.
//
#include "pybind11/embed.h"
#include "geyser.h"

namespace py = pybind11;

PYBIND11_EMBEDDED_MODULE(geyser, m) {
    geyser::Geyser::bind(py::class_<geyser::Geyser>(m, "Geyser"));
    geyser::Logger::bind(py::class_<geyser::Logger>(m, "Logger"));
    geyser::Profile::bind(py::class_<geyser::Profile>(m, "Profile"));
    geyser::Geyser::init();
}

int main(int argc, const char *argv[], const char *envp[]) {
    py::scoped_interpreter guard{};
    py::module_::import("geyser");

    return geyser::Geyser::entry(argc, argv, envp);
}