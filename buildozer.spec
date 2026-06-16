[app]
title = Leaf Area Meter
package.name = leafareameter
package.domain = org.science
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# ЗОЛОТА МАТРИЦЯ ВЕРСІЙ: 
# Жорстко фіксуємо Python 3.11 та стабільний NumPy 1.26.4
requirements = hostpython3==3.11, python3==3.11, kivy==2.3.0, pillow, numpy==1.26.4, camera4kivy

orientation = portrait
fullscreen = 0

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.ndk = 25c
android.private_storage = True
android.accept_sdk_license = True

# Прапорці для ігнорування суворих правил C-компілятора
android.extra_cflags = -Wno-error=implicit-function-declaration

android.gradle_dependencies = "androidx.camera:camera-core:1.3.1", "androidx.camera:camera-camera2:1.3.1", "androidx.camera:camera-lifecycle:1.3.1", "androidx.camera:camera-view:1.3.1"
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
