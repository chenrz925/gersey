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
    auto platform = py::module_::import("platform");
    logger.info(fmt::format("geyser {}", GEYSER_MACRO_STRINGIFY(GEYSER_VERSION_INFO)));
    logger.info(fmt::format(
            "{} {} {} {} {} {} {}",
            GEYSER_MACRO_STRINGIFY(GEYSER_SYSTEM_NAME),
            GEYSER_MACRO_STRINGIFY(GEYSER_SYSTEM_VERSION),
            GEYSER_MACRO_STRINGIFY(GEYSER_SYSTEM_PROCESSOR),
            GEYSER_MACRO_STRINGIFY(GEYSER_COMPILER_NAME),
            GEYSER_MACRO_STRINGIFY(GEYSER_COMPILER_VERSION),
            __DATE__, __TIME__
    ));
//    auto platform_system = platform.attr("python_version")().cast<py::str>().cast<std::string>();
    logger.info(fmt::format(
            "python {} {} ",
            py::str(platform.attr("python_version")()).cast<std::string>(),
            platform.attr("python_compiler")().cast<py::str>().cast<std::string>()
    ));
    logger.info(platform.attr("version")().cast<py::str>().cast<std::string>());

    return 0;
}
