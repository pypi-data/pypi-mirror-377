#include <string>
#include <vector>
#include <species/polymer_type.h>

namespace rxn_print
{
    std::vector<std::string> getReactantCountsStrings(std::vector<Unit *> &unitReactants, std::vector<PolymerTypeGroupPtr> &polyReactants)
    {
        std::vector<std::string> reactantCountsStrings;
        for (const auto &polyReactant : polyReactants)
            reactantCountsStrings.push_back(polyReactant->name + " (" + std::to_string(polyReactant->count) + ")");
        for (const auto &unitReactant : unitReactants)
            reactantCountsStrings.push_back(unitReactant->name + " (" + std::to_string(unitReactant->count) + ")");
        return reactantCountsStrings;
    }

    std::vector<std::string> getProductCountsStrings(std::vector<Unit *> &unitProducts, std::vector<PolymerTypeGroupPtr> &polyProducts)
    {
        std::vector<std::string> productCountsStrings;
        for (const auto &polyProduct : polyProducts)
            productCountsStrings.push_back(polyProduct->name + " (" + std::to_string(polyProduct->count) + ")");
        for (const auto &unitProduct : unitProducts)
            productCountsStrings.push_back(unitProduct->name + " (" + std::to_string(unitProduct->count) + ")");
        return productCountsStrings;
    }

    std::string reactionToString(
        std::vector<Unit *> &unitReactants,
        std::vector<PolymerTypeGroupPtr> &polyReactants,
        std::vector<Unit *> &unitProducts,
        std::vector<PolymerTypeGroupPtr> &polyProducts)
    {
        std::vector<std::string> reactantCountStrings = getReactantCountsStrings(unitReactants, polyReactants);
        std::vector<std::string> productCountStrings = getProductCountsStrings(unitProducts, polyProducts);

        std::string reactionString = "";
        for (size_t i = 0; i < reactantCountStrings.size() - 1; ++i)
            reactionString += reactantCountStrings[i] + " + ";
        reactionString += reactantCountStrings[reactantCountStrings.size() - 1];
        reactionString += " -> ";
        for (size_t i = 0; i < productCountStrings.size() - 1; ++i)
            reactionString += productCountStrings[i] + "  + ";
        reactionString += productCountStrings[productCountStrings.size() - 1];
        return reactionString;
    }

    /**
     * @brief Returns the string representation of a reaction with the current counts.
     *
     * @return std::string
     */
    std::string reactionCountsToString(
        std::vector<Unit *> &unitReactants,
        std::vector<PolymerTypeGroupPtr> &polyReactants,
        std::vector<Unit *> &unitProducts,
        std::vector<PolymerTypeGroupPtr> &polyProducts)
    {

        uint16_t DEFAULT_STRING_SIZE = 10;
        std::string outputString;

        std::vector<std::string> reactantStrings;
        std::vector<std::string> productStrings;

        // First pass through all reactants and products
        //
        for (size_t i = 0; i < unitReactants.size(); ++i)
        {
            std::string reactantString = unitReactants[i]->name + " (" + std::to_string(unitReactants[i]->count) + ")";
            reactantStrings.push_back(reactantString);
        }
        for (size_t i = 0; i < polyProducts.size(); ++i)
        {
            std::string productString = polyProducts[i]->name + " (" + std::to_string(polyProducts[i]->count) + ")";
            productStrings.push_back(productString);
        }
        for (size_t i = 0; i < unitProducts.size(); ++i)
        {
            std::string productString = unitProducts[i]->name + " (" + std::to_string(unitProducts[i]->count) + ")";
            productStrings.push_back(productString);
        }

        // Loop through reactant and product strings to find the maximum string size
        size_t maximumStringSize = 10; // default string size
        for (const std::string &reactionString : reactantStrings)
            if (reactionString.size() > maximumStringSize)
                maximumStringSize = reactionString.size();
        for (const std::string &productString : productStrings)
            if (productString.size() > maximumStringSize)
                maximumStringSize = productString.size();

        // Loop through reactant and product strings to pad and print them

        std::string reactants = "";

        if (polyReactants.size() > 0) // if there are poly reactants
        {
            outputString = std::to_string(polyReactants[0]->count) + ")";
            reactants += polyReactants[0]->name + " (" + std::to_string(polyReactants[0]->count) + ")";
            for (size_t i = 1; i < polyReactants.size(); ++i)
                reactants += " + " + polyReactants[i]->name + " (" + std::to_string(polyReactants[i]->count) + ")";
            if (unitReactants.size() > 0)
                reactants += " + ";
        }

        if (unitReactants.size() > 0)
        {
            reactants += unitReactants[0]->name + " (" + std::to_string(unitReactants[0]->count) + ")";
            for (size_t i = 1; i < unitReactants.size(); ++i)
                reactants += " + " + unitReactants[i]->name + " (" + std::to_string(unitReactants[i]->count) + ")";
        }

        for (int i = 0; i < int(polyReactants.size()) - 1; ++i)
            reactants += polyReactants[i]->name + "(" + std::to_string(polyReactants[i]->count) + ") + ";
        if (polyReactants.size() > 0)
            reactants += polyReactants[polyReactants.size() - 1]->name + "(" + std::to_string(polyReactants[polyReactants.size() - 1]->count) + ")";
        if (!reactants.empty() && !unitReactants.empty())
            reactants += " + ";
        for (int i = 0; i < int(unitReactants.size()) - 1; ++i)
            reactants += unitReactants[i]->name + "(" + std::to_string(unitReactants[i]->count) + ") + ";
        if (unitReactants.size() > 0)
            reactants += unitReactants[unitReactants.size() - 1]->name + "(" + std::to_string(unitReactants[unitReactants.size() - 1]->count) + ")";
        reactants += " -> ";

        std::string products = "";
        for (int i = 0; i < int(polyProducts.size()) - 1; ++i)
            products += polyProducts[i]->name + "(" + std::to_string(polyProducts[i]->count) + ") + ";
        if (polyProducts.size() > 0)
            products += polyProducts[polyProducts.size() - 1]->name + "(" + std::to_string(polyProducts[polyProducts.size() - 1]->count) + ")";
        if (!products.empty() && !unitProducts.empty())
            products += " + ";
        for (int i = 0; i < int(unitProducts.size()) - 1; ++i)
            products += unitProducts[i]->name + "(" + std::to_string(unitProducts[i]->count) + ") + ";
        if (unitProducts.size() > 0)
            products += unitProducts[unitProducts.size() - 1]->name + "(" + std::to_string(unitProducts[unitProducts.size() - 1]->count) + ")";
        ;

        return reactants + products;
    }
}
