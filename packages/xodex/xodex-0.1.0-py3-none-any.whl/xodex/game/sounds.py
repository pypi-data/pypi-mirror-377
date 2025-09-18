import os
from typing import Optional
from importlib import import_module

import pygame
from pygame.mixer import Sound, Channel

from xodex.utils.values import Values
from xodex.core.singleton import Singleton
from xodex.core.exceptions import NotRegistered, AlreadyRegistered, ObjectError


class Sounds(Singleton):
    """
    Singleton class for managing sound effects and channels using pygame.mixer.
    Provides registration, playback, volume, mute, fade, and introspection utilities.

    Features:
    - Register, unregister, and batch register/unregister sounds.
    - Play, stop, pause, unpause, and fade in/out sounds and music.
    - Master volume and mute/unmute support.
    - Channel management and introspection.
    - Dynamic (re)loading and refreshing of sounds.
    - Optional callback on sound end (if supported).
    """

    _channels: dict[str, Channel] = {}
    _music: str = None
    _channel_count: int = 0
    _master_volume: float = 1.0
    _muted: bool = False

    def __init__(self, folder: str = "."):
        """
        Initialize the Sounds manager.

        :param folder: Default folder to load sounds from.
        """
        self.sound_folder = None
        try:
            xodex_settings = os.getenv("XODEX_SETTINGS_MODULE")
            self.setting = import_module(xodex_settings)
            self.sound_folder = self.setting.SOUND_DIR
        except Exception:
            pass
        self.sound_folder = self.sound_folder or folder
        self.__sounds: dict[str, Sound] = {}
        self.load_sounds(self.sound_folder)

    def __len__(self) -> int:
        return len(self.__sounds)

    def __contains__(self, key: str) -> bool:
        return key in self.__sounds

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return f"<{self.__class__.__name__} in {self.sound_folder}>"

    # region Music

    @classmethod
    def play_music(cls, loops: int = -1, start: float = 0, fade_ms: int = 0):
        """Play background music with optional fade-in."""
        try:
            pygame.mixer.music.load(Sounds._music)
            pygame.mixer.music.play(loops, start, fade_ms)
        except Exception as e:
            print(f"Failed to play music: {e}")

    @classmethod
    def set_music(cls, filename: str):
        """Set the music file to be played."""
        cls._music = filename

    @classmethod
    def stop_music(cls, fade_ms: int = 0):
        """Stop playing background music, with optional fade-out."""
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

    @classmethod
    def set_music_volume(cls, volume: float):
        """Set background music volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume * cls._master_volume)))

    @classmethod
    def pause_music(cls):
        """Pause background music."""
        pygame.mixer.music.pause()

    @classmethod
    def unpause_music(cls):
        """Unpause background music."""
        pygame.mixer.music.unpause()

    @classmethod
    def fadeout_music(cls, fade_ms: int = 1000):
        """Fade out the music over fade_ms milliseconds."""
        pygame.mixer.music.fadeout(fade_ms)

    @classmethod
    def mute_music(cls):
        """Mute background music."""
        pygame.mixer.music.set_volume(0.0)

    @classmethod
    def unmute_music(cls):
        """Unmute background music (restores master volume)."""
        pygame.mixer.music.set_volume(cls._master_volume)

    # endregion

    # region Sound/Channel

    def play(
        self, sound: str, channel: str = "", loops: int = 0, maxtime: int = 0, fade_ms: int = 0, on_end=None
    ) -> Optional[Channel]:
        """
        Play a sound by name, optionally on a named channel, with fade-in and callback.

        :param sound: Registered sound name.
        :param channel: Channel name (optional).
        :param loops: Number of loops.
        :param maxtime: Max time to play in ms.
        :param fade_ms: Fade-in time in ms.
        :param on_end: Optional callback when sound ends (if supported).
        :return: Channel object or None.
        """
        try:
            snd = self.__sounds[sound]
            if channel == "":
                ch = snd.play(loops, maxtime, fade_ms)
            else:
                ch = Sounds._channels[channel].play(snd, loops, maxtime, fade_ms)
            if ch and on_end and hasattr(ch, "set_endevent"):
                ch.set_endevent(on_end)
            return ch
        except KeyError:
            print(f"Sound or channel '{sound}'/'{channel}' not found.")

    def stop(self, sound: str):
        """
        Stop a sound by name and its channel if exists.

        :param sound: Registered sound name.
        """
        try:
            self.__sounds[sound].stop()
        except KeyError:
            print(f"Sound '{sound}' not found.")
        else:
            try:
                Sounds._channels[sound].stop()
            except KeyError:
                pass

    def set_volume(self, sound: str, volume: float):
        """
        Set the volume for a sound and its channel.

        :param sound: Registered sound name.
        :param volume: Volume (0.0 to 1.0).
        """
        try:
            self.__sounds[sound].set_volume(max(0.0, min(1.0, volume * self._master_volume)))
        except KeyError:
            print(f"Sound '{sound}' not found.")
        else:
            try:
                Sounds._channels[sound].set_volume(max(0.0, min(1.0, volume * self._master_volume)))
            except KeyError:
                pass

    @classmethod
    def pause(cls, channel: str) -> None:
        """Pause playback on a channel."""
        try:
            cls._channels[channel].pause()
        except KeyError:
            pass

    @classmethod
    def unpause(cls, channel: str) -> None:
        """Unpause playback on a channel."""
        try:
            cls._channels[channel].unpause()
        except KeyError:
            pass

    def fadeout(self, sound: str, fade_ms: int = 1000):
        """
        Fade out a sound by name.

        :param sound: Registered sound name.
        :param fade_ms: Fade-out time in ms.
        """
        try:
            self.__sounds[sound].fadeout(fade_ms)
        except KeyError:
            print(f"Sound '{sound}' not found.")

    def mute(self):
        """Mute all sounds and music."""
        self._muted = True
        for s in self.__sounds.values():
            s.set_volume(0.0)
        pygame.mixer.music.set_volume(0.0)

    def unmute(self):
        """Unmute all sounds and music (restores master volume)."""
        self._muted = False
        for s in self.__sounds.values():
            s.set_volume(self._master_volume)
        pygame.mixer.music.set_volume(self._master_volume)

    def set_master_volume(self, volume: float):
        """
        Set the master volume for all sounds and music.

        :param volume: Volume (0.0 to 1.0).
        """
        self._master_volume = max(0.0, min(1.0, volume))
        for s in self.__sounds.values():
            s.set_volume(self._master_volume)
        pygame.mixer.music.set_volume(self._master_volume)

    def is_muted(self) -> bool:
        """Return True if muted."""
        return self._muted

    # endregion Sound

    def pause_all(self):
        """Pause all channels."""
        pygame.mixer.pause()

    def unpause_all(self):
        """Unpause all channels."""
        pygame.mixer.unpause()

    @classmethod
    def channels(cls) -> Values:
        """Return all registered channels."""
        return Values(cls._channels)

    def sounds(self) -> Values:
        """Return all registered sounds."""
        return Values(self.__sounds)

    def play_if_not_busy(
        self, channel: str, sound: str, loops: int = 0, maxtime: int = 0, fade_ms: int = 0
    ) -> Optional[Channel]:
        """
        Play a sound on a channel only if the channel is not busy.
        """
        if not self.is_busy(channel):
            return self.play(sound, channel, loops, maxtime, fade_ms)
        return None

    def reset_play(self, channel: str, sound: str) -> Optional[Channel]:
        """
        Play a sound on a channel only if it's not already playing that sound.
        """
        try:
            main_sound = self.__sounds[sound]
        except KeyError:
            return None
        if self.get_sound(channel) is main_sound:
            return None
        return self.play(sound, channel)

    @classmethod
    def get_sound(cls, channel: str) -> Optional[Sound]:
        """
        Get the currently playing Sound object on a channel.
        """
        try:
            return cls._channels[channel].get_sound()
        except KeyError:
            return None

    @classmethod
    def is_busy(cls, channel: str) -> bool:
        """
        Check if a channel is currently playing any sound.
        """
        try:
            return cls._channels[channel].get_busy()
        except KeyError:
            return False

    def register(self, sound: Sound, sound_name: str):
        """
        Register a Sound object with a name.

        :param sound: Sound object.
        :param sound_name: Name to register.
        """
        if not isinstance(sound, Sound):
            raise ObjectError(f"The Sound {sound_name} is not of type Sound.")
        if self.isregistered(sound_name):
            raise AlreadyRegistered(f"The Sound {sound_name} is already registered.")
        self.__sounds[sound_name] = sound

    def batch_register(self, sounds: dict):
        """
        Register multiple sounds at once.

        :param sounds: Dict of {name: Sound}.
        """
        for name, sound in sounds.items():
            self.register(sound, name)

    def unregister(self, sound_name: str) -> None:
        """
        Unregister a Sound by name.

        :param sound_name: Registered sound name.
        """
        if not self.isregistered(sound_name):
            raise NotRegistered(f"The Sound {sound_name} is not registered")
        del self.__sounds[sound_name]

    def batch_unregister(self, sound_names: list):
        """
        Unregister multiple sounds at once.

        :param sound_names: List of sound names.
        """
        for name in sound_names:
            self.unregister(name)

    def isregistered(self, sound_name: str) -> bool:
        """
        Return True if a Sound is registered.

        :param sound_name: Registered sound name.
        """
        return sound_name in self.__sounds

    def exists(self, sound_name: str) -> bool:
        """
        Check if a sound file exists in the sound folder.

        :param sound_name: Sound file name.
        """
        return os.path.exists(os.path.join(self.sound_folder, sound_name))

    @classmethod
    def new_channel(cls, channel_name: str):
        """Create and register a new Channel with a name."""
        if not channel_name:
            return
        channel = Channel(cls._channel_count)
        cls._channels[channel_name] = channel
        cls._channel_count += 1

    @classmethod
    def remove_stopped(cls):
        """Remove channels that are not playing any sound."""
        to_remove = [name for name, ch in cls._channels.items() if not ch.get_busy()]
        for name in to_remove:
            del cls._channels[name]

    def load(self, filename: str, sound_name: str = ""):
        """
        Load a Sound file and register it.

        :param filename: Sound file name.
        :param sound_name: Name to register (optional).
        """
        if filename in os.listdir(self.sound_folder):
            try:
                sound = Sound(os.path.join(self.sound_folder, filename))
                if sound_name == "":
                    try:
                        self.register(sound, os.path.splitext(filename)[0])
                    except AlreadyRegistered:
                        pass
                else:
                    try:
                        self.register(sound, sound_name)
                    except AlreadyRegistered:
                        pass
            except Exception as e:
                print(f"Failed to load sound {filename}: {e}")

    def load_sounds(self, directory: str, extensions: tuple = (".wav", ".ogg", ".mp3")):
        """
        Load all sounds from a directory with given extensions.

        :param directory: Directory to load from.
        :param extensions: Tuple of allowed extensions.
        """
        try:
            for fname in os.listdir(directory):
                if fname.endswith(extensions):
                    self.load(fname)
        except Exception:
            print(f"Cannot find the path: '{directory}'")

    def reload_sounds(self, clear: bool = False):
        """
        Reload all sounds from the current sound folder.
        """
        if clear:
            self.__sounds.clear()
        self.load_sounds(self.sound_folder)
        return self

    def list_sounds(self) -> list:
        """List all registered sound names."""
        return list(self.__sounds.keys())

    @classmethod
    def list_channels(cls) -> list:
        """List all registered channel names."""
        return list(cls._channels.keys())

    def clear(self):
        """
        Clear all registered sounds and channels.
        """
        self.__sounds.clear()
        Sounds._channels.clear()
        Sounds._channel_count = 0

    def info(self) -> dict:
        """
        Get a summary of the current sound system state.

        :return: Dict with 'sounds' and 'channels' keys.
        """
        return {
            "sounds": self.list_sounds(),
            "channels": Sounds.list_channels(),
            "muted": self._muted,
            "master_volume": self._master_volume,
        }
