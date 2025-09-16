#include "SFML/Graphics.hpp"
#include "SFML/Window.hpp"

typedef sf::Clock* ClockPtr;

extern "C" {
    __declspec(dllexport) ClockPtr createClock() {
        return new sf::Clock();
    }

    __declspec(dllexport) void clockRestart(ClockPtr clock) {
        clock->restart();
    }

    __declspec(dllexport) double getClockElapsedTime(ClockPtr clock) {
        return clock->getElapsedTime().asSeconds();
    }
}
