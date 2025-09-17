#pragma once
#include <string>
#include <iostream>
#include <fstream>
#include "utils/parse.h"

namespace config
{

    struct CommandLineConfig
    {
        std::string inputFilepath;
        std::string outputFilepath;
        std::string polymerOutputDir;
        std::string sequenceFilepath;
    };

    struct SimulationConfig
    {
        uint64_t numParticles;
        double terminationTime;
        double analysisTime;
    };

    namespace // private functions
    {
        bool validateInputFile(const std::string &filepath)
        {
            std::ifstream file(filepath);
            if (!file.is_open())
            {
                std::cerr << "Cannot open input file: " << filepath << std::endl;
                return false;
            }
            file.close();
            return true;
        }

        bool prepareOutputFile(const std::string &filepath)
        {
            std::ofstream outfile(filepath);
            if (!outfile.is_open())
            {
                std::cerr << "Failed to open output file: " << filepath << std::endl;
                return false;
            }
            outfile.close();
            return true;
        }
    }

    CommandLineConfig parseArguments(int argc, char **argv)
    {
        if (argc < 3)
        {
            std::cerr
                << "Usage: " << argv[0]
                << " <inputFilePath> <outputFilePath>"
                << " [--report-polymers=<directory>] [--report-sequences=<filepath>]\n";
            exit(EXIT_FAILURE);
        }

        CommandLineConfig config;
        config.inputFilepath = argv[1];
        config.outputFilepath = argv[2];

        // Parse optional flags
        std::vector<std::string> argStrings;
        for (int i = 3; i < argc; ++i)
        {
            argStrings.push_back(argv[i]);
        }
        
        input::readVariable(argStrings, "--report-polymers", config.polymerOutputDir);
        input::readVariable(argStrings, "--report-sequences", config.sequenceFilepath);

        if (!config::validateInputFile(config.inputFilepath))
            exit(EXIT_FAILURE);

        if (!prepareOutputFile(config.outputFilepath))
            exit(EXIT_FAILURE);

        return config;
    }
}