#include <pybind11/pybind11.h>

#include "kernel.h"

namespace py = pybind11;

PYBIND11_MODULE(_geyser, m) {
    py::class_<geyser::Kernel>(m, "Core")
            .def(py::init())
            .def("register_class", &geyser::Kernel::register_class)
            .def("compose", &geyser::Kernel::compose)
            .def_property_readonly("concurrency", &geyser::Kernel::concurrency)
            .def("__getitem__", &geyser::Kernel::access)
            .def("execute", &geyser::Kernel::execute)
            .def_property_readonly("compiler", &geyser::Kernel::compiler)
            .def_property_readonly("class_count", &geyser::Kernel::class_count)
            .def_property_readonly("object_count", &geyser::Kernel::object_count)
            .def_property_readonly("references", &geyser::Kernel::references);
}