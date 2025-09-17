#include "common.h"
#include <eigen-3.4.0/Eigen/Core>
#include <fstream>
// #include <analysis/analysis.h>

void reportPolymers(SpeciesSet &speciesSet, std::string outputDir, int iteration)
{
    std::string filepath = outputDir + "/poly_" + std::to_string(iteration) + ".dat";

    std::ofstream output;
    output.open(filepath.c_str(), std::ios::out);

    auto polymers = speciesSet.getPolymers();
    for (int i = 0; i < polymers.size(); ++i)
    {
        auto polymer = polymers[i];
        for (int j = 0; j < polymer->getDegreeOfPolymerization(); ++j)
        {
            output << +polymer->repeatUnitAtPosition(j) << " ";
        }
        output << std::endl;
    }
    output.close();
}