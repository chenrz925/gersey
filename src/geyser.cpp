//
// Created by 陈润泽 on 2021/8/25.
//

#include "geyser.h"
#include "fmt/format.h"

void geyser::Geyser::bind(py::class_<Geyser> &&clazz) {
    clazz.def_static("entry", &Geyser::entry);
}

int geyser::Geyser::entry() {
    Logger::get("entry").error(fmt::format("{}", "This is entry"));
    return 1;
}
