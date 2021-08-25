//
// Created by 陈润泽 on 2021/8/25.
//

#ifndef CMAKE_EXAMPLE_GEYSER_H
#define CMAKE_EXAMPLE_GEYSER_H

#include "pybind11/pybind11.h"
#include "logger.h"

namespace py = pybind11;

namespace geyser {
    class Geyser {
    public:
        static void bind(py::class_<Geyser> &&clazz);

        static int entry();
    };
}

#endif //CMAKE_EXAMPLE_GEYSER_H
