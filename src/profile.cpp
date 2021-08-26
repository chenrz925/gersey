//
// Created by 陈润泽 on 2021/8/26.
//

#include "profile.h"

geyser::Profile geyser::Profile::get(const std::string &filename) {
    auto last_dot = filename.find_last_of('.');
    if (last_dot != std::string::npos) {
        auto suffix = filename.substr(last_dot);
        if (suffix == ".json") {}
        else if (suffix == ".yaml" || suffix == ".yml") {}
        else if (suffix == ".toml" || suffix == ".tml") {}
        else {
            throw py::value_error(fmt::format("Unsupported suffix {}", suffix));
        }
    } else
        throw py::value_error(fmt::format("File name without suffix is NOT supported."));
}
