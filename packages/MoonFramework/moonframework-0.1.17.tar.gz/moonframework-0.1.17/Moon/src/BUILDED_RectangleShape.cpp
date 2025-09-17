// ===============================================================================
// File: BUILDED_SGL_RECTANGLE_SHAPE.cpp
// SFML Rectangle Shape API implementation
// Part of DLL library
//
// Features:
// - Create/delete rectangles
// - Position/size/rotation control
// - Fill/outline color settings
// - Scaling and origin adjustment
// - Get current shape parameters
// ===============================================================================

#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif

typedef sf::RectangleShape* RectanglePtr;

extern "C" {
    __declspec(dllexport) RectanglePtr _Rectangle_Create(float width, float height) {
        return new sf::RectangleShape(sf::Vector2f(width, height));
    }

    __declspec(dllexport) void _Rectangle_SetPosition(RectanglePtr rectangle, float x, float y) {
        rectangle->setPosition(x, y);
    }

    __declspec(dllexport) float _Rectangle_GetPositionX(RectanglePtr rectangle) {
        return rectangle->getPosition().x;
    }

    __declspec(dllexport) float _Rectangle_GetPositionY(RectanglePtr rectangle) {
        return rectangle->getPosition().y;
    }

    __declspec(dllexport) void _Rectangle_SetColor(RectanglePtr rectangle, int r, int g, int b, int alpha) {
        rectangle->setFillColor(sf::Color(r, g, b, alpha));
    }

    __declspec(dllexport) void _Rectangle_SetOrigin(RectanglePtr rectangle, float x, float y) {
        rectangle->setOrigin(x, y);
    }

    __declspec(dllexport) void _Rectangle_SetSize(RectanglePtr rectangle, float width, float height) {
        rectangle->setSize(sf::Vector2f(width, height));
    }

    __declspec(dllexport) void _Rectangle_SetRotation(RectanglePtr rectangle, float angle) {
        rectangle->setRotation(angle);
    }

    __declspec(dllexport) void _Rectangle_SetOutlineThickness(RectanglePtr rectangle, float thickness) {
        rectangle->setOutlineThickness(thickness);
    }

    __declspec(dllexport) void _Rectangle_SetOutlineColor(RectanglePtr rectangle, int r, int g, int b, int alpha) {
        rectangle->setOutlineColor(sf::Color(r, g, b, alpha));
    }

    __declspec(dllexport) void _Rectangle_SetScale(RectanglePtr rectangle, float scaleX, float scaleY) {
        rectangle->setScale(scaleX, scaleY);
    }

    __declspec(dllexport) float _Rectangle_GetWidth(RectanglePtr rectangle) {
        return rectangle->getSize().x;
    }

    __declspec(dllexport) float _Rectangle_GetHeight(RectanglePtr rectangle) {
        return rectangle->getSize().y;
    }

    __declspec(dllexport) void _Rectangle_Delete(RectanglePtr rectangle) {
        delete rectangle;
    }
}
// ===============================================================================
