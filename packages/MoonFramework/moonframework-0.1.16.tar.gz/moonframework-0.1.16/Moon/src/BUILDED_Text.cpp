#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif
#ifndef SFML_WINDOW_HPP
#include "SFML/Window.hpp"
#endif
#ifndef SFML_SYSTEM_HPP
#include "SFML/System.hpp"
#endif
#pragma execution_character_set("utf-8")

// BUILTED_SGL_TEXT.cpp =========================================================================

typedef sf::Font* FontPtr;
typedef sf::Text* TextPtr;

extern "C" {
    __declspec(dllexport) FontPtr loadSystemFont(const char* path) {
        FontPtr font = new sf::Font();
        try {
            if (!font->loadFromFile(path)) {
                return nullptr;
            }
        } catch (const std::exception& e) {
            return nullptr;
        }
        font->setSmooth(false);
        return font;
    }

    __declspec(dllexport) TextPtr createText(FontPtr font) {
        TextPtr text = new sf::Text();
        text->setFont(*font);
        return text;
    } 

    __declspec(dllexport) void setText(TextPtr text, const char* str) {
        std::string std_str(str);
        text->setString(sf::String::fromUtf8(std_str.begin(), std_str.end()));
    }

    __declspec(dllexport) void setTextSize(TextPtr text, int size) {
        text->setCharacterSize(size);
    }

    __declspec(dllexport) void setTextScale(TextPtr text, float scaleX, float scaleY) {
        text->setScale(scaleX, scaleY);
    }

    __declspec(dllexport) void setTextColor(TextPtr text, int r, int g, int b, int a) {
        text->setFillColor(sf::Color(r, g, b, a));
    }

    __declspec(dllexport) void setTextPosition(TextPtr text, float x, float y) {
        text->setPosition(x, y);
    }

    __declspec(dllexport) void setTextOfsset(TextPtr text, float x, float y) {
        text->setOrigin(x, y);
    }

    __declspec(dllexport) void setTextAngle(TextPtr text, float angle) {
        text->setRotation(angle);
    }

    __declspec(dllexport) void setStyle(TextPtr text, sf::Text::Style style) {
        text->setStyle(style);
    }

    __declspec(dllexport) void setOutlineColor(TextPtr text, int r, int g, int b, int a) {
        text->setOutlineColor(sf::Color(r, g, b, a));
    }

    __declspec(dllexport) void setOutlineThickness(TextPtr text, float thickness) {
        text->setOutlineThickness(thickness);
    }

    __declspec(dllexport) void setLetterSpacing(TextPtr text, float spacing) {
        text->setLetterSpacing(spacing);
    }

    __declspec(dllexport) double getTextWidth(TextPtr text) {
        return text->getGlobalBounds().width;
    }

    __declspec(dllexport) double getTextHeight(TextPtr text) {
        return text->getGlobalBounds().height;
    }

    __declspec(dllexport) void setFont(TextPtr text, FontPtr font) {
        text->setFont(*font);
    }
}
// BUILTED_SGL_TEXT.cpp =========================================================================
