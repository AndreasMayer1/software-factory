# Android Device Setup for Integration Tests

This guide covers attaching an Android device to the devcontainer so the LLM-autonomous integration-test loop can drive it as a Flutter target. It satisfies REQ-PROC-054 AC-07.

Two paths are supported: USB attachment (the device is plugged into the Windows host and forwarded into WSL), and wireless attachment (the device exposes `adb` over TCP and the container connects directly). Either path produces the same outcome — `flutter devices` in the container lists the device, and `flutter test integration_test -d <device-id>` runs against it.

A physical device is faster than an emulator (no cold boot) and exercises real Android hardware. When no device is plugged in, the optional Android-emulator narrow-watcher path documented in REQ-PROC-054 AC-07 fills the same role at the cost of emulator boot time; its implementation is tracked separately.

---

## 1. Prerequisites on the Android device

Performed once per device.

1. Open **Settings → About phone**, tap **Build number** seven times to enable developer mode.
2. Open **Settings → System → Developer options**, enable **USB debugging**.
3. For wireless attachment, also enable **Wireless debugging** in Developer options.
4. Plug the device into a USB port on the Windows host (or, for wireless-only, connect it to the same network as the Windows host).
5. On first connection the device shows a "Allow USB debugging?" prompt with the host's RSA fingerprint. Confirm and check "Always allow from this computer" so the prompt does not repeat.

If the device is already used for development from another machine, the prompt may not appear; revoking USB-debugging authorizations under Developer options forces it again.

---

## 2. USB attachment via usbipd-win

Performed once per Windows host, plus once per attach session.

### 2.1 Install `usbipd-win` on the Windows host

In an elevated PowerShell window:

```powershell
winget install --interactive --exact dorssel.usbipd-win
```

Restart the Windows host once after installation so the kernel driver loads. `usbipd-win` provides the `usbipd` command and the WSL-side `usbip` client; no separate setup is needed inside WSL on a current Ubuntu 22.04 distro.

### 2.2 Identify the device's bus ID

Plug the device into the Windows host. In a regular PowerShell window:

```powershell
usbipd list
```

The output lists USB devices with `BUSID`, `VID:PID`, and `DESCRIPTION` columns. Locate the Android device — typically described by the manufacturer name (for example `Samsung Galaxy A40`). Note its `BUSID` (commonly something like `2-3`).

### 2.3 Bind the device (one time per device)

In an elevated PowerShell window:

```powershell
usbipd bind --busid <busid>
```

This marks the device as shareable. Binding is persistent across reboots; only re-run after unbinding.

### 2.4 Attach the device into WSL

In a regular PowerShell window (no elevation required):

```powershell
usbipd attach --wsl --busid <busid>
```

The attachment is per-session and ends when the device is unplugged, the Windows host is rebooted, or `usbipd detach --busid <busid>` is invoked. For a daily workflow, attach once at the start of the development session.

### 2.5 Verify the device is reachable from the container

Open a terminal inside the devcontainer:

```bash
adb devices
```

The device should appear with a numeric serial and status `device`. If status is `unauthorized`, accept the trust prompt on the device (see §1, step 5). If status is `offline`, detach and re-attach via usbipd.

Then verify Flutter sees it:

```bash
flutter devices
```

The device should appear in the list with its model name and platform.

---

## 3. Wireless attachment via adb tcpip

Useful when the device cannot remain physically tethered to the Windows host, or as a fallback if usbipd is unavailable.

### 3.1 Initial pairing over USB (one time)

The first wireless attachment still requires a one-time USB connection so the device records the host's RSA key. Complete §2.1 through §2.5 first; once `adb devices` lists the device authorized over USB, proceed.

### 3.2 Switch the device's adb daemon to TCP mode

From inside the container, with the device USB-attached and authorized:

```bash
adb tcpip 5555
```

The device's adb daemon now listens on TCP port 5555 on the device's local network interface. This setting persists until the device reboots; after a reboot the device returns to USB mode and §3.2 must be re-run.

### 3.3 Note the device's IP address

In the Android device's **Settings → About phone → Status** (path varies by OEM), record the **IP address** on the Wi-Fi network. Or list it from the container after the USB session:

```bash
adb shell ip route | awk '{print $9}'
```

The address typically looks like `192.168.x.y` (or whatever range the local Wi-Fi uses).

### 3.4 Connect over TCP

```bash
adb connect <device-ip>:5555
```

`adb devices` now lists the device by `<device-ip>:5555` as its serial; `flutter devices` recognises it the same way.

The connection persists until the device reboots, the network changes, or `adb disconnect <device-ip>:5555` is run.

### 3.5 Reconnecting in a later session

After a device reboot, re-pair over USB (§3.2) once, then `adb connect` again. Once paired, the device remembers the host's key and re-pairing is fast.

If only the network changes (the device IP moves), `adb connect <new-ip>:5555` is enough; the device's daemon stays in TCP mode.

---

## 4. Running an integration test against the attached device

With the device listed by `flutter devices`, run an integration test from the project root inside the container:

```bash
flutter test integration_test -d <device-id>
```

Where `<device-id>` is one of the values from `flutter devices` — either the USB serial or the `<ip>:5555` form. The test runs on the device; results print to the container's terminal.

For a specific test file:

```bash
flutter test integration_test/path/to/specific_test.dart -d <device-id>
```

---

## 5. Troubleshooting

### `adb devices` shows the device as `unauthorized`

Accept the trust prompt on the device (it may be hidden under the lock screen). If no prompt appears, revoke USB-debugging authorizations in Developer options on the device and re-attach.

### `adb devices` is empty after usbipd attach

Confirm the device shows up at the host first: in PowerShell, `usbipd list` should mark the bus ID as `Attached` and the WSL distro name. If it shows `Shared` rather than `Attached`, re-run `usbipd attach --wsl --busid <busid>`. If it shows nothing for the device, the device is unplugged or the cable is data-incapable (some USB cables are charge-only).

### `adb connect` returns `failed to connect to <ip>:5555`

Most common cause: the device's adb daemon reverted to USB mode after a reboot. Reconnect over USB, run `adb tcpip 5555` again, then retry `adb connect`. Second cause: the device's IP changed — re-check it in device settings.

### `flutter devices` lists nothing despite `adb devices` showing the device

The Flutter SDK in the container has a separate `adb` client. Restarting the SDK's cached state usually resolves it:

```bash
adb kill-server
adb start-server
flutter devices
```

If still empty, run `flutter doctor` to see whether the Android toolchain is in a healthy state.

### `usbipd attach` from PowerShell complains about no default WSL distro

`usbipd attach --wsl` targets the default WSL distro. Set the project's distro as the default once: `wsl --set-default <distro-name>`. List distros with `wsl --list --verbose`.

### Integration test runs but the device's screen stays dark

Wake the device manually before invoking the test. Integration tests do not unlock a locked device; ensure the device is on its home screen with the screen on. For an unattended setup, disable the device's lock screen during integration-test work.

---

## 6. Related material

- [`wsl_devcontainer_setup.md`](wsl_devcontainer_setup.md) — prerequisite. The devcontainer must be reachable and the project source-of-truth must be on WSL ext4 before Android device attachment matters.
- [`sync_setup.md`](sync_setup.md) — not relevant for Android-target tests, which run entirely from the container. Mutagen is only needed for Windows-target operations.
- REQ-PROC-054 AC-07 — the contract this guide realises.
- REQ-NFUNC-023 *Epic: Integration Tests* — defines *which* integration tests must exist per user flow; this guide tells you how to run them against an Android target.
