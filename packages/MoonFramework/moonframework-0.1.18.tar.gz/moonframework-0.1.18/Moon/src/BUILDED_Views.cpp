#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif


extern "C" {
    typedef sf::FloatRect* FloatRectPtr;

    __declspec(dllexport) FloatRectPtr _FloatRect_Create(float rect_left, float rect_top, float rect_width, float rect_height) {
        return new sf::FloatRect(rect_left, rect_top, rect_width, rect_height);
    }

    __declspec(dllexport) void _FloatRect_Delete(FloatRectPtr rect) {
        delete rect;
    }

    __declspec(dllexport) float _FloatRect_GetPositionX(FloatRectPtr rect) {
        return rect->getPosition().x;
    }

    __declspec(dllexport) float _FloatRect_GetPositionY(FloatRectPtr rect) {
        return rect->getPosition().y;
    }

    __declspec(dllexport) float _FloatRect_GetWidth(FloatRectPtr rect) {
        return rect->getSize().x;
    }

    __declspec(dllexport) float _FloatRect_GetHeight(FloatRectPtr rect) {
        return rect->getSize().y;
    }

    __declspec(dllexport) void _FloatRect_SetPosition(FloatRectPtr rect, float x, float y) {
        rect->left = x;
        rect->top = y;
    }

    __declspec(dllexport) void _FloatRect_SetSize(FloatRectPtr rect, float w, float h) {
        rect->width = w;
        rect->height = h;
    }

}

extern "C" {
    typedef sf::View* ViewPtr;

    __declspec(dllexport) ViewPtr _View_Create(FloatRectPtr rect) {
        ViewPtr view = new sf::View(*rect);
        return view;
    }

    __declspec(dllexport) void _View_Delete(ViewPtr view) {
        delete view;
    }

    __declspec(dllexport) float _View_GetPositionX(ViewPtr view) {
        return view->getViewport().left;
    }

    __declspec(dllexport) float _View_GetPositionY(ViewPtr view) {
        return view->getViewport().top;
    }

    __declspec(dllexport) float _View_GetCenterX(ViewPtr view) {
        return view->getCenter().x;
    }

    __declspec(dllexport) float _View_GetCenterY(ViewPtr view) {
        return view->getCenter().y;
    }

    __declspec(dllexport) float _View_GetAngle(ViewPtr view) {
        return view->getRotation();
    }

    __declspec(dllexport) float _View_GetWidth(ViewPtr view) {
        return view->getSize().x;
    }

    __declspec(dllexport) float _View_GetHeight(ViewPtr view) {
        return view->getSize().y;
    }

    __declspec(dllexport) void _View_Rotate(ViewPtr view, float angle) {
        view->rotate(angle);
    }

    __declspec(dllexport) void _View_Reset(ViewPtr view, FloatRectPtr rect) {
        view->reset(*rect);
    }

    __declspec(dllexport) void _View_Move(ViewPtr view, float x, float y) {
        view->move(x, y);
    }

    __declspec(dllexport) void _View_SetCenter(ViewPtr view, float x, float y) {
        view->setCenter(x, y);
    }

    __declspec(dllexport) void _View_SetAngle(ViewPtr view, float angle) {
        view->setRotation(angle);
    } 

    __declspec(dllexport) void _View_SetViewport(ViewPtr view, FloatRectPtr rect) {
        view->setViewport(*rect);
    } 

    __declspec(dllexport) void _View_SetSize(ViewPtr view, float w, float h) {
        view->setSize(w, h);
    } 

    __declspec(dllexport) void _View_Zoom(ViewPtr view, float zoom) {
        view->zoom(zoom);
    }
}
