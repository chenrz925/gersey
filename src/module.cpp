#include <pybind11/pybind11.h>
#include "geyser.h"

namespace py = pybind11;

PYBIND11_MODULE(geyser, m) {
    py::setattr(m, "__version__", py::str(GEYSER_MACRO_STRINGIFY(GEYSER_VERSION_INFO)));

    geyser::Geyser::bind(py::class_<geyser::Geyser>(m, "Geyser"));
    geyser::Logger::bind(py::class_<geyser::Logger>(m, "Logger"));
    geyser::Profile::bind(py::class_<geyser::Profile>(m, "Profile"));
    geyser::Geyser::init();
}