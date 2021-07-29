#include <pybind11/pybind11.h>

#include "core.h"

namespace py = pybind11;

PYBIND11_MODULE(_geysercpp, m) {
    py::class_<geyser::Core>(m, "Core")
            .def(py::init())
            .def("__call__", &geyser::Core::invoke);
}