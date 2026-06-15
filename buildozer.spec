[app]
title = Leaf Area Meter
package.name = leafareameter
package.domain = org.science
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Додаємо літеру 'v' перед версією numpy, оскільки рецепт робить git checkout, а теги в репозиторії NumPy мають вигляд v1.26.4
requirements = hostpython3==3.11.9,python3==3.11.9,kivy==2.3.0,pillow,numpy==v1.26.4,camera4kivy,cython<3.0.0

orientation = portrait
fullscreen = 0

android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 34

# Мінімальний API 24 (Android 7.0) для успішної збірки NumPy бінарників
android.minapi = 24

android.ndk = 25c
android.private_storage = True
android.accept_sdk_license = True
p4a.branch = master

# Передаємо прапорець компілятора безпосередньо в Buildozer, щоб ігнорувати помилки implicit-function-declaration у системних модулях Python
android.extra_cflags = -Wno-error=implicit-function-declaration

# Залежності для стабільної роботи камери через camera4kivy (CameraX)
android.gradle_dependencies = "androidx.camera:camera-core:1.3.1", "androidx.camera:camera-camera2:1.3.1", "androidx.camera:camera-lifecycle:1.3.1", "androidx.camera:camera-view:1.3.1"
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
