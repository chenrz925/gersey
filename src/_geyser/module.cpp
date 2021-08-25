#include <pybind11/pybind11.h>

#include "core.h"

namespace py = pybind11;

PYBIND11_MODULE(_geyser, m) {
    py::class_<geyser::Core>(m, "Core")
            .def(py::init())
            .def("register_class", &geyser::Core::register_class)
            .def("compose", &geyser::Core::compose)
            .def_property_readonly("concurrency", &geyser::Core::concurrency)
            .def("__getitem__", &geyser::Core::access)
            .def("execute", &geyser::Core::execute)
            .def_property_readonly("compiler", &geyser::Core::compiler)
            .def_property_readonly("class_count", &geyser::Core::class_count)
            .def_property_readonly("object_count", &geyser::Core::object_count)
            .def_property_readonly("references", &geyser::Core::references);
}