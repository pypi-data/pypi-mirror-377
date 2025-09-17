#pragma once
#include "common.h"
#include "kmc/state.h"
#include "species/polymer_type.h"

class SpeciesSet
{
public:
    SpeciesSet() {};

    SpeciesSet(
        std::vector<PolymerType> &polymerTypes_,
        std::vector<PolymerGroupStruct> &PolymerGroupStructs_,
        std::vector<Unit> units_,
        size_t numParticles_) : polymerTypes(std::move(polymerTypes_)), units(std::move(units_)), numParticles(numParticles_)
    {
        // Calculate NAV
        double totalC0 = 0;
        for (auto &unitID : species::unitIDs)
            totalC0 += units[unitID].C0;
        NAV = numParticles / totalC0;

        // Set initial counts
        for (auto &unitID : species::unitIDs)
        {
            uint64_t initialCount = static_cast<uint64_t>(units[unitID].C0 * NAV);
            units[unitID].setInitialCount(initialCount);
        }

        polymerGroups.reserve(PolymerGroupStructs_.size());
        polymerGroupPtrs.reserve(PolymerGroupStructs_.size());

        // Creating polymer groups
        for (auto &polymerGroup : PolymerGroupStructs_)
        {
            auto indices = polymerGroup.polymerTypeIndices;
            std::vector<PolymerTypePtr> polymerSubTypePtrs;
            polymerSubTypePtrs.reserve(indices.size());
            for (auto index : indices)
                polymerSubTypePtrs.push_back(&polymerTypes[index]);

            polymerGroups.push_back(PolymerTypeGroup(polymerGroup.name, polymerSubTypePtrs));
            polymerGroupPtrs.push_back(&polymerGroups.back());
        }
    };

    SpeciesState getStateData() const
    {
        SpeciesState data;

        // Unit conversions
        for (auto &id : species::unitIDs)
            data.unitConversions.push_back(units[id].calculateConversion());

        // Unit counts
        for (auto &id : species::unitIDs)
            data.unitCounts.push_back(units[id].count);

        // Polymer counts
        for (const auto &polymerGroup : polymerGroups)
            data.polymerCounts.push_back(polymerGroup.count);

        // Total conversion
        data.totalConversion = calculateConversion();

        return data;
    }

    std::vector<std::string> getUnitNames() const
    {
        std::vector<std::string> names;
        for (auto &unitID : species::unitIDs)
            names.push_back(units[unitID].name);
        return names;
    }

    std::vector<std::string> getMonomerNames() const
    {
        std::vector<std::string> names;
        for (auto &monomerID : species::monomerIDs)
            names.push_back(units[monomerID].name);
        return names;
    }

    std::vector<std::string> getPolymerGroupNames() const
    {
        std::vector<std::string> names;
        for (auto &polymerGroup : polymerGroups)
            names.push_back(polymerGroup.name);
        return names;
    }

    double calculateConversion() const
    {
        double numerator = 0;
        double denominator = 0;
        uint64_t initialCount;

        for (auto id : species::monomerIDs)
        {
            initialCount = units[id].getInitialCount();
            numerator += initialCount - units[id].count;
            denominator += initialCount;
        }
        if (denominator == 0)
            return 0;

        return numerator / denominator;
    };

    void updatePolyTypeGroups()
    {
        for (size_t i = 0; i < polymerGroups.size(); ++i)
            polymerGroupPtrs[i]->updatePolymerCounts();
    };

    std::vector<Polymer *> getPolymers()
    {
        // Reserve space for all polymers
        uint64_t numPolymers = 0;
        for (auto polymerType : polymerTypes)
            numPolymers += polymerType.count;
        std::vector<Polymer *> polymers;
        polymers.reserve(numPolymers);
        // console::log("Reserving space for " + std::to_string(numPolymers) + " polymers");

        // Add all polymer pointers to the reserved space
        for (auto polymerType : polymerTypes)
        {

            std::vector<Polymer *> typePolymers = polymerType.getPolymers();
            polymers.insert(polymers.end(), typePolymers.begin(), typePolymers.end());
        }
        return polymers;
    }

    std::vector<std::vector<unitID>> getAllSequences(std::vector<Polymer *> &polymers)
    {

        std::vector<std::vector<unitID>> sequences;
        sequences.reserve(polymers.size());

        for (auto *polymer : polymers)
        {
            if (!polymer->isCompressed())
                sequences.push_back(polymer->getSequence());
        }
        return sequences;
    }

    std::vector<std::vector<analysis::SequenceStats>> getAllSequenceStats(std::vector<Polymer *> &polymers)
    {
        std::vector<std::vector<analysis::SequenceStats>> allStats;
        for (size_t i = 0; i < polymers.size(); ++i)
        {
            if (polymers[i]->isCompressed())
                allStats.push_back(polymers[i]->getPositionalStats());
        }
        return allStats;
    }

    std::vector<Unit> &getUnits() { return units; }
    std::vector<PolymerTypeGroup> &getPolyTypeGroups() { return polymerGroups; }
    std::vector<PolymerTypeGroupPtr> &getPolymerGroupPtrs() { return polymerGroupPtrs; }
    double getNAV() { return NAV; }

private:
    std::vector<PolymerType> polymerTypes;
    std::vector<PolymerTypeGroup> polymerGroups;
    std::vector<PolymerTypeGroupPtr> polymerGroupPtrs;

    std::vector<Unit> units;
    size_t numParticles;
    double NAV;
};