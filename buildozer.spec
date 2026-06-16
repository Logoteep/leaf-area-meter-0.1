[app]
title = Leaf Area Meter
package.name = leafareameter
package.domain = org.science
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# ЧИСТІ ВИМОГИ: Без "v", без "3.11.9", без hostpython. 
# Стабільний Buildozer сам все правильно завантажить.
requirements = python3,kivy==2.3.0,pillow,numpy,camera4kivy,cython<3.0.0

orientation = portrait
fullscreen = 0

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.ndk = 25c
android.private_storage = True
android.accept_sdk_license = True

# УВАГА: Рядок p4a.branch = master ВИДАЛЕНО, щоб уникнути експериментального Python 3.14

# Захист компілятора
android.extra_cflags = -Wno-error=implicit-function-declaration

# Залежності для стабільної роботи камери
android.gradle_dependencies = "androidx.camera:camera-core:1.3.1", "androidx.camera:camera-camera2:1.3.1", "androidx.camera:camera-lifecycle:1.3.1", "androidx.camera:camera-view:1.3.1"
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
