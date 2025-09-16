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
