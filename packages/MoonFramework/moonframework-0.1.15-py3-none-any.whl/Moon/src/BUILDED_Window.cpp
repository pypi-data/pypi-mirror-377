// ================================================================================
//                           BUILDED_SGL_WINDOW.cpp
//                    Биндинги для работы с окнами в PySGL
// ================================================================================
//
// Этот файл содержит C++ функции для работы с окнами SFML,
// которые экспортируются в Python через ctypes.
//
// Основные компоненты:
// - Управление окнами (создание, настройка, отрисовка)
// - Обработка событий (клавиатура, мышь, изменение размера)
// - Работа с видами (View) и координатными системами
// - Настройки контекста OpenGL
// - Утилиты для работы со временем
//
// ================================================================================

#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif
#ifndef SFML_WINDOW_HPP
#include "SFML/Window.hpp"
#endif

// ================================================================================
//                              ОПРЕДЕЛЕНИЯ ТИПОВ
// ================================================================================

typedef sf::RenderWindow* WindowPtr;        // Указатель на окно рендеринга
typedef sf::Event* EventPtr;                // Указатель на событие
typedef sf::View* ViewPtr;                  // Указатель на вид (камеру)


// ================================================================================
//                        НАСТРОЙКИ КОНТЕКСТА OPENGL
// ================================================================================
// Функции для управления настройками OpenGL контекста:
// - Антиалиасинг (сглаживание)
// - Буферы глубины и трафарета
// - Версия OpenGL
// - sRGB поддержка
// ================================================================================

extern "C" {
    typedef sf::ContextSettings* ContextSettingsPtr;

    // Создание нового объекта настроек контекста
    __declspec(dllexport) ContextSettingsPtr _WindowContextSettings_Create() {
        return new sf::ContextSettings();
    }

    // Установка флагов атрибутов контекста
    __declspec(dllexport) void _WindowContextSettings_SetAttributeFlags(ContextSettingsPtr contextSettings, int flags) {
        contextSettings->attributeFlags = flags;
    }

    // Установка уровня антиалиасинга (0, 2, 4, 8, 16)
    __declspec(dllexport) void _WindowContextSettings_SetAntialiasingLevel(ContextSettingsPtr contextSettings, int level) {
        contextSettings->antialiasingLevel = level;
    }

    // Установка количества бит для буфера глубины
    __declspec(dllexport) void _WindowContextSettings_SetDepthBits(ContextSettingsPtr contextSettings, int bits) {
        contextSettings->depthBits = bits;
    }

    // Установка основной версии OpenGL
    __declspec(dllexport) void _WindowContextSettings_SetMajorVersion(ContextSettingsPtr contextSettings, int version) {
        contextSettings->majorVersion = version;
    }

    // Установка дополнительной версии OpenGL
    __declspec(dllexport) void _WindowContextSettings_SetMinorVersion(ContextSettingsPtr contextSettings, int version) {
        contextSettings->minorVersion = version;
    }

    // Установка количества бит для буфера трафарета
    __declspec(dllexport) void _WindowContextSettings_SetStencilBits(ContextSettingsPtr contextSettings, int bits) {
        contextSettings->stencilBits = bits;
    }

    // Включение/выключение поддержки sRGB цветового пространства
    __declspec(dllexport) void _WindowContextSettings_SetSrgbCapable(ContextSettingsPtr contextSettings, bool capable) {
        contextSettings->sRgbCapable = capable;
    }

    // Удаление объекта настроек контекста
    __declspec(dllexport) void _WindowContextSettings_Delete(ContextSettingsPtr contextSettings) {
        delete contextSettings;
    }
}

// ================================================================================
//                           УПРАВЛЕНИЕ ОКНОМ
// ================================================================================
// Основные функции для работы с окнами:
// - Создание и удаление окон
// - Настройка свойств (заголовок, размер, позиция)
// - Отрисовка и очистка
// - Проверка состояния
// ================================================================================

extern "C" {
    // Создание нового окна с указанными параметрами
    __declspec(dllexport) WindowPtr _Window_Create(const int width, const int height, 
        const char* title, int style, ContextSettingsPtr settings) {
        return new sf::RenderWindow(sf::VideoMode(width, height), title, style, *settings);
    }

    // Закрытие окна (окно становится недоступным для взаимодействия)
    __declspec(dllexport) void _Window_Close(WindowPtr window) {
        window->close();
    }

    // Управление видимостью курсора мыши
    __declspec(dllexport) void _Window_SetCursorVisibility(WindowPtr window, bool value) {
        window->setMouseCursorVisible(value);
    }

    // Установка заголовка окна
    __declspec(dllexport) void _Window_SetTitle(WindowPtr window, const char* title) {
        window->setTitle(title);
    }

    // Включение/выключение вертикальной синхронизации
    __declspec(dllexport) void _Window_SetVsync(WindowPtr window, bool enable) {
        window->setVerticalSyncEnabled(enable);
    }

    // Установка системного курсора для окна
    __declspec(dllexport) void _Window_SetSystemCursor(WindowPtr window, sf::Cursor::Type cursor) {
        sf::Cursor c = sf::Cursor();
        c.loadFromSystem(cursor);
        window->setMouseCursor(c);
    }

    // Проверка, открыто ли окно и доступно ли для взаимодействия
    __declspec(dllexport) bool _Window_IsOpen(WindowPtr window) {
        return window->isOpen();
    }

    // Полное удаление окна и освобождение памяти
    __declspec(dllexport) void _Window_Delete(WindowPtr window) {
        window->close();
        delete window;
    }

    __declspec(dllexport) bool _Window_SetIconFromPath(WindowPtr window, const char* path) {
        sf::Image image;
        if (!image.loadFromFile(path)) {
            return false;
        }
        window->setIcon(image.getSize().x, image.getSize().y, image.getPixelsPtr());
        return true;
    }

    // ================================================================================
    //                    ПОЛУЧЕНИЕ РАЗМЕРА ОКНА
    // ================================================================================
    
    // Получение ширины окна в пикселях
    __declspec(dllexport) int _Window_GetSizeWidth(WindowPtr window) {
        return window->getSize().x;
    }
    
    // Получение высоты окна в пикселях
    __declspec(dllexport) int _Window_GetSizeHeight(WindowPtr window) {
        return window->getSize().y;
    }

    // ================================================================================
    //                    ПОЛУЧЕНИЕ ПОЗИЦИИ ОКНА
    // ================================================================================
    
    // Получение X-координаты окна на экране
    __declspec(dllexport) int _Window_GetPositionX(WindowPtr window) {
        return window->getPosition().x;
    }
    
    // Получение Y-координаты окна на экране
    __declspec(dllexport) int _Window_GetPositionY(WindowPtr window) {
        return window->getPosition().y;
    }

    // ================================================================================
    //              УСТАНОВКА ПОЗИЦИИ И РАЗМЕРА ОКНА
    // ================================================================================
    
    // Установка позиции окна на экране
    __declspec(dllexport) void _Window_SetPosition(WindowPtr window, int x, int y) {
        window->setPosition(sf::Vector2i(x, y));
    }

    // Установка размера окна
    __declspec(dllexport) void _Window_SetSize(WindowPtr window, int width, int height) {
        window->setSize(sf::Vector2u(width, height));
    }

    // ================================================================================
    //                  ПРЕОБРАЗОВАНИЕ КООРДИНАТ
    // ================================================================================
    // Преобразование между экранными пикселями и мировыми координатами
    
    // Преобразование пикселей в мировые координаты (X)
    __declspec(dllexport) float _Window_MapPixelToCoordsX(WindowPtr window, double x, double y, ViewPtr view) {
        return window->mapPixelToCoords(sf::Vector2i(x,  y), *view).x;
    }

    // Преобразование пикселей в мировые координаты (Y)
    __declspec(dllexport) float _Window_MapPixelToCoordsY(WindowPtr window, double x, double y, ViewPtr view) {
        return window->mapPixelToCoords(sf::Vector2i(x,  y), *view).y;
    }

    // Преобразование мировых координат в пиксели (X)
    __declspec(dllexport) float _Window_MapCoordsToPixelX(WindowPtr window, double x, double y, ViewPtr view) {
        return window->mapCoordsToPixel(sf::Vector2f(x, y), *view).x;
    }

    // Преобразование мировых координат в пиксели (Y)
    __declspec(dllexport) float _Window_MapCoordsToPixelY(WindowPtr window, double x, double y, ViewPtr view) {
        return window->mapCoordsToPixel(sf::Vector2f(x, y), *view).y;
    }

    // ================================================================================
    //                            РЕНДЕРИНГ
    // ================================================================================
    // Основные функции для отрисовки графики
    
    // Очистка окна указанным цветом
    __declspec(dllexport) void _Window_Clear(WindowPtr window, int r, int g, int b, int a) {
        window->clear(sf::Color(r, g, b, a));
    }

    // Отображение всех нарисованных объектов на экране
    __declspec(dllexport) void _Window_Display(WindowPtr window) {
        window->display();
    }

    // Отрисовка объекта с настройками по умолчанию
    __declspec(dllexport) void _Window_Draw(WindowPtr window, sf::Drawable* drawable) {
        window->draw(*drawable);
    }

    // Отрисовка объекта с пользовательскими настройками рендеринга
    __declspec(dllexport) void _Window_DrawWithRenderStates(WindowPtr window, sf::RenderStates* render_states, sf::Drawable* drawable)  {
        window->draw(*drawable, *render_states);
    }

    // Отрисовка объекта с применением шейдера
    __declspec(dllexport) void _Window_DrawWithShader(WindowPtr window, sf::Shader* shader, sf::Drawable* drawable) {
        window->draw(*drawable, shader);
    }

    // ================================================================================
    //                      УПРАВЛЕНИЕ ВИДОМ (VIEW/КАМЕРОЙ)
    // ================================================================================
    // Функции для управления камерой и областью просмотра
    
    // Применение вида к окну (установка активной камеры)
    __declspec(dllexport) void _Window_SetView(WindowPtr window, ViewPtr view) {
        window->setView(*view);
    }

    // Получение стандартного вида (камеры) окна
    __declspec(dllexport) ViewPtr _Window_GetDefaultView(WindowPtr window) {
        return new sf::View(window->getDefaultView());
    }

    // ================================================================================
    //                      НАСТРОЙКИ ПРОИЗВОДИТЕЛЬНОСТИ
    // ================================================================================
    
    // Установка ограничения кадров в секунду (FPS)
    __declspec(dllexport) void _Window_SetWaitFps(WindowPtr window, unsigned int fps) {
        window->setFramerateLimit(fps);
    }

    // ================================================================================
    //                        ОБРАБОТКА СОБЫТИЙ
    // ================================================================================
    // Функции для работы с событиями окна (клавиатура, мышь, изменение размера)
    
    // Получение следующего события из очереди
    __declspec(dllexport) int _Window_GetCurrentEventType(WindowPtr window, sf::Event* event) {
        if (window->pollEvent(*event)) {
            return event->type;
        }
        return -1;  // Нет событий в очереди
    }

}

// ================================================================================
//                              КОНЕЦ ФАЙЛА
// ================================================================================
// Все функции для работы с окнами PySGL определены.
// Они предоставляют полный интерфейс для создания и управления
// графическими окнами в Python приложениях.
// ================================================================================
