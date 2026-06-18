# CoT Forwarder — ATAK-CIV 5.7.0.5 plugin

Selectively forwards Cursor-on-Target (CoT) marker data from ATAK to an external
device (e.g. a Raspberry Pi) **bypassing the TAK server**. The operator flips a single
marker ON/OFF with a toggle button in the radial menu; the data is sent as line-framed
JSON over UDP or TCP.

The companion receiver lives in the sibling folder **`../pi-receiver/`** (its own
README explains how to run it).

---

## 1. What it does

- **Radial-menu toggle.** For any `PointMapItem` of an "atom" type (`a-*` — Friendly /
  Hostile / Neutral / Unknown …) a green/gray **ON/OFF** button appears in the marker's
  radial menu (`ForwardMenuFactory` registered with `MapMenuReceiver`).
- **State in metadata.** The ON/OFF flag is stored with `setMetaBoolean("cotfwd.enabled", …)`
  so it survives UI refreshes and an ATAK restart (ATAK's statesaver persists it).
- **ON:** immediately sends an `UPDATE` (UID, type, callsign, lat, lon, hae) and attaches
  an `OnPointChangedListener` — every move of the marker sends another `UPDATE`.
- **OFF / removal:** sends a `DELETE` for the UID. Removal is caught globally via
  `MapEvent.ITEM_REMOVED`, so deleting an ON marker also sends a `DELETE`.
- **Feedback:** a short Toast (in Polish — "Przesylanie WL/WYL: <callsign>") and the
  icon flips green↔gray on every toggle.
- **Preferences:** destination IP / Port / Protocol (UDP/TCP), under
  *Settings → Tool Preferences → CoT Forwarder*.
- **Networking:** all socket I/O runs on a single background `ExecutorService` (no
  `NetworkOnMainThreadException`); changing the settings re-opens the sockets **without
  restarting ATAK** (`OnSharedPreferenceChangeListener`).

---

## 2. How it works (architecture)

```
CotForwarderLifecycle            IPlugin entry point (declared in assets/plugin.xml)
  └─ CotForwarderMapComponent    onCreate wires everything; onDestroyImpl tears it down
       ├─ NetworkManager         UDP/TCP send on a background executor; reloads on pref change
       ├─ ForwardManager         per-marker ON/OFF state + movement & removal listeners
       │    └─ CotJson           builds the UPDATE / DELETE JSON payloads
       └─ ForwardMenuFactory     injects the ON/OFF button into the radial menu
       └─ CotForwarderPreferenceFragment   the IP / Port / Protocol screen
```

Data flow for a toggle:

```
radial button tap
  → ForwardMenuFactory.performAction
    → ForwardManager.toggle  (flips cotfwd.enabled metadata)
      → CotJson.update/delete (build JSON)
        → NetworkManager.send (executor → UDP/TCP, payload = json + "\n")
          → ../pi-receiver  receives and prints/acts on it
```

Source files (`app/src/main/java/com/atakmap/android/cotforwarder/`):

| File | Responsibility |
|---|---|
| `plugin/CotForwarderLifecycle.java` | `IPlugin` → `AbstractPlugin(MapComponent)` entry point |
| `plugin/PluginNativeLoader.java` | native-lib loader boilerplate (unused; no `.so` shipped) |
| `CotForwarderMapComponent.java` | lifecycle; builds & registers all collaborators |
| `ForwardMenuFactory.java` | the ON/OFF radial-menu button |
| `ForwardManager.java` | ON/OFF state, movement & removal listeners |
| `NetworkManager.java` | UDP/TCP I/O on an executor + live pref reload |
| `CotJson.java` | UPDATE / DELETE JSON payload builder |
| `CotForwarderPreferenceFragment.java` | the preference screen |

### JSON wire format

One message per line (`\n`-terminated), UTF-8:

```json
{"action":"UPDATE","uid":"ABC-123","type":"a-h-G","callsign":"Alpha","lat":52.2297,"lon":21.0122,"hae":135.0,"time":1718200000000}
{"action":"DELETE","uid":"ABC-123","time":1718200000000}
```

---

## 3. Repository layout

```
CotForwarderPlugin/          <- THIS folder (the ATAK plugin, a Gradle project)
├── app/                     <- plugin module (Java sources, assets, resources)
├── gradle/  build.gradle  settings.gradle  gradlew[.bat]
├── local.properties        <- machine-specific paths (NOT committed — see §4)
└── README.md               <- this file

../pi-receiver/              <- SIBLING folder: the Raspberry Pi receiver (own README)
```

> **Important:** the plugin is built against a local ATAK SDK. It expects to sit
> **inside the ATAK SDK directory** (so the relative paths to `atak-gradle-takdev.jar`
> and `android_keystore` resolve), or to be pointed at the SDK via `local.properties`
> (see §4). Each developer needs the matching **ATAK-CIV 5.7.0.5 SDK** locally.

---

## 4. Prerequisites & `local.properties`

- **JDK 17** — Android Studio bundles a suitable JBR (e.g.
  `C:\Program Files\Android\Android Studio\jbr`). Set `JAVA_HOME` to it for CLI builds.
- **Android SDK** with platform `android-34` and build-tools `34.0.0`.
- **ATAK-CIV 5.7.0.5 SDK** (provides `atak-gradle-takdev.jar`, `main.jar`,
  `android_keystore`). The plugin builds in **offline dev-kit** mode (no remote TAK repo).

`local.properties` is **not committed** (machine-specific). Create it with:

```properties
# Android SDK location
sdk.dir=C:\\Users\\<you>\\AppData\\Local\\Android\\Sdk

# ATAK SDK root — lets the takdev offline dev-kit find main.jar / keystore.
# REQUIRED unless this project sits exactly one level under the SDK root.
sdk.path=D:/ATAK-CIV-5.7.0.5-SDK

# Signing (from the official ATAK template keystore). Point at the real file:
takDebugKeyFile=D:/ATAK-CIV-5.7.0.5-SDK/android_keystore
takDebugKeyAlias=wintec_mapping
takDebugKeyFilePassword=tnttnt
takDebugKeyPassword=tnttnt
takReleaseKeyFile=D:/ATAK-CIV-5.7.0.5-SDK/android_keystore
takReleaseKeyAlias=wintec_mapping
takReleaseKeyFilePassword=tnttnt
takReleaseKeyPassword=tnttnt
```

> **Why `sdk.path`?** The takdev plugin's offline dev-kit looks for `main.jar` (the
> ATAK API) in `${rootDir}/../..` and in `${sdk.path}`. The SDK `samples/<name>/` sit
> *two* levels under the SDK root so the first path matches them; if you place this
> project anywhere else, set `sdk.path` to the SDK root so the second path matches.

---

## 5. Build

**Recommended:** open the folder in **Android Studio**, select the `civDebug` build
variant (*Build → Select Build Variants → `civDebug`*) and Build.

From the command line (with `JAVA_HOME` on JDK 17):

```bash
cd CotForwarderPlugin
./gradlew assembleCivDebug          # or  gradlew.bat assembleCivDebug   on cmd
```

Output APK:

```
app/build/outputs/apk/civ/debug/ATAK-Plugin-cotforwarder-0.1--5.7.0-civ-debug.apk
```

For a shippable build use `assembleCivRelease` (proguard-shrunk, signed with the same
keystore → `…-civ-release.apk`).

The APK is signed with the official ATAK template identity (`O=WinTec Arrowmaker`,
alias `wintec_mapping`) — **do not change the signing config**, or ATAK will refuse to
load the plugin.

---

## 6. Install, enable, configure, use

1. **Install:** `adb install -r app/build/outputs/apk/civ/debug/<apk>`
2. **Load the plugin:** launch ATAK → ☰ menu → **Plugins** (TAK Package Mgmt) → find
   **CoT Forwarder** → tap to **Load** it (status becomes *Loaded*). Newly installed
   plugins are detected but not auto-loaded; you must enable them here once.
3. **Configure:** *Settings → Tool Preferences → CoT Forwarder* → set **IP**, **Port**
   (default `18999`), **Protocol** (UDP/TCP) of your receiver. Changes apply live.
4. **Run the receiver** on the target host — see `../pi-receiver/README.md`.
5. **Use:** drop a marker → open its **radial menu** → tap the **»** button. It turns
   **green** (ON) and an `UPDATE` is sent; tap again → **gray** (OFF) and a `DELETE` is
   sent. Moving an ON marker streams further `UPDATE`s; deleting it sends a `DELETE`.

> ATAK gives no other on-screen confirmation — the Toast and the icon color are the
> feedback; the authoritative proof is the receiver's log.

---

## 7. Testing on an Android emulator (no physical device)

Useful for development. ATAK ships `x86_64` native libs so it runs on a standard
`x86_64` emulator (`android-34 / google_apis`).

- **GPU:** ATAK's map crashes with `GLSurfaceView "No config chosen"` under
  `-gpu auto`/`-gpu host`. Launch the emulator with **`-gpu swiftshader_indirect`**.
- **First-run wizard:** grant permissions via adb to skip it, e.g.
  `adb shell pm grant com.atakmap.app.civ android.permission.ACCESS_FINE_LOCATION`
  (also `..._STORAGE`, `POST_NOTIFICATIONS`, etc.), then relaunch ATAK.
- **Reaching a receiver on your PC:** from the emulator the host is `10.0.2.2`. Run the
  receiver on your PC and set the plugin's **IP = `10.0.2.2`**.
- ATAK in the SDK is debuggable, so you can pre-seed the IP without typing on the
  emulator keyboard: with ATAK force-stopped, inject `cotfwd_ip/cotfwd_port/cotfwd_proto`
  into `…/shared_prefs/com.atakmap.app.civ_preferences.xml` via
  `adb … run-as com.atakmap.app.civ`, then relaunch.
- Watch the data flow with: `adb logcat -s CotFwd.MenuFactory CotFwd.Manager CotFwd.Network`.

The **network half** can be tested with no ATAK at all — see
`../pi-receiver/test_network.py`.

---

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `package com.atakmap.* does not exist` at compile | takdev can't find the ATAK API. Set `sdk.path` in `local.properties` to the SDK root (§4). |
| `Keystore file … not found for signing config` | Fix `takDebugKeyFile` / `takReleaseKeyFile` in `local.properties` to the real `android_keystore` path (§4). |
| Plugin installs but `AtakPluginRegistry: … will NOT load` | Not enabled yet — load it in the Plugin Manager (§6, step 2). |
| Toggle does nothing visible | Expected — check the receiver log / `adb logcat` (no on-screen action beyond the Toast/icon). |
| Toggle sends to the wrong host | Set IP/Port/Protocol in Tool Preferences; for an emulator use `10.0.2.2`. |
| Emulator: ATAK crashes on startup (`No config chosen`) | Use `-gpu swiftshader_indirect` (§7). |

---

## 9. Notes

- **Icons:** `assets/icons/ic_forward_on.png` (green) / `ic_forward_off.png` (gray) are
  small generated double-chevron glyphs (~64×64, transparent). Swap them freely.
- **Java, not Kotlin/lambdas:** listeners use anonymous classes on purpose — the SDK
  README warns that lambdas can be broken by proguard in release builds.
- **Signing:** keystore password `tnttnt`, alias `wintec_mapping` (official template).
  Required for ATAK to load the plugin; do not remove.
