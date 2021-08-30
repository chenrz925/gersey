//
// Created by 陈润泽 on 2021/8/30.
//

#include "bucket.h"
#include "pybind11/operators.h"

void geyser::ComposeWrapper::bind(py::class_ <geyser::ComposeWrapper> &&clazz) {
}

py::type geyser::ComposeWrapper::operator()(py::type clazz) {
    return py::type(pybind11::handle(), false);
}

