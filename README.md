# About the KloPi

The KloPi is a fun project which has been realized for a bar in my neighborhood.
They changed to waterless urinals, but kept the push buttons.
As they are now useless the idea came up that when someone pushes the button, a soundfile shall be played.

This repositiry contains the software for the controller and descriptions of the hardware that is needed in order to set up the system.

# BOM

* Raspberry Pi or similar device with Bluetooth
* Bluetooth Speaker
* 433 MHz Receiver
* 433 MHz Sender
* Buttons for the Toilet Assembly


# System Preparations

The following instractions have been verified on Armbian Bullseye. However they should work equally well on Raspbian and the likes.

Install tools and services:
```
# apt install sox libsox-fmt-pulse libsox-fmt-mp3 \
    pulseaudio pulseaudio-module-bluetooth pulsemixer \
    bluetooth bluez bluez-firmware \
    gpiod python3-libgpiod \
    inotify-tools git python3-pyinotify
# cp system.pa /etc/pulse/system.pa
# cp pulseaudio.service /etc/systemd/system/pulseaudio.service
```

As described in the [pulseaudio documentation](https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/SystemWide/), the users of the system which need to access the audio system must belong to the correct groups.
> When PulseAudio starts in the system mode, it will change its user and group from root to pulse in order to not have too many privileges.
> The pulse user needs to be in the audio and bluetooth groups in order to be able to use ALSA and bluetooth devices.
>
> All users that need access to PulseAudio have to be in the pulse-access group, even root.
> (TODO: We should probably allow root to access PulseAudio without being in the pulse-access group. Patches welcome!)

After the system is prepared, perform a reboot and try to connect the bluetooth speaker.
```
# bluetoothctl
[bluetooth]# scan on
[bluetooth]# devices
Device 12:34:56:78:9A:BC Some BT Speaker
[bluetooth]# pair 12:34:56:78:9A:BC
[bluetooth]# connect 12:34:56:78:9A:BC
Attempting to connect to 12:34:56:78:9A:BC
[CHG] Device 12:34:56:78:9A:BC Connected: yes
Connection successful
```

Once the speaker is connected, open pulsemixer and set the new speaker as default sink, so it is used when playing sound files.

In order to set up automatic connection establishment with the speaker, the [bluetoothctl-autoconnector](https://github.com/noraworld/bluetoothctl-autoconnector) can be used.

Install the soundserver service and create the appropriate user.
```
# adduser --disabled-password klopi_sound
# sudo -u klopi_sound mkdir /home/klopi_sound/music
# cp soundserver.service /etc/systemd/system/soundserver.service
# systemctl enable soundserver.service
```

In case /var/run is on a ramfs, add the following lines to `/etc/rc.local`.
```
# init klopi run folder
mkdir /var/run/klopi
chown klopi_sound /var/run/klopi
```

Learn the signal from the remote control by executing the `find_signals.py` script.
If it detects a proper signal, it will be output to the console.
The signal value must then be copied to the file `/root/signals.list`.
The list file can contain multiple signal definitions, where each signal value is one line.

Once the signal can be captured successfully (test with the `watch_air.py` command directly), the watch service can be installed.
```
# cp airwatcher.service /etc/systemd/system/airwatcher.service
# systemctl enable airwatcher.service
```

The last step is to add some music to the `/home/klopi_sound/music` folder.
