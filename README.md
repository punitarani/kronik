# kronik

## Installation

- Prerequisites:
    - brew
    - Python 3.12+
    - Java Runtime Environment (JRE)
    - LLVM
- Android Debug Bridge (adb)
    - `brew install android-platform-tools`
- Download Android Command Line tools
    - Download
      from [https://developer.android.com/studio/command-line](https://developer.android.com/studio/command-line)
    - Extract the contents to `~/Library/Android/sdk/cmdline-tools/latest`
    - Add the following to PATH (might have to add to `.zshrc`/`.bash_profile`):
      ```bash
      export ANDROID_HOME=~/Library/Android/sdk
      export PATH=$ANDROID_HOME/emulator:$PATH
      export PATH=$ANDROID_HOME/platform-tools:$PATH
      export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$PATH
      ```
    - Download the tools:
      `sdkmanager --install "platform-tools" "emulator" "platforms;android-34" "system-images;android-34;google_apis_playstore;arm64-v8a"`
    - Install an emulator:
      `avdmanager create avd -n KronikPixel -k "system-images;android-34;google_apis_playstore;arm64-v8a" --device "pixel"`
    - Start the emulator: `emulator -avd KronikPixel`
    - List all emulators: `emulator -list-avds`
- Download [Appium](https://appium.io/docs/en/latest/)
    - Appium: `npm i --location=global appium`
    - Appium UIAutomator2 Server: `appium driver install uiautomator2`
- Download [FFmpeg](https://www.ffmpeg.org/)
    - MacOS: `brew install ffmpeg`
- Setup Kronik
    - `poetry install`

## Running the demo

This is to test the functionality of the installed packages and tools.

1. Run `appium` in a separate terminal
2. Start an emulator with `emulator -avd KronikPixel`
3. Run `poetry run python tests/demo.py`

## Running the application

### Start the backend

Start the backend API

```bash
Usage: poetry run uvicorn kronik.be.server:app--port 8000
```

### Run the application

Runs the main kronik application.

```bash
poetry run python kronik/main.py
```
