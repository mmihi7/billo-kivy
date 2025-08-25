[app]

# (str) Title of your application
title = Billo

# (str) Package name
package.name = com.billo.customer

# (str) Package domain (needed for android/ios packaging)
package.domain = org.billo

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (list) List of inclusions using entry points
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,cython==0.29.36,kivy==2.2.1,kivymd==1.1.1,pyjnius@git+https://github.com/kivy/pyjnius.git@master,supabase,python-dotenv,pyjwt,cryptography,pycryptodome,requests,pillow

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = 2.0.0

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB
#android.presplash_color = #FFFFFF

# (string) Presplash animation using Lottie format.
# see https://lottiefiles.com/ for examples
# Lottie files can be created using various tools, like Adobe After Effect or Synfig
#android.presplash_lottie = "path/to/lottie/file.json"

# (str) Adaptive icon background color
#android.adaptive_icon_background = #FFFFFF

# (str) Adaptive icon foreground image
#android.adaptive_icon_foreground = %(source.dir)s/data/icon_fg.png

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (list) features (adds uses-feature -tags to manifest)
#android.features = android.hardware.usb.host

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 23b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
#android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
# android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a file which will show on Android after splash.
#android.show_splash = True

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Skip byte compile for .py files
# android.no-byte-compile-python = False

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a, armeabi-v7a

#
# Python for android (p4a) specific
#

# (str) python-for-android fork to use, defaults to upstream (kivy)
p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port =

# Control passing the --use-setup-py vs --ignore-setup-py to p4a
# "in the future" --use-setup-py is the behaviour of p4a, right now it is --ignore-setup-py
# Setting this to false will passes --ignore-setup-py, true will pass --use-setup-py
# Setting to os.environ.get('ANDROID_INCREMENTAL_BUILD', True) makes the default pass --use-setup-py if the env var is not set.
#android.p4a_use_setup_py = False

# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain
# Note: use this to disable ccache (for Android debugging)
# android.p4a_add_myself = --copy-libs --sdk-dir=/path/to/sdk --ndk-dir=/path/to/ndk
# (str) extra command line arguments to pass to gradle during builds
# android.gradle_options = -Pandroid.injected.signing.store.file=/path/to/keystore -Pandroid.injected.signing.store.password=***** -Pandroid.injected.signing.key.alias=key-alias -Pandroid.injected.signing.key.password=******

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (list) Java files to add as activities to the manifest.
#android.add_java_files = ExampleActivity.java

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of a custom template to use for AndroidManifest.xml
#android.manifest.template =

# (str) Name of the custom template to use for AndroidManifest.tmpl
#android.manifest.merge.template =

# (str) A type of the theme
# Android documentation, 1= Material 2=Material3
#android.material_theme = 1

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Skip byte compile for .py files
# android.no-byte-compile-python = False

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In general, in you should aim to build for
# Use arch = arm64-v8a for newer devices and armeabi-v7a for older ones.
# You can specify multiple archs, as in the example below.
# arch = armeabi-v7a arm64-v8a
#
# If you get a "WARNING: unknown --target-os" run
# "shell buildozer "p4a.branch=master" android debug"
# (and leave the "p4a.branch" option in the [app] section)
#
# Values meaning all arches (default), all supported by the SDK, or a list of the wanted ones
#android.archs = armeabi-v7a

# (str) The format used to package the app for release mode (aab or apk or aar).
# android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aar).
# android.debug_artifact = apk

# (str) The API key for your Google Maps Android app
#android.map_api_key = ""

# Path to the patch file
p4a.patch_dir = .
# Apply the patch to pyjnius
p4a.patches = fix_pyjnius.patch

# Enable pre-build hook
pre_build = hooks/pre-build.sh