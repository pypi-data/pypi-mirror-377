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
