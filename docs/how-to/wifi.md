# Connect over Wi-Fi

Start with a working, authorized USB ADB connection from the [tutorial](../tutorials/first-training.md). Put the computer and Quest on the same trusted local network. Keep the headset awake. Replace `USB_SERIAL` and `QUEST_IP` in every command; they are placeholders.

1. While USB is still connected, enable the headset's TCP transport:

   ```console
   adb -s USB_SERIAL tcpip 5555
   ```

2. Find the headset's current local IP in its connected Wi-Fi network details, or inspect its route:

   ```console
   adb -s USB_SERIAL shell ip route
   ```

   In typical output, the address after `src` is the device address. Do not use the gateway address after `via`.

3. Connect and verify the network transport:

   ```console
   adb connect QUEST_IP:5555
   adb -s QUEST_IP:5555 get-state
   adb devices -l
   ```

   Accept an authorization prompt in the headset if one appears. Continue only when the exact `QUEST_IP:5555` row says `device`.

4. Unplug USB, run `get-state` again, then use the network serial:

   ```console
   python -m eleven_trainer pull .local/wifi-export.json --device QUEST_IP:5555
   python -m eleven_trainer install .local/cycle.json --device QUEST_IP:5555
   ```

The USB cable is no longer needed for these transfers while the connection remains valid. A restart, network change or expired authorization may require USB setup again. If connection fails, reconnect USB, authorize, and repeat the steps; do not repeatedly launch new ADB servers.

## Close wireless access

Switch the headset transport back to USB, then drop the host connection:

```console
adb -s QUEST_IP:5555 usb
adb disconnect QUEST_IP:5555
```

`adb disconnect` alone closes the computer's connection; it does not disable the headset's TCP listener. Use this legacy TCP method only on a trusted LAN, without router port forwarding. These commands follow Android's [USB-initialized Wi-Fi ADB workflow](https://developer.android.com/tools/adb#wireless).

## Use a different computer-side ADB port

If another service occupies local port 5037, consistently use one alternate port for raw ADB and the tool:

```console
adb -P 15037 devices -l
adb -P 15037 connect QUEST_IP:5555
python -m eleven_trainer devices --adb-port 15037
python -m eleven_trainer install .local/cycle.json --device QUEST_IP:5555 --adb-port 15037
```

`15037` is the computer's ADB server port. `5555` is the headset's TCP port. They serve different endpoints. Apply `-P 15037` to the USB bootstrap commands too when using that server.
