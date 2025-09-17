#pragma once
#include "common.h"
#include "reactions.h"

/**
 * @brief Stores set of all reactions and can calculate cumulative properties such as
 * reaction rates and probabilities.
 *
 */
class ReactionSet
{
public:
    size_t chooseRandomReactionIndex()
    {
        double randomNumber = rng_utils::dis(rng_utils::rng);
        for (size_t reactionIndex = 0; reactionIndex < numReactions; ++reactionIndex)
        {
            if (randomNumber <= reactionCumulativeProbabilities[reactionIndex])
                return reactionIndex;
        }
        console::error("Uh oh! No reaction was chosen - something is wrong with the cumulative probability vector. Exiting.");
        return 0; // Not reached as console::error will exit
    }

    /**
     * @brief Calculate and update reaction probabilities. First updates the reaction rates,
     * then calculates the probability and cumulative probability vectors.
     */
    void updateReactionProbabilities(double NAV_)
    {
        NAV = NAV_;
        updateReactionRates();
        reactionProbabilities[0] = reactionRates[0] / totalReactionRate;
        reactionCumulativeProbabilities[0] = reactionProbabilities[0];
        for (size_t i = 1; i < numReactions; ++i)
        {
            reactionProbabilities[i] = reactionRates[i] / totalReactionRate;
            reactionCumulativeProbabilities[i] = reactionProbabilities[i] + reactionCumulativeProbabilities[i - 1];
        }
    }

    ReactionSet(std::vector<Reaction *> reactions_) : reactions(reactions_)
    {
        numReactions = reactions.size();
        reactionRates.resize(numReactions);
        reactionProbabilities.resize(numReactions);
        reactionCumulativeProbabilities.resize(numReactions);
    };

    ReactionSet() {};
    ~ReactionSet() {};

    Reaction *getReaction(size_t reactionIndex) { return reactions[reactionIndex]; }
    int getNumReactions() { return numReactions; }
    double getTotalReactionRate() { return totalReactionRate; }
    void setNAV(double NAV_) { NAV = NAV_; }
    double getNAV() { return NAV; }

private:
    int numReactions = 0;
    std::vector<Reaction *> reactions;

    double totalReactionRate = 0;
    std::vector<double> reactionRates;
    std::vector<double> reactionProbabilities;
    std::vector<double> reactionCumulativeProbabilities;

    double NAV;

    /**
     * @brief Calculate and update reaction rates for all reactions.
     * Also updates total reaction rate.
     */
    void updateReactionRates()
    {
        totalReactionRate = 0;
        for (size_t i = 0; i < numReactions; ++i)
        {
            reactionRates[i] = reactions[i]->calculateRate(NAV);
            totalReactionRate += reactionRates[i];
        }
    }
};