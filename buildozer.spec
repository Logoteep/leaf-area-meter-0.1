[app]
title = Leaf Area Meter
package.name = leafareameter
package.domain = org.science
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# 1. Прибираємо hostpython3 та python3 версії — Buildozer сам поставить свою стабільну, pre-patched версію Python.
# 2. Замість точної версії numpy вказуємо <2.0.0. Це змусить завантажити останній реліз гілки 1.x (1.26.4) з PyPI у вигляді C-архіву, оминаючи помилки Git-тегів та C++20 збої.
requirements = python3,kivy==2.3.0,pillow,numpy<2.0.0,camera4kivy,cython<3.0.0

orientation = portrait
fullscreen = 0

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.ndk = 25c
android.private_storage = True
android.accept_sdk_license = True
p4a.branch = master

# Додатковий захист від суворих правил компілятора
android.extra_cflags = -Wno-error=implicit-function-declaration

android.gradle_dependencies = "androidx.camera:camera-core:1.3.1", "androidx.camera:camera-camera2:1.3.1", "androidx.camera:camera-lifecycle:1.3.1", "androidx.camera:camera-view:1.3.1"
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
