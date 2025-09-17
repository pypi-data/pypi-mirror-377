#pragma once

enum ReactorType
{
    BATCH = 0,
    SEMIBATCH,
    CONTINOUS
};

/**
 * @brief This class does nothing at the moment but I am planning to use it
 * when I get to semi-batch functionality.
 * 
 */
class Reactor
{
public:
    Reactor(ReactorType reactorType, double T=0, double P=0) : 
        type(reactorType), temperature(T), pressure(P) 
        {

        }

private:
    ReactorType type;
    double temperature; // Kelvin
    double pressure;    // bar
    double volume;      // L
    double NAV;
};