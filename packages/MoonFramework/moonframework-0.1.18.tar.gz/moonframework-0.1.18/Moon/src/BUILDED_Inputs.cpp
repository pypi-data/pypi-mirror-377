#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif
#ifndef SFML_WINDOW_HPP
#include "SFML/Window.hpp"
#endif

// BUILTED_SGL_INPUTS.cpp =========================================================================
extern "C" {
    __declspec(dllexport) bool IsKeyPressed(int key) {
        return sf::Keyboard::isKeyPressed(static_cast<sf::Keyboard::Key>(key));
    }
}

extern "C" {
    __declspec(dllexport) bool IsMouseButtonPressed(int button) {
        return sf::Mouse::isButtonPressed(static_cast<sf::Mouse::Button>(button));
    }

    __declspec(dllexport) int GetMousePositionX() {
        return sf::Mouse::getPosition().x;
    }

    __declspec(dllexport) int GetMousePositionY() {
        return sf::Mouse::getPosition().y;
    }

    __declspec(dllexport) int GetMousePositionXWindow(sf::RenderWindow* window) {
        return sf::Mouse::getPosition(*window).x;
    }

    __declspec(dllexport) int GetMousePositionYWindow(sf::RenderWindow* window) {
        return sf::Mouse::getPosition(*window).y;
    }

    
}
// BUILDED_SGL_INPUTS.cpp =========================================================================
