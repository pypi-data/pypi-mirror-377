from setuptools import setup

setup(
    name="hypium",
    version="6.0.5.200",
    description="A UI test framework for HarmonyOS devices",
    license="",
    packages=['hypium',
              'hypium.action',
              'hypium.action.app',
              'hypium.action.host',
              'hypium.action.device',
              'hypium.checker',
              'hypium.advance',
              'hypium.advance.deveco_testing',
              'hypium.uidriver.interface',
              'hypium.uidriver.ohos',
              'hypium.uidriver.common',
              'hypium.uidriver.uitree',
              'hypium.uidriver.uitree.widget_finder',
              'hypium.model',
              'hypium.uidriver',
              'hypium.utils',
              'hypium.webdriver',
              "hypium.dfx"],
    package_data={
        "hypium": ["dfx/*.md", "dfx/data"],
    },
    install_requires=[
        "psutil",
        "lxml",
        "opencv-python",
        "xdevice",
        "xdevice-ohos",
        "xdevice-devicetest",
    ],
    extras_require={
        "advance": ["opencv-python"],
        "qr": ["pyzbar", "qrcode"]
    },
    include_package_data=True
)
