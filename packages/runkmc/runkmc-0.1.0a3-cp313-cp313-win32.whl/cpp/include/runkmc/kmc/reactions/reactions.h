#pragma once
#include "common.h"
#include "species/polymer_type.h"
#include "species/polymer.h"
#include "species/unit.h"
#include "reaction_print.h"
#include <memory>

struct RateConstant
{
    std::string name;
    double value;
    RateConstant(std::string name_, double value_)
        : name(name_), value(value_) {};
};

enum ReactionType
{
    ELEMENTARY,
    INITIATOR_DECOMPOSITION,
    INITIATION,
    PROPAGATION,
    DEPROPAGATION,
    TERMINATION_C,
    TERMINATION_D,
    CHAINTRANSFER_M,
    CHAINTRANSFER_S,
    THERM_INIT_M
};

class Reaction
{
public:
    ReactionType type;
    Reaction(ReactionType type_, double rateConstant_, size_t numPolyReactants, size_t numUnitReactants,
             size_t numPolyProducts, size_t numUnitProducts) : type(type_), rateConstant(rateConstant_)
    {
        polyReactants.resize(numPolyReactants);
        unitReactants.resize(numUnitReactants);
        polyProducts.resize(numPolyProducts);
        unitProducts.resize(numUnitProducts);
    };
    virtual ~Reaction() = default;
    Reaction(const Reaction &) = default;
    Reaction &operator=(const Reaction &) = default;
    Reaction(Reaction &&) = default;
    Reaction &operator=(Reaction &&) = default;

    /**
     * @brief Calculates rate of reaction for a given NAV.
     *
     * @return double
     */
    virtual double calculateRate(double NAV) = 0;

    /**
     * @brief Undergoes reaction. Automatically updates unit counts and moves pointers to Polymer objects
     * into containers based on type.
     */
    virtual void react() = 0;

    std::string toString()
    {
        return rxn_print::reactionToString(unitReactants, polyReactants, unitProducts, polyProducts);
    }

    std::string toStringWithCounts()
    {
        return rxn_print::reactionCountsToString(unitReactants, polyReactants, unitProducts, polyProducts);
    }

protected:
    std::vector<PolymerTypeGroupPtr> polyReactants;
    std::vector<Unit *> unitReactants;
    std::vector<PolymerTypeGroupPtr> polyProducts;
    std::vector<Unit *> unitProducts;

    double rateConstant;
};

/// FIX MEEEEEEEEEEE
/**
 * @brief Elementary reaction (e.g., A + B ––> C)
 * Arbitrary number of unit reactants forming arbitrary number of unit products.
 */
class Elementary : virtual public Reaction
{
public:
    Elementary(double rateConstant, std::vector<Unit *> unitReactants_, std::vector<Unit *> unitProducts_)
        : Reaction(ELEMENTARY, rateConstant, 0, unitReactants_.size(), 0, unitProducts_.size())
    {
        unitReactants = std::move(unitReactants_);
        unitProducts = std::move(unitProducts_);
    };

    void react()
    {
        for (size_t i = 0; i < unitReactants.size(); ++i)
            --unitReactants[i]->count;
        for (size_t i = 0; i < unitProducts.size(); ++i)
            ++unitProducts[i]->count;
    }

    double calculateRate()
    {
        double rate = rateConstant;
        for (size_t i = 0; i < unitReactants.size(); ++i)
            rate *= unitReactants[i]->count;
        return rate;
    }
};

/**
 * @brief Initiator decomposition reaction (e.g., AIBN ––> I + I)
 * Decomoposition of initiator molecule to form two active primary radicals.
 */
class InitiatorDecomposition : public Reaction
{
public:
    InitiatorDecomposition(double rateConstant, Unit *unitReactant, Unit *unitProduct1, Unit *unitProduct2, double efficiency_)
        : Reaction(INITIATOR_DECOMPOSITION, rateConstant, 0, 1, 0, 2), efficiency(efficiency_)
    {
        unitReactants[0] = unitReactant;
        unitProducts[0] = unitProduct1;
        unitProducts[1] = unitProduct2;
    }

    void react()
    {
        --unitReactants[0]->count;
        if (rng_utils::dis(rng_utils::rng) <= efficiency)
            ++unitProducts[0]->count;
        if (rng_utils::dis(rng_utils::rng) <= efficiency)
            ++unitProducts[1]->count;
    }

    double calculateRate(double NAV)
    {
        return rateConstant * unitReactants[0]->count;
    }

protected:
    double efficiency; // Reaction efficiency (0, 1]
};

/**
 * @brief Initiation reaction (e.g., I + A ––> IA)
 * Reaction between a radical molecule and monomer to create a polymer.
 */
class Initiation : public Reaction
{
public:
    Initiation(double rateConstant, Unit *unitReactant1, Unit *unitReactant2, PolymerTypeGroupPtr polyProduct)
        : Reaction(INITIATION, rateConstant, 0, 2, 1, 0)
    {
        unitReactants[0] = unitReactant1; // initiator
        unitReactants[1] = unitReactant2; // monomer
        polyProducts[0] = polyProduct;
    };

    void react()
    {
        --unitReactants[0]->count;
        --unitReactants[1]->count;
        Polymer *polymer = new Polymer();
        polymer->addUnitToEnd((unitReactants[0])->ID);
        polymer->addUnitToEnd((unitReactants[1])->ID);
        polyProducts[0]->insertPolymer(polymer);
    }

    double calculateRate(double NAV)
    {
        // REMOVE_ME IS ONLY FOR TESTING
        int REMOVE_ME = 1;
        return REMOVE_ME * rateConstant * unitReactants[0]->count * unitReactants[1]->count / NAV;
    }
};

/**
 * @brief Propagation reaction (e.g., P[A,A] + B ––> P[A,B] + B).
 * Adds a monomer unit to the terminal chain end.
 */
class Propagation : public Reaction
{
public:
    Propagation(double rateConstant, PolymerTypeGroupPtr polyReactant, Unit *unitReactant, PolymerTypeGroupPtr polyProduct)
        : Reaction(PROPAGATION, rateConstant, 1, 1, 1, 0)
    {
        polyReactants[0] = polyReactant;
        unitReactants[0] = unitReactant;
        polyProducts[0] = polyProduct;
    }

    void react()
    {
        --unitReactants[0]->count;
        Polymer *polymer = polyReactants[0]->removeRandomPolymer();
        polymer->addUnitToEnd(unitReactants[0]->ID);
        polyProducts[0]->insertPolymer(polymer);
    }

    double calculateRate(double NAV)
    {
        return rateConstant * polyReactants[0]->count * unitReactants[0]->count / NAV;
    }
};

/**
 * @brief Depropagation reaction (e.g., P[A,A] ––> P[?,A] + A).
 * Removes the terminal chain end unit.
 */
class Depropagation : public Reaction
{
public:
    Depropagation(double rateConstant, PolymerTypeGroupPtr polyReactant, PolymerTypeGroupPtr polyProduct, Unit *unitProduct)
        : Reaction(DEPROPAGATION, rateConstant, 1, 0, 1, 1)
    {
        polyReactants[0] = polyReactant;
        polyProducts[0] = polyProduct;
        unitProducts[0] = unitProduct;
    }

    void react()
    {
        ++unitProducts[0]->count;
        Polymer *polymer = polyReactants[0]->removeRandomPolymer();
        size_t dop_0 = polymer->getDegreeOfPolymerization();
        polymer->removeUnitFromEnd();
        size_t dop_1 = polymer->getDegreeOfPolymerization();
        assert(dop_0 - dop_1 == 1);
        polyProducts[0]->insertPolymer(polymer);
    }

    double calculateRate(double NAV)
    {
        return rateConstant * polyReactants[0]->count;
    }
};

/**
 * @brief Termination by disproportionation (e.g., P[A,A] + P[B,A] ––> D + D).
 *
 */
class TerminationDisproportionation : public Reaction
{
public:
    TerminationDisproportionation(double rateConstant, PolymerTypeGroupPtr polyReactant1, PolymerTypeGroupPtr polyReactant2,
                                  PolymerTypeGroupPtr polyProduct1, PolymerTypeGroupPtr polyProduct2, uint8_t sameReactant_)
        : Reaction(TERMINATION_D, rateConstant, 2, 0, 2, 0), sameReactant(sameReactant_)
    {

        polyReactants[0] = polyReactant1;
        polyReactants[1] = polyReactant2;
        polyProducts[0] = polyProduct1;
        polyProducts[1] = polyProduct2;
    }

    void react()
    {
        Polymer *polymer1 = polyReactants[0]->removeRandomPolymer();
        Polymer *polymer2 = polyReactants[1]->removeRandomPolymer();
        polymer1->terminateByDisproportionation();
        polymer2->terminateByDisproportionation();
        polyProducts[0]->insertPolymer(polymer1);
        polyProducts[1]->insertPolymer(polymer2);
    }

    double calculateRate(double NAV)
    {
        return rateConstant * polyReactants[0]->count * (polyReactants[1]->count - sameReactant) / NAV;
    }

private:
    uint8_t sameReactant; // True = 1, False = 0
};

/**
 * @brief Termination by combination (e.g., P[A,A] + P[B,A] ––> D).
 *
 */
class TerminationCombination : public Reaction
{
public:
    TerminationCombination(double rateConstant, PolymerTypeGroupPtr polyReactant1, PolymerTypeGroupPtr polyReactant2,
                           PolymerTypeGroupPtr polyProduct1, uint8_t sameReactant_)
        : Reaction(TERMINATION_C, rateConstant, 2, 0, 1, 0), sameReactant(sameReactant_)
    {
        polyReactants[0] = polyReactant1;
        polyReactants[1] = polyReactant2;
        polyProducts[0] = polyProduct1;
    }

    void react()
    {
        Polymer *polymer1 = polyReactants[0]->removeRandomPolymer();
        Polymer *polymer2 = polyReactants[1]->removeRandomPolymer();
        polymer1->terminateByCombination(polymer2);
        polyProducts[0]->insertPolymer(polymer1);
    }

    double calculateRate(double NAV)
    {
        return rateConstant * polyReactants[0]->count * (polyReactants[1]->count - sameReactant) / NAV;
    }

private:
    uint8_t sameReactant; // True = 1, False = 0
};

class ChainTransferToMonomer : public Reaction
{
public:
    ChainTransferToMonomer(double rateConstant, PolymerTypeGroupPtr polyReactant, Unit *unitReactant, PolymerTypeGroupPtr polyProduct1, PolymerTypeGroupPtr polyProduct2)
        : Reaction(CHAINTRANSFER_M, rateConstant, 1, 1, 2, 0)
    {
        polyReactants[0] = polyReactant;
        unitReactants[0] = unitReactant;
        polyProducts[0] = polyProduct1;
        polyProducts[1] = polyProduct2;
    }

    void react()
    {
        // console::debug("Chain transfer to monomer reaction");
        // Terminate the reacting polymer by chain transfer to monomer
        Polymer *polymer = polyReactants[0]->removeRandomPolymer();
        polymer->terminateByChainTransfer();
        polyProducts[0]->insertPolymer(polymer);
        --unitReactants[0]->count;
        
        // Create a new monomer radical
        Polymer *newRadical = new Polymer();
        newRadical->addUnitToEnd((unitReactants[0])->ID);
        polyProducts[1]->insertPolymer(newRadical);
    }

    double calculateRate(double NAV)
    {
        return rateConstant * polyReactants[0]->count * unitReactants[0]->count / NAV;
    }
};

class ThermalInitiationMonomer : public Reaction
{
public:
    ThermalInitiationMonomer(double rateConstant, Unit *unitReactant1, Unit *unitReactant2, Unit *unitReactant3, PolymerTypeGroupPtr polyProduct1, PolymerTypeGroupPtr polyProduct2)
        : Reaction(THERM_INIT_M, rateConstant, 0, 3, 2, 0)
    {
        unitReactants[0] = unitReactant1;
        unitReactants[1] = unitReactant2;
        unitReactants[2] = unitReactant3;
        polyProducts[0] = polyProduct1;
        polyProducts[1] = polyProduct2;
    }

    void react()
    {
        --unitReactants[0]->count = unitReactants[0]->count;
        --unitReactants[1]->count = unitReactants[1]->count;
        --unitReactants[2]->count = unitReactants[2]->count;

        Polymer *polymer1 = new Polymer();
        polymer1->addUnitToEnd((unitReactants[0])->ID);
        polyProducts[0]->insertPolymer(polymer1);

        Polymer *polymer2 = new Polymer();
        polymer2->addUnitToEnd((unitReactants[0])->ID);
        polyProducts[1]->insertPolymer(polymer2);
    }

    double calculateRate(double NAV)
    {
        return rateConstant * pow(unitReactants[0]->count, 3) / NAV;
    }
};

typedef std::unique_ptr<Reaction>
    ReactionPtr;