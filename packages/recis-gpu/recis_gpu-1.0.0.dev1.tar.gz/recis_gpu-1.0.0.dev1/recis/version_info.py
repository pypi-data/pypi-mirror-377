

VERSION = "1.0.0"

GIT_BRANCH = "main"
GIT_COMMIT_HASH = "a13904e"
GIT_COMMIT_HASH_FULL = "a13904e44a10df627dc9fbcc3b819dedefe886df"
GIT_COMMIT_TIME = "2025-09-12 20:27:31 +0800"
GIT_COMMIT_AUTHOR = "Ctios"
GIT_COMMIT_MESSAGE = """ci(ci): add build wheel and realese action"""
GIT_TAG = "v1.0.0"

BUILD_TIME = "2025-09-17T15:14:12.935976"
BUILD_TIMESTAMP = 1758093252
PYTHON_VERSION = """3.10.13 (main, Sep 11 2023, 13:44:35) [GCC 11.2.0]"""
PLATFORM = "Linux xdl-hpc-dev.ea119 4.19.91-009.ali4000.alios7.x86_64 #1 SMP Mon Jan 25 10:47:38 CST 2021 x86_64 x86_64 x86_64 GNU/Linux"
HOSTNAME = "xdl-hpc-dev.ea119"
BUILD_USER = "root"

INTERNAL_VERSION = "0"
TORCH_CUDA_ARCH_LIST = ""
NV_PLATFORM = "0"


def get_version_info():
    """返回完整的版本信息字典"""
    return {
        'version': VERSION,
        'git': {
            'branch': GIT_BRANCH,
            'commit_hash': GIT_COMMIT_HASH,
            'commit_hash_full': GIT_COMMIT_HASH_FULL,
            'commit_time': GIT_COMMIT_TIME,
            'commit_author': GIT_COMMIT_AUTHOR,
            'commit_message': GIT_COMMIT_MESSAGE,
            'tag': GIT_TAG,
        },
        'build': {
            'build_time': BUILD_TIME,
            'build_timestamp': BUILD_TIMESTAMP,
            'python_version': PYTHON_VERSION,
            'platform': PLATFORM,
            'hostname': HOSTNAME,
            'build_user': BUILD_USER,
            'internal_version': INTERNAL_VERSION,
            'torch_cuda_arch_list': TORCH_CUDA_ARCH_LIST,
            'nv_platform': NV_PLATFORM,
        }
    }


def print_version_info():
    """打印版本信息"""
    info = get_version_info()
    print(f"RecIS Version: {info['version']}")
    print(f"Git Branch: {info['git']['branch']}")
    print(f"Git Commit: {info['git']['commit_hash']}")
    print(f"Build Time: {info['build']['build_time']}")
    print(f"Build User: {info['build']['build_user']}")


if __name__ == "__main__":
    print_version_info()
