#pragma once
#include "common.h"
#include "config/config.h"
#include "reactions/reaction_set.h"
#include "species/species_set.h"
#include "analysis/analysis.h"
#include "state.h"
#include "analysis/report.h"

/**
 * @brief Kinetic Monte Carlo simulation class
 *
 */
class KMC
{
public:
    KMC(SpeciesSet &species, ReactionSet &reactions, config::CommandLineConfig config_, config::SimulationConfig options_)
        : speciesSet(std::move(species)), reactionSet(std::move(reactions)), config(config_), options(options_)
    {
        NAV = speciesSet.getNAV();

        speciesSet.updatePolyTypeGroups();

        reactionSet.updateReactionProbabilities(NAV);

        stateOutput = std::ofstream(config.outputFilepath);

        if (config.sequenceFilepath != "")
            sequenceStateOutput = std::ofstream(config.sequenceFilepath);
    };

    void analyze()
    {
        auto polymers = speciesSet.getPolymers();
        auto allSequenceStats = speciesSet.getAllSequenceStats(polymers);
        auto allSequences = speciesSet.getAllSequences(polymers);

        auto sequenceSummary = analysis::calculateSequenceSummary(allSequences, allSequenceStats);
        auto sequenceStatsMatrix = analysis::calculateSequenceStatsMatrix(sequenceSummary.sequenceStatsTensor);

        if (config.sequenceFilepath != "")
        {
            auto kmcState = getStateData();
            SequenceState sequenceState(kmcState, sequenceSummary.avgPositionalStats);
            sequenceState.writeState(sequenceStateOutput);
        }

        AnalysisState analysisState;
        analysis::analyzeChainLengthDist(sequenceStatsMatrix, speciesSet.getUnits(), analysisState);
        analysis::analyzeSequenceLengthDist(sequenceStatsMatrix, analysisState);
        currentAnalysisState = analysisState;

        if (config.polymerOutputDir != "")
        {
            reportPolymers(speciesSet, config.polymerOutputDir, iteration);
        }
    }

    void run()
    {
        startTime = std::chrono::steady_clock::now();

        printStateHeader();
        printCurrentState();
        printSequenceStateHeader();

        auto timeMax = options.terminationTime;
        auto timeStep = options.analysisTime;

        while (kmcTime < timeMax)
        {
            iteration += 1;
            reactionCounts.reserve(reactionSet.getNumReactions());
            for (size_t i = 0; i < reactionSet.getNumReactions(); ++i)
                reactionCounts[i] = 0;

            runToTime(kmcTime + timeStep);

            analyze();

            printCurrentState();
            // printCurrentSequenceState();
        }
    }

    config::CommandLineConfig &getConfig() { return config; };
    config::SimulationConfig &getOptions() { return options; };
    SpeciesSet &getSpeciesSet() { return speciesSet; };
    ReactionSet &getReactionSet() { return reactionSet; };
    uint64_t getKMCStep() { return kmcStep; };
    double getKMCTime() { return kmcTime; };

private:
    // ********** Simulation functions **********

    void runToTime(double time)
    {
        while (kmcTime < time)
        {
            if (reactionSet.getTotalReactionRate() == 0)
                break;

            step();
        }
    }

    void step()
    {
        size_t reactionIndex = reactionSet.chooseRandomReactionIndex();

        reactionCounts[reactionIndex]++;

        Reaction *reaction = reactionSet.getReaction(reactionIndex);

        reaction->react();

        speciesSet.updatePolyTypeGroups();

        reactionSet.updateReactionProbabilities(NAV);

        updateTime();
    }

    void updateTime()
    {
        double rn = rng_utils::dis(rng_utils::rng) + 1e-40;
        kmcTime -= log(rn) / reactionSet.getTotalReactionRate();
        kmcStep += 1;
    }

    // ********** State functions **********

    KMCState getStateData() const
    {
        auto currentTime = std::chrono::steady_clock::now();
        double elapsedSeconds = std::chrono::duration_cast<std::chrono::milliseconds>(currentTime - startTime).count() / 1000.;
        double timePer1e6Steps = 0;
        if (kmcStep > 0)
        {
            timePer1e6Steps = elapsedSeconds / (kmcStep / 1e6);
        }

        return KMCState{
            iteration,
            kmcStep,
            kmcTime,
            elapsedSeconds,
            timePer1e6Steps,
            NAV};
    }

    void printCurrentState()
    {
        auto kmcState = getStateData();
        auto speciesState = speciesSet.getStateData();
        auto analysisState = currentAnalysisState;

        SystemState state(kmcState, speciesState, analysisState);
        state.writeState(stateOutput);
    }

    void printStateHeader()
    {
        const auto unitNames = speciesSet.getUnitNames();
        const auto monomerNames = speciesSet.getMonomerNames();
        const auto polymerNames = speciesSet.getPolymerGroupNames();

        SystemState::writeHeader(stateOutput, unitNames, monomerNames, polymerNames);
    }

    void printSequenceStateHeader()
    {
        if (config.sequenceFilepath != "")
            SequenceState::writeHeader(sequenceStateOutput, speciesSet.getMonomerNames());
    }

    config::CommandLineConfig config;
    config::SimulationConfig options;

    uint64_t kmcStep = 0;
    double kmcTime = 0;
    double NAV;

    ReactionSet reactionSet;
    SpeciesSet speciesSet;

    uint64_t iteration = 0;
    std::vector<int> reactionCounts;
    AnalysisState currentAnalysisState;
    std::chrono::steady_clock::time_point startTime;
    std::ofstream stateOutput; // console output stream (default is std::cout)?
    std::ofstream sequenceStateOutput;
};