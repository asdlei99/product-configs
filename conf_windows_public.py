# Copyright (c) 2019 Intel Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

PRODUCT_REPOS = [
    {'name': 'MediaSDK'},
    # Give possibility to build windows for changes from product configs repository
    {'name': 'product-configs'}
]

BUILD_ENVIRONMENT = {
    'INTELMEDIASDKROOT': str(options['REPOS_DIR'] / 'MediaSDK' / 'api'),
    'MINIDDK_ROOT': r'C:\Program Files (x86)\Windows Kits\10',
    'MINIDDK_VERSION': '10.0.17134.0',
    'MSBuildEmitSolution': '1'
}

MSBUILD_ARGUMENTS = {
    '/target': 'Build',
    '/verbosity': 'minimal',
    '/maxcpucount': options['CPU_CORES']
}

def clean_msbuild_dirs(repos_dir):
    import shutil

    build_dir = repos_dir / 'build'
    if build_dir.exists():
        log.info('remove directory %s', build_dir)
        shutil.rmtree(build_dir)

action(
    'Clean msbuild dirs',
    stage=stage.CLEAN,
    callfunc=(clean_msbuild_dirs, [options['REPOS_DIR']], {})
)

for platform in ['x64', 'Win32']:
    # TODO: Release and/or Debug configurations should be previded by build scripts
    for configuration in ['Release', 'Debug']:
        vs_component(
            f"Build dispatcher (2017) {platform}",
            solution_path=options['REPOS_DIR'] / r'MediaSDK\api\mfx_dispatch\windows\libmfx_vs2015.sln',
            msbuild_args={
                '/property': {
                    'Platform': platform,
                    'Configuration': configuration
                }
            },
            env=BUILD_ENVIRONMENT
        )

        install_package_file_suffixes = ['.lib', '.pdb']
        if configuration == 'Debug':
            install_package_file_suffixes.append('.idb')

        # TODO: release and debug install packages should be separated
        for suffix in install_package_file_suffixes:
            INSTALL_PKG_DATA_TO_ARCHIVE.append({
                'from_path': options['REPOS_DIR'] / 'build',
                'relative': [
                    {
                        'path': rf'win_{platform}\lib\libmfx_vs2015{"" if configuration == "Release" else "_d"}{suffix}'
                    }
            ]})

    DEV_PKG_DATA_TO_ARCHIVE.extend([{
        'from_path': options['REPOS_DIR'] / 'build',
        'relative': [
            {
                'path': rf'win_{platform}'
            }
        ]
    }])
