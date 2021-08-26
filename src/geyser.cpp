//
// Created by 陈润泽 on 2021/8/25.
//

#include "geyser.h"
#include "fmt/format.h"

void geyser::Geyser::init() {
    Logger::init();
}

void geyser::Geyser::bind(py::class_<Geyser> &&clazz) {
    clazz.def_static("entry", &Geyser::entry);
}

int geyser::Geyser::entry() {
    auto &logger = geyser::Logger::get("geyser.Geyser");
    logger.info(fmt::format("geyser v{}", GEYSER_MACRO_STRINGIFY(GEYSER_VERSION_INFO)));
    logger.info(fmt::format(
            "build {} {} {} {} {} {}",
            GEYSER_MACRO_STRINGIFY(GEYSER_SYSTEM_NAME),
            GEYSER_MACRO_STRINGIFY(GEYSER_SYSTEM_VERSION),
            GEYSER_MACRO_STRINGIFY(GEYSER_COMPILER_NAME),
            GEYSER_MACRO_STRINGIFY(GEYSER_COMPILER_VERSION),
            __DATE__, __TIME__
    ));
    return 0;
}
