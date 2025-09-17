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
