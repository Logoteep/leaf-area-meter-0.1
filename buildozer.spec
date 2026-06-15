[app]
title = Leaf Area Meter
package.name = leafareameter
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3, kivy==2.3.0, pillow, camera4kivy, plyer, cython<3.0.0

android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 21
android.ndk = 25c
android.gradle_dependencies = "androidx.camera:camera-core:1.3.1", "androidx.camera:camera-camera2:1.3.1", "androidx.camera:camera-lifecycle:1.3.1", "androidx.camera:camera-view:1.3.1"
android.enable_androidx = True

p4a.branch = develop
