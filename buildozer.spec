[app]
title = Leaf Area Meter
package.name = leafareameter
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3==3.10.11, hostpython3==3.10.11, kivy==2.3.0, pillow, pyjnius, android

orientation = portrait
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.features = android.hardware.camera, android.hardware.camera.autofocus

p4a.branch = develop
