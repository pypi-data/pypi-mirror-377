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
#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif
#ifndef STRING_H
#include "string"
#endif
#ifndef IOSTREAM_H
#include "iostream"
#endif

using std::endl, std::cout;

using std::string;


extern "C" {
    typedef sf::BlendMode* BlendModePtr;

    __declspec(dllexport) BlendModePtr _BlendMode_CreateFull(
                                                sf::BlendMode::Factor ColorSourceFactor, 
                                                sf::BlendMode::Factor ColorDestinationFactor,
                                                sf::BlendMode::Equation ColorBlendEquation,
                                                sf::BlendMode::Factor AlphaSourceFactor, 
                                                sf::BlendMode::Factor AlphaDestinationFactor,
                                                sf::BlendMode::Equation AlphaBlendEquation
                                            ) {
        return new sf::BlendMode(ColorSourceFactor, ColorDestinationFactor, ColorBlendEquation, 
                                 AlphaSourceFactor, AlphaDestinationFactor, AlphaBlendEquation);
    }

    __declspec(dllexport) void _BlendMode_Delete(BlendModePtr blend_mode) {
        delete blend_mode;
    }
}

extern "C" {
    typedef sf::RenderStates* RenderStatesPtr;

    __declspec(dllexport) RenderStatesPtr _RenderStates_Create() {
        RenderStatesPtr render_states = new sf::RenderStates();
        return render_states;
    }

    __declspec(dllexport) void _RenderStates_Delete(RenderStatesPtr render_states) {
        delete render_states;
    }

    __declspec(dllexport) void _RenderStates_SetShader(RenderStatesPtr render_states, sf::Shader* shader) {
        render_states->shader = shader;
    }

    __declspec(dllexport) void _RenderStates_SetBlendMode(RenderStatesPtr render_states, BlendModePtr blend_mode) {
        render_states->blendMode = *blend_mode;
    }

    __declspec(dllexport) void _RenderStates_SetTexture(RenderStatesPtr render_states, sf::Texture *texture) {
        render_states->texture = texture;
    }

    __declspec(dllexport) void _RenderStates_SetTransform(RenderStatesPtr render_states, sf::Transform* transform) {
        render_states->transform = *transform;
    }
}

extern "C" {
    typedef sf::Shader* ShaderPtr;

    __declspec(dllexport) ShaderPtr
    _Shader_Create() {
        return new sf::Shader();
    }

    __declspec(dllexport) bool
    _Shader_LoadFromFile(ShaderPtr shader, char* vertex_file, char* fragment_file) {
        return shader->loadFromFile(vertex_file, fragment_file);
    }

    __declspec(dllexport) bool
    _Shader_LoadFromStrings(ShaderPtr shader, char* vertex_string, char* fragment_string) {
        return shader->loadFromMemory(vertex_string, fragment_string);
    }

    __declspec(dllexport) bool
    _Shader_LoadFromStringWithType(ShaderPtr shader, char* shader_string, sf::Shader::Type type) {
        if (type == 2) {
            return shader->loadFromMemory(shader_string, sf::Shader::Fragment);
        } else if (type == 1) {
            return shader->loadFromMemory(shader_string, sf::Shader::Geometry);
        } else if (type == 0) {
            return shader->loadFromMemory(shader_string, sf::Shader::Vertex);
        }
    }

    //////////////////////////////////////////////////////////////////////
    // Uniforms
    //////////////////////////////////////////////////////////////////////

    __declspec(dllexport) void
    _Shader_SetUniformInt(ShaderPtr shader, char* name, int value) {
        shader->setUniform(name, value);
    }

    __declspec(dllexport) void
    _Shader_SetUniformFloat(ShaderPtr shader, char* name, float value) {
        shader->setUniform(name, value);
    }

    __declspec(dllexport) void
    _Shader_SetUniformBool(ShaderPtr shader, char* name, bool value) {
        shader->setUniform(name, value); 
    }

    __declspec(dllexport) void
    _Shader_SetUniformTexture(ShaderPtr shader, char* name, sf::Texture texture) {
        shader->setUniform(name, texture);
    }

    __declspec(dllexport) void
    _Shader_SetUniformIntVector(ShaderPtr shader, char* name, int x, int y) {
        shader->setUniform(name, sf::Glsl::Ivec2(x, y));
    }

    __declspec(dllexport) void
    _Shader_SetUniformFloatVector(ShaderPtr shader, char* name, float x, float y) {
        shader->setUniform(name, sf::Glsl::Vec2(x, y));
    }

    __declspec(dllexport) void
    _Shader_SetUniformColor(ShaderPtr shader, char* name, int r, int g, int b, int a) {
        shader->setUniform(name, sf::Glsl::Vec4(r/256.0f, g/256.0f, b/256.0f, a/256.0f));
    }

    //////////////////////////////////////////////////////////////////////
    // Uniforms
    //////////////////////////////////////////////////////////////////////

    __declspec(dllexport) void
    _Shader_Bind(ShaderPtr shader, ShaderPtr new_shader) {
        shader->bind(new_shader);
    }

    __declspec(dllexport) void
    _Shader_Unbind(ShaderPtr shader) {
        shader->bind(NULL);
    }

    __declspec(dllexport) void* _Shader_GetCurrentTexture() {
        return &sf::Shader::CurrentTexture;
    }
}
#ifndef SFML_AUDIO_HPP
#include "SFML/Audio.hpp"
#endif
#ifndef IOSTREAM_H
#include <iostream>
#endif

using std::cout, std::endl;
extern "C" {
    typedef sf::SoundBuffer* SoundBufferPtr;

    __declspec(dllexport) SoundBufferPtr _SoundBuffer_loadFromFile(const char* path) {
        SoundBufferPtr buffer = new sf::SoundBuffer();

        if (buffer->loadFromFile(path))
            cout << "Sound: " << path << " loaded." << endl;
        else {
            cout << "Sound: " << path << "error loading sound" << endl;
        }
        return buffer;
    }

    __declspec(dllexport) void _SoundBuffer_Destroy(SoundBufferPtr buffer) {
        delete buffer;
    }

    __declspec(dllexport) int _SoundBuffer_GetChannelsCount(SoundBufferPtr buffer) {
        return buffer->getChannelCount();
    }

    __declspec(dllexport) int _SoundBuffer_GetSampleRate(SoundBufferPtr buffer) {
        return buffer->getSampleRate();
    }
}

extern "C" {
    typedef sf::Sound* SoundPtr;

    __declspec(dllexport) SoundPtr _Sound_Create(SoundBufferPtr buffer) {
        SoundPtr sound = new sf::Sound();
        sound->setBuffer(*buffer);
        return sound;
    }

    __declspec(dllexport) void _Sound_Destroy(SoundPtr sound) {
        delete sound;
    }

    __declspec(dllexport) void _Sound_Play(SoundPtr sound) {
        sound->play();
    }

    __declspec(dllexport) void _Sound_Pause(SoundPtr sound) {
        sound->pause();
    }

    __declspec(dllexport) void _Sound_Stop(SoundPtr sound) {
        sound->stop();
    }

    __declspec(dllexport) void _Sound_SetLoop(SoundPtr sound, bool loop) {
        sound->setLoop(loop);
    }

    __declspec(dllexport) void _Sound_SetVolume(SoundPtr sound, float volume) {
        sound->setVolume(volume);
    }

    __declspec(dllexport) void _Sound_SetPitch(SoundPtr sound, float pitch) {
        sound->setPitch(pitch);
    }

    __declspec(dllexport) void _Sound_SetAttenuation(SoundPtr sound, float attenuation) {
        sound->setAttenuation(attenuation);
    }

    __declspec(dllexport) void _Sound_ResetBuffer(SoundPtr sound) {
        sound->resetBuffer();
    }

    __declspec(dllexport) void _Sound_SetPosition(SoundPtr sound, float x, float y, float z) {
        sound->setPosition(x, y, z);
    }

    __declspec(dllexport) void _Sound_SetRelativeToListener(SoundPtr sound, bool relative) {
        sound->setRelativeToListener(relative);
    }
    
    __declspec(dllexport) int _Sound_GetStatus(SoundPtr sound) {
        return sound->getStatus();
    }
}

extern "C" {
    typedef sf::Music* MusicPtr;

    __declspec(dllexport) MusicPtr _Music_Create(const char* path) {
        MusicPtr music = new sf::Music();
        music->openFromFile(path);
        return music;
    }

    __declspec(dllexport) void _Music_Play(MusicPtr music) {
        music->play();
    }

    __declspec(dllexport) void _Music_Pause(MusicPtr music) {
        music->pause();
    }

    __declspec(dllexport) void _Music_Stop(MusicPtr music) {
        music->stop();
    }

    __declspec(dllexport) void _Music_SetLoop(MusicPtr music, bool loop) {
        music->setLoop(loop);
    }

    __declspec(dllexport) void _Music_SetVolume(MusicPtr music, float volume) {
        music->setVolume(volume);
    }

    __declspec(dllexport) void _Music_SetPitch(MusicPtr music, float pitch) {
        music->setPitch(pitch);
    }

    __declspec(dllexport) void _Music_SetAttenuation(MusicPtr music, float attenuation) {
        music->setAttenuation(attenuation);
    }
}
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
#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif

extern "C" {

    typedef sf::RenderTexture* RenderTexturePtr;

    __declspec(dllexport) RenderTexturePtr
    _RenderTexture_Init() {
        return new sf::RenderTexture();
    }

    __declspec(dllexport) bool
    _RenderTexture_Create(RenderTexturePtr texture, int width, int height) {
        return texture->create(width, height);
    }

    __declspec(dllexport) void
    _RenderTexture_Draw(RenderTexturePtr texture, sf::Drawable* shape) {
        texture->draw(*shape);
    }

    __declspec(dllexport) void
    _RenderTexture_Clear(RenderTexturePtr texture, int r, int g, int b, int a) {
        texture->clear(sf::Color(r, g, b, a));
    }

    __declspec(dllexport) void
    _RenderTexture_Display(RenderTexturePtr texture) {
        texture->display();
    }

    __declspec(dllexport) void
    _RenderTexture_SetSmooth(RenderTexturePtr texture, bool smooth) {
        texture->setSmooth(smooth);
    }

    __declspec(dllexport) void
    _RenderTexture_DrawWithStates(RenderTexturePtr texture, sf::Drawable* shape, sf::RenderStates* states) {
        texture->draw(*shape, *states);
    }

    __declspec(dllexport) void
    _RenderTexture_DrawWithShader(RenderTexturePtr texture, sf::Drawable* shape, sf::Shader* shader) {
        texture->draw(*shape, shader);
    }

    __declspec(dllexport) void
    _RenderTexture_SetView(RenderTexturePtr texture, sf::View* view) {
        texture->setView(*view);
    }

    __declspec(dllexport) sf::View*
    _RenderTexture_GetDefaultView(RenderTexturePtr texture) {
        return new sf::View(texture->getDefaultView());
    }

    __declspec(dllexport) sf::View*
    _RenderTexture_GetView(RenderTexturePtr texture) {
        return new sf::View(texture->getView());
    }

    __declspec(dllexport) sf::Texture* 
    _RenderTexture_GetTexture(RenderTexturePtr texture) {
        return new sf::Texture( texture->getTexture() );
    }

    __declspec(dllexport) void
    _RenderTexture_Delete(RenderTexturePtr texture) {
        delete texture;
    }


}

extern "C" {
    typedef sf::Texture* TexturePtr;

    __declspec(dllexport) TexturePtr _Texture_LoadFromFile(char* file_path) {
        TexturePtr texture = new sf::Texture();
        texture->loadFromFile(file_path);
        return texture;
    }

    __declspec(dllexport) TexturePtr _Texture_LoadFromFileWithBoundRect(char* file_path, int x, int y, int w, int h) {
        TexturePtr texture = new sf::Texture();
        texture->loadFromFile(file_path, sf::IntRect(x, y ,w, h));
        return texture;
    }

    __declspec(dllexport) void _Texture_Delete(TexturePtr texture) {
        delete texture;
    }

    __declspec(dllexport) int _Texture_GetMaxixmumSize(TexturePtr texture) {
        return texture->getMaximumSize();
    }

    __declspec(dllexport) int _Texture_GetSizeX(TexturePtr texture) {
        return texture->getSize().x;
    }

    __declspec(dllexport) int _Texture_GetSizeY(TexturePtr texture) {
        return texture->getSize().y;
    }

    __declspec(dllexport) void _Texture_SetRepeated(TexturePtr texture, bool value) {
        texture->setRepeated(value);
    }

    __declspec(dllexport) void _Texture_SetSmooth(TexturePtr texture, bool value) {
        texture->setSmooth(value);
    }

    __declspec(dllexport) void _Texture_Swap(TexturePtr texture, TexturePtr texture2) {
        texture->swap(*texture2);
    }

    __declspec(dllexport) TexturePtr _Texture_SubTexture(TexturePtr texture, int x, int y, int w, int h) {
        TexturePtr subTexture = new sf::Texture();
        subTexture->loadFromImage(texture->copyToImage(), sf::IntRect(x, y, w, h));
        return subTexture;
    }
}

extern "C" {

    typedef sf::Sprite* SpritePtr;
    
    __declspec(dllexport) sf::Sprite*
    _Sprite_GetFromRenderTexture(RenderTexturePtr texture) {
        return new sf::Sprite(texture->getTexture());
    }

    __declspec(dllexport) SpritePtr
    _Sprite_GetFromTexture(TexturePtr texture) {
        return new sf::Sprite(*texture);
    }

    __declspec(dllexport) void
    _Sprite_Scale(SpritePtr sprite, float x, float y) {
        sprite->scale(x, y);
    }

    __declspec(dllexport) void
    _Sprite_Rotate(SpritePtr sprite, float angle) {
        sprite->rotate(angle);
    }

    //////////////////////////////////////////////////////////////////
    // Setters
    //////////////////////////////////////////////////////////////////
    __declspec(dllexport) void
    _Sprite_SetColor(SpritePtr sprite, int r, int g, int b, int a) {
        sprite->setColor(sf::Color(r, g, b, a));
    }

    __declspec(dllexport) void
    _Sprite_SetOrigin(SpritePtr sprite, float x, float y) {
        sprite->setOrigin(x, y);
    }

    __declspec(dllexport) void
    _Sprite_SetPosition(SpritePtr sprite, float x, float y) {
        sprite->setPosition(x, y);
    }

    __declspec(dllexport) void
    _Sprite_SetRotation(SpritePtr sprite, float angle) {
        sprite->setRotation(angle);
    }

    __declspec(dllexport) void
    _Sprite_SetScale(SpritePtr sprite, float x, float y) {
        sprite->setScale(x, y);
    }

    // todo: 
    // __declspec(dllexport) void
    // _Sprite_SetTexture(SpritePtr sprite) {
    // }

    //////////////////////////////////////////////////////////////////

    __declspec(dllexport) int
    _Sprite_GetColorR(SpritePtr sprite) {
        return sprite->getColor().r;
    }
    
    __declspec(dllexport) int
    _Sprite_GetColorG(SpritePtr sprite) {
        return sprite->getColor().g;
    }

    __declspec(dllexport) int
    _Sprite_GetColorB(SpritePtr sprite) {
        return sprite->getColor().b;
    }

    __declspec(dllexport) int
    _Sprite_GetColorA(SpritePtr sprite) {
        return sprite->getColor().a;
    }

    __declspec(dllexport) float
    _Sprite_GetOriginX(SpritePtr sprite) {
        return sprite->getOrigin().x;
    }

    __declspec(dllexport) float
    _Sprite_GetOriginY(SpritePtr sprite) {
        return sprite->getOrigin().y;
    }

    __declspec(dllexport) float
    _Sprite_GetPositionX(SpritePtr sprite) {
        return sprite->getPosition().x;
    }

    __declspec(dllexport) float
    _Sprite_GetPositionY(SpritePtr sprite) {
        return sprite->getPosition().y;
    }

    __declspec(dllexport) float
    _Sprite_GetRotation(SpritePtr sprite) {
        return sprite->getRotation();
    }

    __declspec(dllexport) float
    _Sprite_GetScaleX(SpritePtr sprite) {
        return sprite->getScale().x;
    }

    __declspec(dllexport) float
    _Sprite_GetScaleY(SpritePtr sprite) {
        return sprite->getScale().y;
    }
}
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
// ================================================================================
//                         BUILDED_WINDOWEVENTS.cpp
//                    Биндинги для работы с событиями окон в PySGL
// ================================================================================
//
// Этот файл содержит C++ функции для работы с событиями SFML,
// которые экспортируются в Python через ctypes.
//
// Основные компоненты:
// - Создание и управление объектами событий
// - Получение информации о событиях клавиатуры
// - Обработка событий мыши (кнопки, координаты, колесо)
// - События изменения размера окна
// - Типизация и классификация событий
//
// ================================================================================

#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif
#ifndef SFML_WINDOW_HPP
#include "SFML/Window.hpp"
#endif

// ================================================================================
//                        УПРАВЛЕНИЕ ОБЪЕКТАМИ СОБЫТИЙ
// ================================================================================
// Функции для создания, удаления и базовой работы с событиями:
// - Создание новых объектов событий
// - Освобождение памяти
// - Получение типа события
// ================================================================================

extern "C" {
    // Создание нового объекта события для хранения данных
    __declspec(dllexport) sf::Event* _Events_Create() {
        return new sf::Event();
    }

    // Удаление объекта события и освобождение памяти
    __declspec(dllexport) void _Events_Destroy(sf::Event* event) {
        delete event;
    }

    // Получение типа текущего события (Closed, KeyPressed, MouseMoved и т.д.)
    __declspec(dllexport) int _Events_GetType(sf::Event* event) {
        return event->type;
    }

    // ================================================================================
    //                          СОБЫТИЯ КЛАВИАТУРЫ
    // ================================================================================
    // Функции для обработки событий клавиатуры
    
    // Получение кода нажатой/отпущенной клавиши
    __declspec(dllexport) int _Events_GetKey(sf::Event* event) {
        return event->key.code;
    }

    // ================================================================================
    //                            СОБЫТИЯ МЫШИ
    // ================================================================================
    // Функции для обработки всех типов событий мыши
    
    // Получение кода нажатой кнопки мыши (0-левая, 1-правая, 2-средняя)
    __declspec(dllexport) int _Events_GetMouseButton(sf::Event* event) {
        return event->mouseButton.button;
    }

    // Получение X-координаты курсора мыши в момент события
    __declspec(dllexport) int _Events_GetMouseX(sf::Event* event) {
        return event->mouseButton.x;
    }

    // Получение Y-координаты курсора мыши в момент события
    __declspec(dllexport) int _Events_GetMouseY(sf::Event* event) {
        return event->mouseButton.y;
    }

    // Получение значения прокрутки колеса мыши (положительное - вверх, отрицательное - вниз)
    __declspec(dllexport) int _Events_GetMouseWheel(sf::Event* event) {
        return event->mouseWheel.delta;
    }

    // ================================================================================
    //                      СОБЫТИЯ ИЗМЕНЕНИЯ РАЗМЕРА ОКНА
    // ================================================================================
    // Функции для получения новых размеров окна при событии Resized
    
    // Получение новой ширины окна после изменения размера (в пикселях)
    __declspec(dllexport) int _Events_GetSizeWidth(sf::Event* event) {
        return event->size.width;
    }

    // Получение новой высоты окна после изменения размера (в пикселях)
    __declspec(dllexport) int _Events_GetSizeHeight(sf::Event* event) {
        return event->size.height;
    }

}

// ================================================================================
//                              КОНЕЦ ФАЙЛА
// ================================================================================
// Все функции для работы с событиями PySGL определены.
// Они предоставляют полный интерфейс для обработки пользовательского ввода
// и системных событий в Python приложениях.
// ================================================================================
