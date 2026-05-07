[app]

title = AI陪伴
package.name = aipeiban
package.domain = org.aipeiban
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

# Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25b
android.sdk = 24

# Build
android.buildtools = 30.0.3
android.use_aapt2 = True

# Requirements
requirements = python3,kivy,requests,urllib3,chardet,idna,certifi

# Icon (optional - using default icons)
# android.icon = %(source.dir)s/res/icon.png
# android.adaptive_icon = %(source.dir)s/res/adaptive_icon.png

# Splash screen (optional)
# android.splashscreen = %(source.dir)s/res/splash.png
android.splashscreen_color = #F5F5F5

# Orientation
android.orientation = portrait

# Deployment
android.deploy = debug
android.build_type = debug

# Other
android.add_assets = data/

[buildozer]
log_level = 2
warn_on_root = 1