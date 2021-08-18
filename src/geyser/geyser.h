//
// Created by 陈润泽 on 2021/8/17.
//

#ifndef GEYSER_GEYSER_H
#define GEYSER_GEYSER_H

#include <memory>
#include <map>
#include "core.h"

#define GEYSER_VERSION "0.1.2"

namespace geyser {
    class Geyser {
    private:
        static std::unique_ptr<Core> core;

        static void register_class(std::string name, py::type clazz, bool auto_compose);

        static void register_class(std::string name, py::type clazz);

        static void register_class(py::type clazz, bool auto_compose);

        static void register_class(py::type clazz);

    public:
        static std::string version() {
            return {GEYSER_VERSION};
        }

        static std::string build() {
            return core->compiler();
        }
    };


    class Bucket {
    private:
        std::map<const std::string, py::object> objects;
    public:
        static void define(py::class_<Bucket> &&clazz);

        Bucket() = default;

        explicit Bucket(const py::kwargs &kwargs);

        py::object dot_get(std::string name);

        py::list dir();
    };
}

#endif //GEYSER_GEYSER_H
