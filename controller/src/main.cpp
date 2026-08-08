#include <iostream>

#include "gridflex/controller/controller.hpp"

int main()
{
    std::cout << gridflex::controller::component_name() << '\n';

    return 0;
}