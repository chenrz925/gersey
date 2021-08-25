#include <pybind11/pybind11.h>
#include "geyser.h"

namespace py = pybind11;

PYBIND11_MODULE(geyser, m) {
    geyser::Geyser::bind(py::class_<geyser::Geyser>(m, "Geyser"));
    geyser::Logger::bind(py::class_<geyser::Logger>(m, "Logger"));
}