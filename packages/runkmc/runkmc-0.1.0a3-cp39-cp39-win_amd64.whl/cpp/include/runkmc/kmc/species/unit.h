#pragma once

typedef uint8_t unitID;

/**
 * Minimal unit class for KMC simulation.
 * Can include any molecule/non-distributed species.
 * Example: initiator, monomer, dyads, etc.
 */
class Unit
{
public:
	std::string type;
	std::string name;
	unitID ID;

	double C0;
	uint16_t FW;
	double efficiency; // for initiators

	uint64_t count_0;
	uint64_t count;

	Unit(const std::string type_, std::string name_, unitID ID_, double C0_, uint16_t FW_, double efficiency_ = 1.0)
		: type(type_), name(name_), ID(ID_), C0(C0_), FW(FW_), efficiency(efficiency_) {}

	void setInitialCount(uint64_t initialCount)
	{
		count_0 = initialCount;
		count = count_0;
	}

	uint64_t getInitialCount() const
	{
		return count_0;
	};

	double calculateConversion() const
	{
		double initialCount = double(getInitialCount());
		if (initialCount == 0)
			return 0;
		return (initialCount - count) / initialCount;
	}

	std::string toString() const
	{
		return name + " (" + std::to_string(ID) + "): " + std::to_string(count) + " / " + std::to_string(getInitialCount());
	}
};

typedef Unit *UnitPtr;
