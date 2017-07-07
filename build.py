from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    visual_versions = [15]
    builder = ConanMultiPackager(username="vitallium", channel="testing", visual_versions=visual_versions)
    builder.add_common_builds(shared_option_name="libxslt:shared", pure_c=True)
    builder.run()
