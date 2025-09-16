// ===============================================================================
// File: BUILDED_SGL_CIRCLE_SHAPE.cpp 
// SFML Circle Shape API implementation
// Part of DLL library
//
// Features:
// - Create/delete circles
// - Position/radius/rotation control  
// - Fill/outline color settings
// - Scaling and origin adjustment
// - Get current shape parameters
// ===============================================================================

#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif

typedef sf::CircleShape* CirclePtr;
// Create/delete circle shape
extern "C" __declspec(dllexport) CirclePtr _Circle_Create(float radius, int point_count) {
    return new sf::CircleShape(radius, point_count);
}

extern "C" __declspec(dllexport) void _Circle_Delete(CirclePtr circle) {
    delete circle;
}

// Position control
extern "C" __declspec(dllexport) void _Circle_SetPosition(CirclePtr circle, float x, float y) {
    circle->setPosition(x, y);
}

extern "C" __declspec(dllexport) float _Circle_GetPositionX(CirclePtr circle) {
    return circle->getPosition().x;
}

extern "C" __declspec(dllexport) float _Circle_GetPositionY(CirclePtr circle) {
    return circle->getPosition().y;
}

// Radius control
extern "C" __declspec(dllexport) void _Circle_SetRadius(CirclePtr circle, float radius) {
    circle->setRadius(radius);
}

extern "C" __declspec(dllexport) float _Circle_GetRadius(CirclePtr circle) {
    return circle->getRadius();
}

// Rotation
extern "C" __declspec(dllexport) void _Circle_SetRotation(CirclePtr circle, float angle) {
    circle->setRotation(angle);
}

extern "C" __declspec(dllexport) float _Circle_GetRotation(CirclePtr circle) {
    return circle->getRotation();
}

// Colors
extern "C" __declspec(dllexport) void _Circle_SetFillColor(CirclePtr circle, int r, int g, int b, int a) {
    circle->setFillColor(sf::Color(r, g, b, a));
}

extern "C" __declspec(dllexport) void _Circle_SetOutlineColor(CirclePtr circle, int r, int g, int b, int a) {
    circle->setOutlineColor(sf::Color(r, g, b, a));
}

extern "C" __declspec(dllexport) void _Circle_SetOutlineThickness(CirclePtr circle, float thickness) {
    circle->setOutlineThickness(thickness);
}

// Scale
extern "C" __declspec(dllexport) void _Circle_SetScale(CirclePtr circle, float scaleX, float scaleY) {
    circle->setScale(scaleX, scaleY);
}

extern "C" __declspec(dllexport) float _Circle_GetScaleX(CirclePtr circle) {
    return circle->getScale().x;
}

extern "C" __declspec(dllexport) float _Circle_GetScaleY(CirclePtr circle) {
    return circle->getScale().y;
}

// Origin
extern "C" __declspec(dllexport) void _Circle_SetOrigin(CirclePtr circle, float x, float y) {
    circle->setOrigin(x, y);
}

extern "C" __declspec(dllexport) float _Circle_GetOriginX(CirclePtr circle) {
    return circle->getOrigin().x;
}

extern "C" __declspec(dllexport) float _Circle_GetOriginY(CirclePtr circle) {
    return circle->getOrigin().y;
}
// ===============================================================================
