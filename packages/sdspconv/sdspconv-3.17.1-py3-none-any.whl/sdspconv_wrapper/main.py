# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------
import os
import sys
import subprocess
import platform

DIR_NAME = "sdspconv-dist"


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    os.environ["EMDT_CONV_ALLOCATOR_PYTHON_EXECUTABLE"] = sys.executable

    folder = os.path.dirname(os.path.abspath(__file__))
    os_type = platform.system()
    if os_type in ["Linux", "Darwin"]:
        sdspconv_script = os.path.abspath(os.path.join(folder, f"./{DIR_NAME}/sdspconv"))
        chmod_x(folder, sdspconv_script)
    elif os_type == "Windows":
        sdspconv_script = os.path.abspath(os.path.join(folder, f"./{DIR_NAME}/sdspconv.bat"))
        # help to handle spaces in paths
        for i in range(len(args)):
            if args[i][0] != '-':
                args[i] = f'"{args[i]}"'
    else:
        raise ValueError("Unsupported operating system")

    str_args = f"{sdspconv_script} {' '.join(args)}"
    result = subprocess.run(str_args, check=False, shell=True)
    return result.returncode


def chmod_x(folder, sdspconv_script):

    def check(path):
        if not os.access(path, os.X_OK):
            os.chmod(path, 0o755)

    check(sdspconv_script)
    dir_path = os.path.join(folder, DIR_NAME)
    for filename in os.listdir(dir_path):
        if filename.endswith(".sh"):
            check(os.path.join(dir_path, filename))


if __name__ == "__main__":
    main()
