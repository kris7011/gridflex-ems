#pragma once

#include <string_view>

namespace gridflex::controller
{

    [[nodiscard]] std::string_view component_name() noexcept;

}