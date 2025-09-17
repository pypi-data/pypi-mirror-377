#pragma once
#include "common.h"

namespace analysis
{
    struct SequenceStats
    {
        std::vector<uint64_t> monomerCounts;
        std::vector<uint64_t> sequenceCounts;
        std::vector<uint64_t> sequenceLengths2;

        static size_t numFields() { return 3; }

        SequenceStats()
        {
            size_t numMonomers = species::monomerIDs.size();
            monomerCounts.resize(numMonomers, 0);
            sequenceCounts.resize(numMonomers, 0);
            sequenceLengths2.resize(numMonomers, 0);
        }
    };
}

/**
 * @brief Struct to hold the state of the KMC simulation
 *
 * @param kmcStep The current KMC step
 * @param kmcTime The current KMC time
 * @param simulationTime The time elapsed since the start of the simulation
 * @param simulationTimePer1e6Steps The simulationTime divided by 1e6 KMC steps
 * @param NAV Avogadro's number * Volume
 */
struct KMCState
{
    uint64_t iteration;
    uint64_t kmcStep;
    double kmcTime;
    double simulationTime;
    double simulationTimePer1e6Steps;
    double NAV;

    static std::vector<std::string> getFieldNames()
    {
        return {"Iteration", "KMC Step", "KMC Time", "Simulation Time", "Simulation Time / 1e6 KMC Steps", "NAV"};
    }
};

/**
 * @brief Struct to hold the state of the species in the simulation
 *
 * @param unitConversions The conversion of each unit
 * @param unitCounts The count of each unit
 * @param polymerCounts The count of each polymer group
 * @param totalConversion The total conversion of the system
 */
struct SpeciesState
{
    std::vector<double> unitConversions;
    std::vector<uint64_t> unitCounts;
    std::vector<uint64_t> polymerCounts;
    double totalConversion;

    static std::vector<std::string> getFieldNames(const std::vector<std::string> &unitNames, const std::vector<std::string> &polymerGroupNames)
    {
        std::vector<std::string> names;

        // Unit conversions
        for (const auto &name : unitNames)
            names.push_back(name + " Conversion");
        names.push_back("Total Conversion");

        // Unit counts
        for (const auto &name : unitNames)
            names.push_back(name + " Count");

        // Polymer counts
        for (const auto &name : polymerGroupNames)
            names.push_back(name + " Count");

        return names;
    }
};

struct AnalysisState
{
    double nAvgChainLength = 0;
    double wAvgChainLength = 0;
    double chainLengthDispersity = 0;

    double nAvgMolecularWeight = 0;
    double wAvgMolecularWeight = 0;
    double molecularWeightDispersity = 0;

    // Sequence statistics for each monomer type
    std::vector<double> nAvgSequenceLengths;
    std::vector<double> wAvgSequenceLengths;
    std::vector<double> sequenceLengthDispersities;

    AnalysisState()
    {
        size_t numMonomers = species::monomerIDs.size();
        nAvgSequenceLengths.resize(numMonomers, 0);
        wAvgSequenceLengths.resize(numMonomers, 0);
        sequenceLengthDispersities.resize(numMonomers, 0);
    }

    static std::vector<std::string> getFieldNames(std::vector<std::string> monomerNames)
    {
        std::vector<std::string> names = {
            "nAvgChainLength",
            "wAvgChainLength",
            "chainLengthDispersity",
            "nAvgMolecularWeight",
            "wAvgMolecularWeight",
            "molecularWeightDispersity",
        };

        for (const auto &monomerName : monomerNames)
        {
            names.push_back("nAvgSequenceLength_" + monomerName);
            names.push_back("wAvgSequenceLength_" + monomerName);
            names.push_back("sequenceLengthDispersity_" + monomerName);
        }

        return names;
    }
};

/**
 * @brief Class to hold and output the state of the KMC simulation
 *
 * @param kmc The state of the KMC simulation
 * @param species The state of the SpeciesSet
 * @param analysis The state of the analysis
 *
 */
class SystemState
{
public:
    SystemState(const KMCState &kmc, const SpeciesState &species, const AnalysisState &analysis)
        : kmcState(kmc), speciesState(species), analysisState(analysis)
    {
    }

    /**
     * @brief Write the state of the simulation to an output stream
     *
     * @param out The output stream to write to
     */
    void writeState(std::ostream &out) const
    {
        out << kmcState.iteration << ','
            << kmcState.kmcStep << ','
            << kmcState.kmcTime << ','
            << kmcState.simulationTime << ','
            << kmcState.simulationTimePer1e6Steps << ','
            << kmcState.NAV;

        // Species data
        for (const auto &conv : speciesState.unitConversions)
        {
            out << ',' << conv;
        }
        out << ',' << speciesState.totalConversion;

        for (const auto &count : speciesState.unitCounts)
        {
            out << ',' << count;
        }

        for (const auto &count : speciesState.polymerCounts)
        {
            out << ',' << count;
        }

        // Analysis data
        out << ',' << analysisState.nAvgChainLength
            << ',' << analysisState.wAvgChainLength
            << ',' << analysisState.chainLengthDispersity
            << ',' << analysisState.nAvgMolecularWeight
            << ',' << analysisState.wAvgMolecularWeight
            << ',' << analysisState.molecularWeightDispersity;

        for (size_t i = 0; i < species::monomerIDs.size(); ++i)
        {
            out << ',' << analysisState.nAvgSequenceLengths[i]
                << ',' << analysisState.wAvgSequenceLengths[i]
                << ',' << analysisState.sequenceLengthDispersities[i];
        }

        out << std::endl;
    }

    /**
     * @brief Write the header for the state data to an output stream
     *
     * @param out The output stream to write to
     * @param unitNames The names of the units in the simulation
     * @param polymerNames The names of the polymer groups in the simulation
     */
    static void writeHeader(std::ostream &out,
                            const std::vector<std::string> &unitNames,
                            const std::vector<std::string> &monomerNames,
                            const std::vector<std::string> &polymerNames)
    {
        // Write KMC headers
        auto kmcHeaders = KMCState::getFieldNames();
        for (size_t i = 0; i < kmcHeaders.size(); ++i)
        {
            if (i > 0)
                out << ',';
            out << kmcHeaders[i];
        }

        // Write Species headers
        auto speciesHeaders = SpeciesState::getFieldNames(unitNames, polymerNames);
        for (const auto &header : speciesHeaders)
        {
            out << ',' << header;
        }

        // Write Analysis headers
        auto analysisHeaders = AnalysisState::getFieldNames(monomerNames);
        for (const auto &header : analysisHeaders)
        {
            out << ',' << header;
        }
        out << std::endl;
    }

private:
    const KMCState &kmcState;
    const SpeciesState &speciesState;
    const AnalysisState &analysisState;
};

class SequenceState
{
public:
    SequenceState(const KMCState &kmc_, const std::vector<analysis::SequenceStats> &stats_)
        : kmcState(kmc_), stats(stats_)
    {
    }

    static void writeHeader(std::ostream &out, std::vector<std::string> monomerNames)
    {
        out << "Iteration,KMC Time,Bucket";

        for (auto &name : monomerNames)
        {
            out << ",MonomerCount_" << name
                << ",SequenceCount_" << name
                << ",SequenceLengths2_" << name;
        }
        out << std::endl;
    };

    void writeState(std::ostream &out)
    {

        for (size_t bucket = 0; bucket < stats.size(); ++bucket)
        {
            out << kmcState.iteration << "," << kmcState.kmcTime << "," << bucket;

            for (size_t i = 0; i < species::monomerIDs.size(); ++i)
            {
                out << "," << stats[bucket].monomerCounts[i]
                    << "," << stats[bucket].sequenceCounts[i]
                    << "," << stats[bucket].sequenceLengths2[i];
            }
            out << std::endl;
        }
    }

private:
    const KMCState &kmcState;
    const std::vector<analysis::SequenceStats> &stats;
};