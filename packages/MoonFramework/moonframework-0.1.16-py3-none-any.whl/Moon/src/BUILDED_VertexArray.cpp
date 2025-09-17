#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif 

extern "C" {

    typedef sf::VertexArray* VertexArrayPtr;

    __declspec(dllexport) VertexArrayPtr 
    _VertexArray_Create() {
        return new sf::VertexArray();
    }

    __declspec(dllexport) void 
    _VertexArray_Delete(VertexArrayPtr vertexArray) {
        delete vertexArray;
    }

    __declspec(dllexport) void 
    _VertexArray_AddVertexForPositionAndColor(VertexArrayPtr vertexArray, double x, double y, int r, int g, int b, int a) {
        vertexArray->append(sf::Vertex(sf::Vector2f(static_cast<float>(x), static_cast<float>(y)), sf::Color(static_cast<sf::Uint8>(r), static_cast<sf::Uint8>(g), static_cast<sf::Uint8>(b), static_cast<sf::Uint8>(a))));
    }

    __declspec(dllexport) void 
    _VertexArray_SetPrimitiveType(VertexArrayPtr vertexArray, int primitiveType) {
        vertexArray->setPrimitiveType(static_cast<sf::PrimitiveType>(primitiveType));
    }

    __declspec(dllexport) void 
    _VertexArray_Resize(VertexArrayPtr vertexArray, int vertexCount) {
        vertexArray->resize(static_cast<size_t>(vertexCount));
    }

    __declspec(dllexport) void 
    _VertexArray_Clear(VertexArrayPtr vertexArray) {
        vertexArray->clear();
    }

    __declspec(dllexport) int
    _VertexArray_GetVertexCount(VertexArrayPtr vertexArray) {
        return static_cast<int>(vertexArray->getVertexCount());
    }

    __declspec(dllexport) float
    _VertexArray_GetVertexPositionX(VertexArrayPtr vertexArray, int index) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return 0.0f; 
        return vertexArray->operator[](index).position.x;
    }

    __declspec(dllexport) float
    _VertexArray_GetVertexPositionY(VertexArrayPtr vertexArray, int index) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return 0.0f; 
        return vertexArray->operator[](index).position.y;
    }
        
    __declspec(dllexport) int
    _VertexArray_GetVertexColorR(VertexArrayPtr vertexArray, int index) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return 0; 
        return vertexArray->operator[](index).color.r;
    }
    
    __declspec(dllexport) int
    _VertexArray_GetVertexColorG(VertexArrayPtr vertexArray, int index) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return 0; 
        return vertexArray->operator[](index).color.g;
    }

    __declspec(dllexport) int
    _VertexArray_GetVertexColorB(VertexArrayPtr vertexArray, int index) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return 0;
        return vertexArray->operator[](index).color.b;
    }
        
    __declspec(dllexport) int
    _VertexArray_GetVertexColorA(VertexArrayPtr vertexArray, int index) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return 0; 
        return vertexArray->operator[](index).color.a;
    }


    __declspec(dllexport) void
    _VertexArray_SetVertexForPositionAndColor(VertexArrayPtr vertexArray, int index, double x, double y, int r, int g, int b, int a) {
        if (index < 0 || index >= vertexArray->getVertexCount()) return; 
        vertexArray->operator[](index) = sf::Vertex(sf::Vector2f(static_cast<float>(x), static_cast<float>(y)), sf::Color(static_cast<sf::Uint8>(r), static_cast<sf::Uint8>(g), static_cast<sf::Uint8>(b), static_cast<sf::Uint8>(a)));
    }

    __declspec(dllexport) int 
    _VertexArray_GetPrimitiveType(VertexArrayPtr vertexArray) {
        return static_cast<int>(vertexArray->getPrimitiveType());
    }

    // Оптимизированные функции для прямого доступа
    __declspec(dllexport) void
    _VertexArray_SetVertexPosition(VertexArrayPtr vertexArray, int index, float x, float y) {
        if (index >= 0 && index < vertexArray->getVertexCount()) {
            (*vertexArray)[index].position = sf::Vector2f(x, y);
        }
    }


    __declspec(dllexport) void
    _VertexArray_SetVertexColor(VertexArrayPtr vertexArray, int index, int r, int g, int b, int a) {
        if (index >= 0 && index < vertexArray->getVertexCount()) {
            (*vertexArray)[index].color = sf::Color(r, g, b, a);
        }
    }

    __declspec(dllexport) void
    _VertexArray_SetAllVerticesColor(VertexArrayPtr vertexArray, int r, int g, int b, int a) {
        sf::Color color(r, g, b, a);
        for (size_t i = 0; i < vertexArray->getVertexCount(); ++i) {
            (*vertexArray)[i].color = color;
        }
    }

    // Функции для работы с текстурными координатами
    __declspec(dllexport) void
    _VertexArray_AddVertexWithTexCoords(VertexArrayPtr vertexArray, float x, float y, int r, int g, int b, int a, float texX, float texY) {
        vertexArray->append(sf::Vertex(
            sf::Vector2f(x, y),
            sf::Color(r, g, b, a),
            sf::Vector2f(texX, texY)
        ));
    }

    __declspec(dllexport) void
    _VertexArray_SetVertexTexCoords(VertexArrayPtr vertexArray, int index, float texX, float texY) {
        if (index >= 0 && index < vertexArray->getVertexCount()) {
            (*vertexArray)[index].texCoords = sf::Vector2f(texX, texY);
        }
    }

    __declspec(dllexport) void
    _VertexArray_SetQuadTexCoords(VertexArrayPtr vertexArray, int startIndex, float left, float top, float width, float height) {
        if (startIndex >= 0 && startIndex + 3 < vertexArray->getVertexCount()) {
            (*vertexArray)[startIndex].texCoords = sf::Vector2f(left, top);
            (*vertexArray)[startIndex + 1].texCoords = sf::Vector2f(left + width, top);
            (*vertexArray)[startIndex + 2].texCoords = sf::Vector2f(left + width, top + height);
            (*vertexArray)[startIndex + 3].texCoords = sf::Vector2f(left, top + height);
        }
    }

    // Специальная функция для отрисовки VertexArray с RenderStates
    __declspec(dllexport) void _Window_DrawVertexArrayWithRenderStates(sf::RenderWindow* window, sf::RenderStates* render_states, VertexArrayPtr vertexArray) {
        window->draw(*vertexArray, *render_states);
    }
}
