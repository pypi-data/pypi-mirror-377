#pragma once

#include "common.h"
#include "polymer.h"
#include "analysis/analysis.h"

/**
 * @brief Stores pointers to polymer objects of a specific type.
 * Type can infer the end group of the polymer objects but is not required to.
 *
 */
class PolymerType
{
public:
    std::string name;
    uint64_t count;

    PolymerType(std::string name_, std::vector<unitID> endGroup_) : name(name_), endGroup(endGroup_), count(0) {};

    ~PolymerType() {};

    std::vector<unitID> getEndGroup() { return endGroup; }

    void insertPolymer(Polymer *polymer)
    {
        ++count;
        polymers.push_back(polymer);
    }

    Polymer *removeRandomPolymer()
    {
        --count;
        size_t randomIndex = int(rng_utils::dis(rng_utils::rng) * polymers.size());
        Polymer *polymer = polymers[randomIndex];           // get random polymer
        polymers[randomIndex] = std::move(polymers.back()); // swap
        polymers.pop_back();                                // and pop!
        return polymer;
    }

    std::vector<Polymer *> getPolymers() { return polymers; }

private:
    std::vector<Polymer *> polymers;
    std::vector<unitID> endGroup; // endGroup to identify the terminal units on the chain end.
};

typedef PolymerType *PolymerTypePtr;

/**
 * @brief Stores pointers to PolymerType objects. These objects are passed into Reaction objects
 * to represent a group of polymer types that can undergo that reaction.
 *
 */
class PolymerTypeGroup
{
public:
    std::string name;
    uint64_t count = 0;

    PolymerTypeGroup(std::string name_, std::vector<PolymerTypePtr> polymerTypePtrs_)
        : name(name_), polymerTypePtrs(polymerTypePtrs_)
    {
        polymerTypeCounts.resize(polymerTypePtrs_.size());
    };

    ~PolymerTypeGroup() {}

    Polymer *removeRandomPolymer()
    {
        if (polymerTypePtrs.size() == 1)
        {
            --count;
            --polymerTypeCounts[0];
            return polymerTypePtrs[0]->removeRandomPolymer();
        }

        std::discrete_distribution<size_t> discrete_dis(polymerTypeCounts.begin(), polymerTypeCounts.end());
        size_t typeIndex = discrete_dis(rng_utils::rng);
        --count;
        --polymerTypeCounts[typeIndex];
        return polymerTypePtrs[typeIndex]->removeRandomPolymer();
    }

    /**
     * @brief Classifies and stores a pointer to a Polymer object into a PolymerType
     * object based on its end group. If there is only one PolymerType object, there
     * is no classification and the pointer is directly stored.
     *
     * @param Polymer* polymer
     */
    void insertPolymer(Polymer *polymer)
    {
        // No classification needed. Directly store the polymer.
        if (polymerTypePtrs.size() == 1)
        {
            ++count;
            ++polymerTypeCounts[0];
            polymerTypePtrs[0]->insertPolymer(polymer);
            return;
        }

        // Classify the polymer based on its end group.
        for (int i = 0; i < polymerTypePtrs.size(); ++i)
        {
            // console::log("PolyType" + polymerTypePtrs[i]->name);
            if (polymer->endGroupIs(polymerTypePtrs[i]->getEndGroup()))
            {
                // console::log("PolymerType match!");
                ++count;
                ++polymerTypeCounts[i];
                polymerTypePtrs[i]->insertPolymer(polymer);
                return;
            }
        }
        // auto dop = polymer->getDegreeOfPolymerization();
        // // console::debug("Degree of polymerization: " + std::to_string(dop));
        // // console::debug("Polymer end group: " + std::to_string(polymer->repeatUnitAtPosition(0)));
        // // console::debug("Polymer sequence: " + polymer->getSequenceString());
        // // console::debug("Number of polymer types: " + std::to_string(polymerTypePtrs.size()));
        // for (PolymerTypePtr polymerTypePtr : polymerTypePtrs)
        // {
        //     auto polymerTypeEndGroup = polymerTypePtr->getEndGroup();

        //     for (size_t i = 0; i < polymerTypeEndGroup.size(); ++i)
        //     {
        //         console::log("PolymerType end group: " + std::to_string(polymerTypeEndGroup[i]));
        //     }
        //     // console::log("PolymerType end group: " + std::to_string(polymerTypePtr->getEndGroup()[0]));
        //     // console::log("PolymerType end group: " + polymerTypePtr->getEndGroupString());
        // }
        // console::log("Polymer end group: " + polymerTypePtrs[0]->getEndGroup());
        console::error("End sequence for inserted polymer does not match. Exiting.....");
    }

    std::vector<PolymerTypePtr> getPolymerTypes() { return polymerTypePtrs; }

    void updatePolymerCounts()
    {
        uint64_t totalCount = 0;
        for (size_t i = 0; i < polymerTypePtrs.size(); ++i)
        {
            uint64_t typeCount = polymerTypePtrs[i]->count;
            polymerTypeCounts[i] = typeCount;
            totalCount += typeCount;
        }
        count = totalCount;
    }

    std::string toString()
    {
        return name + ": " + std::to_string(count);
    }

private:
    std::vector<PolymerTypePtr> polymerTypePtrs;
    std::vector<uint64_t> polymerTypeCounts;
};

struct PolymerGroupStruct
{
    std::string name;
    std::vector<size_t> polymerTypeIndices;
    PolymerGroupStruct(std::string name_, std::vector<size_t> polymerTypeIndices_)
        : name(name_), polymerTypeIndices(polymerTypeIndices_) {};
};

typedef PolymerTypeGroup *PolymerTypeGroupPtr;