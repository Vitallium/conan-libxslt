from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="vitallium", channel="testing")
    visual_versions = [14]
    builder.add_common_builds(shared_option_name="libxslt:shared", visual_versions=visual_versions, pure_c=True)
    builder.run()