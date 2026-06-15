[app]
# (string) Title of your application
title = Leaf Area Meter

# (string) Package name
package.name = leafareameter

# (string) Package domain (needed for android packaging)
package.domain = org.science

# (string) Source directory where main.py is located
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# !!! ВІДЕННЯ ПОМИЛКИ №1: Додано версію додатка !!!
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0,pillow,numpy,camera4kivy,cython<3.0.0

# (str) Supported orientations
orientation = portrait
fullscreen = 0

# (list) Permissions for Android 11+
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 21
android.ndk = 25c
android.private_storage = True

# !!! ВІДЕННЯ ПОМИЛКИ №2: Фіксуємо сучасну гілку p4a з підтримкою AAB !!!
p4a.branch = master

# Залежності Gradle для сучасної роботи CameraX з екосистеми camera4kivy
android.gradle_dependencies = "androidx.camera:camera-core:1.3.1", "androidx.camera:camera-camera2:1.3.1", "androidx.camera:camera-lifecycle:1.3.1", "androidx.camera:camera-view:1.3.1"
android.enable_androidx = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
warn_on_root = 0
