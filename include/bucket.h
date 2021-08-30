//
// Created by 陈润泽 on 2021/8/30.
//

#ifndef GEYSER_BUCKET_H
#define GEYSER_BUCKET_H

#include "pybind11/pybind11.h"

namespace py = pybind11;

namespace geyser {
    class ComposeWrapper {
    public:
        static void bind(py::class_<ComposeWrapper> &&clazz);

        ComposeWrapper(const std::string &name, bool auto_compose);

        py::type operator()(py::type clazz);
    };
}

#endif //GEYSER_BUCKET_H
