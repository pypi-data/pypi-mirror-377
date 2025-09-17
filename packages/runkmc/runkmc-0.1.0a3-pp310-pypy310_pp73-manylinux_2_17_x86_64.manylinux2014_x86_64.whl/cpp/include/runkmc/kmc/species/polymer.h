#pragma once
#include "common.h"
#include "analysis/analysis.h"

enum PolymerState
{
	UNINITIATED,
	ALIVE,
	TERMINATED_D,
	TERMINATED_C,
	TERMINATED_CT,
};

class Polymer
{
private:
	PolymerState state;
	std::vector<analysis::SequenceStats> posStats;
	std::vector<unitID> sequence;
	unitID initiator;

public:
	Polymer(uint32_t maxDOP = 1000)
	{
		sequence.reserve(maxDOP);
		state = ALIVE;
		posStats.reserve(species::NUM_BUCKETS);
	};

	~Polymer() = default;

	/***************** State functions *****************/
	bool isUninitiated() { return state == PolymerState::UNINITIATED; }
	bool isAlive() { return state == PolymerState::ALIVE; }
	void updateState(PolymerState ps) { state = ps; }

	/***************** Modify functions ****************/

	void addUnitToEnd(const unitID unit)
	{
		sequence.push_back(unit);
	}

	void removeUnitFromEnd()
	{
		if (sequence.empty())
			console::error("Trying to remove unit from empty polymer.");
		if (getDegreeOfPolymerization() <= 1)
			console::error("Trying to remove last unit from polymer.");

		sequence.pop_back();
	}

	/***************** State functions *****************/
	size_t getDegreeOfPolymerization() { return sequence.size(); }

	bool endGroupIs(const std::vector<unitID> &endGroup)
	{
		if (!isAlive() || endGroup.size() > getDegreeOfPolymerization() + 1)
			return false;
		return equal(sequence.end() - endGroup.size(), sequence.end(), endGroup.begin());
	}

	unitID repeatUnitAtPosition(const uint32_t posIndex)
	{
		if (posIndex > getDegreeOfPolymerization())
			return 0;
		return sequence[posIndex];
	}

	// void setSequenceStats(analysis::SequenceStats stats_) { stats = stats_; }

	std::vector<unitID> &getSequence() { return sequence; }

	std::string getSequenceString()
	{
		std::string sequenceString;
		for (auto id : sequence)
		{
			sequenceString += std::to_string(id) + " ";
		}
		return sequenceString;
	}

	std::vector<analysis::SequenceStats> &getPositionalStats() { return posStats; }

	PolymerState getState() { return state; }

	void clearSequence()
	{
		sequence.clear();
		std::vector<unitID>().swap(sequence);
	}

	/***************** Reaction functions *****************/

	void terminate()
	{
		posStats = analysis::calculatePositionalSequenceStats(sequence, species::NUM_BUCKETS);
		clearSequence();
	}

	bool isCompressed()
	{
		if (sequence.empty() && !posStats.empty())
			return true;
		return false;
	}

	void terminateByChainTransfer()
	{
		state = PolymerState::TERMINATED_CT;
		terminate();
	}

	void terminateByDisproportionation()
	{
		state = PolymerState::TERMINATED_D;
		terminate();
	}

	void terminateByCombination(Polymer *&polymer)
	{
		sequence.insert(sequence.end(), polymer->sequence.rbegin(), polymer->sequence.rend());
		state = PolymerState::TERMINATED_C;
		terminate();
	}
};
