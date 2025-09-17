#pragma once

#include "common.h"
#include "eigen-3.4.0/Eigen/Core"
#include "state.h"

namespace analysis
{
    struct SequenceSummary
    {
        std::vector<Eigen::MatrixXd> sequenceStatsTensor;
        std::vector<SequenceStats> avgPositionalStats;

        SequenceSummary(std::vector<Eigen::MatrixXd> t, std::vector<SequenceStats> a)
            : sequenceStatsTensor(t), avgPositionalStats(a) {}
    };

    static size_t getBucketIndex(size_t position, size_t chainLength, size_t numBuckets)
    {
        if (chainLength <= 1)
            return 0;

        double normalizedPos = static_cast<double>(position) / (chainLength);

        size_t bucket = static_cast<size_t>(normalizedPos * numBuckets);
        return (bucket == numBuckets) ? numBuckets - 1 : bucket;
        // return std::min(bucket, numBuckets - 1);
    }

    std::vector<SequenceStats> calculatePositionalSequenceStats(std::vector<unitID> &sequence, size_t numBuckets)
    {
        std::vector<SequenceStats> stats(numBuckets);
        if (sequence.empty())
            return stats;

        unitID currentMonomer = 0;
        size_t currentSequenceLength = 0;
        bool inSequence = false;

        for (size_t i = 0; i < sequence.size(); ++i)
        {
            size_t bucket = getBucketIndex(i, sequence.size(), numBuckets);
            unitID id = sequence[i];

            // Skip non-monomer units
            if (!species::isIn(id, species::monomerIDs))
                continue;

            size_t monomerIndex = species::getIndexIn(id, species::monomerIDs);
            stats[bucket].monomerCounts[monomerIndex]++;

            if (id == currentMonomer)
            {
                currentSequenceLength++;
            }
            else if (inSequence)
            {
                size_t prevIndex = species::getIndexIn(currentMonomer, species::monomerIDs);
                stats[bucket].sequenceCounts[prevIndex] += 1;
                stats[bucket].sequenceLengths2[prevIndex] += currentSequenceLength * currentSequenceLength;
                currentSequenceLength = 1;
            }
            else
            {
                inSequence = true;
                currentSequenceLength = 1;
            }

            currentMonomer = id;
        }

        // Add the stats for the last sequence
        size_t bucket = getBucketIndex(sequence.size() - 1, sequence.size(), numBuckets);
        size_t lastMonomerIdx = species::getIndexIn(currentMonomer, species::monomerIDs);
        stats[bucket].sequenceCounts[lastMonomerIdx] += 1;
        stats[bucket].sequenceLengths2[lastMonomerIdx] += currentSequenceLength * currentSequenceLength;

        return stats;
    }

    SequenceSummary calculateSequenceSummary(
        std::vector<std::vector<unitID>> &sequences,
        std::vector<std::vector<analysis::SequenceStats>> &precomputedStats)
    {
        size_t numSequences = sequences.size();
        size_t numPrecomputedSequences = precomputedStats.size();
        size_t numPolymers = numSequences + numPrecomputedSequences;
        size_t numMonomers = species::monomerIDs.size();
        size_t numFields = SequenceStats::numFields();
        size_t numBuckets = species::NUM_BUCKETS;

        std::vector<Eigen::MatrixXd> sequenceStatsTensor(numBuckets); // numBuckets matrices
        for (auto &matrix : sequenceStatsTensor)
        {
            matrix = Eigen::MatrixXd::Zero(numPolymers, numMonomers * numFields); // Each matrix is (polymers × stats)
        }

        std::vector<SequenceStats> avgPositionalStats(numBuckets);

        // console::log("Num sequences: " + std::to_string(numSequences));
        for (size_t i = 0; i < numSequences; ++i)
        {
            auto stats = calculatePositionalSequenceStats(sequences[i], numBuckets);
            for (size_t bucket = 0; bucket < numBuckets; ++bucket)
            {
                for (size_t monIdx = 0; monIdx < numMonomers; ++monIdx)
                {
                    size_t colBase = monIdx * numFields;
                    sequenceStatsTensor[bucket](i, colBase + 0) = stats[bucket].monomerCounts[monIdx];
                    sequenceStatsTensor[bucket](i, colBase + 1) = stats[bucket].sequenceCounts[monIdx];
                    sequenceStatsTensor[bucket](i, colBase + 2) = stats[bucket].sequenceLengths2[monIdx];

                    avgPositionalStats[bucket].monomerCounts[monIdx] += stats[bucket].monomerCounts[monIdx];
                    avgPositionalStats[bucket].sequenceCounts[monIdx] += stats[bucket].sequenceCounts[monIdx];
                    avgPositionalStats[bucket].sequenceLengths2[monIdx] += stats[bucket].sequenceLengths2[monIdx];
                }
            }
        }
        // console::log("Num precomputed sequences: " + std::to_string(numPrecomputedSequences));
        for (size_t i = 0; i < numPrecomputedSequences; ++i)
        {
            auto stats = precomputedStats[i];
            size_t tensorIndex = numSequences + i;

            for (size_t bucket = 0; bucket < numBuckets; ++bucket)
            {
                for (size_t monIdx = 0; monIdx < numMonomers; ++monIdx)
                {
                    size_t colBase = monIdx * numFields;
                    sequenceStatsTensor[bucket](tensorIndex, colBase + 0) = stats[bucket].monomerCounts[monIdx];
                    sequenceStatsTensor[bucket](tensorIndex, colBase + 1) = stats[bucket].sequenceCounts[monIdx];
                    sequenceStatsTensor[bucket](tensorIndex, colBase + 2) = stats[bucket].sequenceLengths2[monIdx];

                    avgPositionalStats[bucket].monomerCounts[monIdx] += stats[bucket].monomerCounts[monIdx];
                    avgPositionalStats[bucket].sequenceCounts[monIdx] += stats[bucket].sequenceCounts[monIdx];
                    avgPositionalStats[bucket].sequenceLengths2[monIdx] += stats[bucket].sequenceLengths2[monIdx];
                }
            }
        }

        return SequenceSummary{sequenceStatsTensor, avgPositionalStats};
    }


    Eigen::MatrixXd calculateSequenceStatsMatrix(const std::vector<Eigen::MatrixXd> &sequenceStatsTensor)
    // Calculate the average sequence statistics (across all buckets) per polymer
    {
        if (sequenceStatsTensor.empty())
            return Eigen::MatrixXd();

        size_t numBuckets = sequenceStatsTensor.size();
        size_t numPolymers = sequenceStatsTensor[0].rows();
        size_t numCols = sequenceStatsTensor[0].cols();

        // console::log("Num buckets: " + std::to_string(numBuckets));
        // console::log("Num polymers: " + std::to_string(numPolymers));
        // console::log("Num cols: " + std::to_string(numCols));

        // Result matrix: polymers × (monomers*fields)
        Eigen::MatrixXd result = Eigen::MatrixXd::Zero(numPolymers, numCols);

        // Get the average stats (across all buckets) for each polymer
        for (size_t i = 0; i < numPolymers; ++i)
        {
            for (size_t bucket = 0; bucket < numBuckets; ++bucket)
            {
                result.row(i) += sequenceStatsTensor[bucket].row(i);
            }
            result.row(i) /= numBuckets;
        }

        return result;
    }

    void analyzeChainLengthDist(Eigen::MatrixXd &sequenceStatsMatrix, std::vector<Unit> &units, AnalysisState &state)
    {
        if (sequenceStatsMatrix.rows() == 0 || sequenceStatsMatrix.cols() == 0)
        {
            // console::warning("No sequence data found.");
            return;
        }

        Eigen::MatrixXd monomerCountDist = sequenceStatsMatrix.leftCols(species::monomerIDs.size());
        // console::log("Dimensions monomerCountDist: " + std::to_string(monomerCountDist.rows()) + " " + std::to_string(monomerCountDist.cols()));
        // std::cout << "monomerCountDist: " << monomerCountDist << std::endl;
        Eigen::VectorXd nAvgChainLengthDist = monomerCountDist.colwise().mean();
        // console::log("Dimensions nAvgChainLengthDist: " + std::to_string(nAvgChainLengthDist.rows()) + " " + std::to_string(nAvgChainLengthDist.cols()));
        
        
        state.nAvgChainLength = nAvgChainLengthDist.mean();
        // console::log(std::to_string(state.nAvgChainLength));

        // std::cout << "nAvgChainLengthDist: " << nAvgChainLengthDist << std::endl;

        if (state.nAvgChainLength != 0)
        {
            state.wAvgChainLength = nAvgChainLengthDist.array().square().mean() / state.nAvgChainLength;
            state.chainLengthDispersity = state.wAvgChainLength / state.nAvgChainLength;
        }

        Eigen::MatrixXd weightedMatrix = monomerCountDist;
        for (auto &id : species::monomerIDs)
        {
            size_t monIdx = species::getIndexIn(id, species::monomerIDs);
            weightedMatrix.col(monIdx) *= units[id].FW;
        }
        Eigen::VectorXd nAvgMolecularWeightDist = weightedMatrix.rowwise().sum();

        state.nAvgMolecularWeight = nAvgMolecularWeightDist.mean();
        if (state.nAvgMolecularWeight != 0)
        {
            state.wAvgMolecularWeight = nAvgMolecularWeightDist.array().square().mean() / state.nAvgMolecularWeight;
            state.molecularWeightDispersity = state.wAvgMolecularWeight / state.nAvgMolecularWeight;
        }
    }

    void analyzeSequenceLengthDist(Eigen::MatrixXd &sequenceStatsMatrix, AnalysisState &state)
    {
        size_t numFields = SequenceStats::numFields();

        for (auto &id : species::monomerIDs)
        {
            size_t monIdx = species::getIndexIn(id, species::monomerIDs);
            size_t colBase = monIdx * numFields;

            if (sequenceStatsMatrix.rows() == 0 || sequenceStatsMatrix.cols() <= colBase + 2)
            {
                state.nAvgSequenceLengths[monIdx] = 0;
                state.wAvgSequenceLengths[monIdx] = 0;
                state.sequenceLengthDispersities[monIdx] = 0;
                // console::warning("No sequence data found.");
                continue;
            }

            auto monomerCount = sequenceStatsMatrix.col(colBase).sum();
            auto sequenceCount = sequenceStatsMatrix.col(colBase + 1).sum();
            auto sequenceLengths2 = sequenceStatsMatrix.col(colBase + 2).sum();

            if (sequenceCount > 0 && monomerCount > 0)
            {
                state.nAvgSequenceLengths[monIdx] = monomerCount / sequenceCount;
                state.wAvgSequenceLengths[monIdx] = sequenceLengths2 / monomerCount;
                state.sequenceLengthDispersities[monIdx] = state.wAvgSequenceLengths[monIdx] / state.nAvgSequenceLengths[monIdx];
            }
            else
            {
                state.nAvgSequenceLengths[monIdx] = 0;
                state.wAvgSequenceLengths[monIdx] = 0;
                state.sequenceLengthDispersities[monIdx] = 0;
            }
        }
    }

}
