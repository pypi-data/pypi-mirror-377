#pragma once
#include <unordered_map>
#include <species/unit.h>
#include <vector>

#define AVOGADROS 6.022149e+23;

namespace species
{
    static const std::string UNIT = "U";
    static const std::string MONOMER = "M";
    static const std::string INITIATOR = "I";
    static const std::string POLYMER = "P";
    static const std::string UNDEFINED = "?";

    static const size_t NUM_BUCKETS = 30;

    // Unit ID Registry – Global State
    static std::vector<unitID> unitIDs;
    static std::vector<unitID> monomerIDs;
    static std::vector<unitID> initiatorIDs;

    static unitID registerNewUnit()
    {
        unitID newID = unitIDs.size() + 1;
        unitIDs.push_back(newID);
        return newID;
    }

    inline unitID registerNewMonomer()
    {
        unitID id = registerNewUnit();
        monomerIDs.push_back(id);
        return id;
    }

    inline unitID registerNewInitiator()
    {
        unitID id = registerNewUnit();
        initiatorIDs.push_back(id);
        return id;
    }

    size_t getIndexIn(unitID id, std::vector<unitID>& ids) {
        auto it = std::find(ids.begin(), ids.end(), id);
        if (it != ids.end())
            return std::distance(ids.begin(), it);
        return SIZE_MAX;
    }

    bool isIn(unitID id, std::vector<unitID>& ids) {
        return getIndexIn(id, ids) != SIZE_MAX;
    }
};