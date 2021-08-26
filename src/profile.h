//
// Created by 陈润泽 on 2021/8/26.
//

#ifndef GEYSER_PROFILE_H
#define GEYSER_PROFILE_H

#include <string>
#include "pybind11/pybind11.h"
#include "fmt/format.h"

namespace py = pybind11;

namespace geyser {
    class Profile {
        static Profile get(const std::string &filename);
    };
}

#endif //GEYSER_PROFILE_H
