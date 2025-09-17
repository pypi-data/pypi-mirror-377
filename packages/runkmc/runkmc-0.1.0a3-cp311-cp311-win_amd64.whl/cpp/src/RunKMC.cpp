#include "config/config.h"
#include "kmc/kmc_builder.h"
#include "kmc/kmc.h"

int main(int argc, char **argv)
{
    auto config = config::parseArguments(argc, argv);

    KMC model = KMCBuilder().fromFile(config);

    model.run();

    return EXIT_SUCCESS;
}