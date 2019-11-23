# Pytools for Intel Platforms

## Prerequisites

* [Python 3.x is installed](https://www.python.org/downloads/)
* [git is installed/configured](https://git-scm.com/download/)
* EDK2-compatible compiler is installed.  This example was tested with the free [Visual Studio 2017 Build Tools](https://microsoft.github.io/mu/CodeDevelopment/prerequisites/#visual-studio-2017)

## Setup Description (example to follow)

* Clone `https://github.com/out0xb2/edk2-platforms.git` and checkout "feature/py_platforms"
* Consider creating & using a [Python Virtual Environment](https://docs.python.org/3/library/venv.html) ([Example](https://microsoft.github.io/mu/CodeDevelopment/prerequisites/#workspace-virtual-environment-setup-process))
* Install Edk2-Pytools
  * `pip install -r Platform\Intel\KabylakeOpenBoardPkg\pip-requirements.txt`
* Ask Stuart (edk2-pytools) to perform initialization of your workspace.  
  * For the KabylakeRvp3:
    * `stuart_setup -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py`
    * This initializes required submodules and platform dependencies such as iASL and NASM, note that manual install & setup of NASM and iASL is __not__ required
    * `stuart_update -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py`
    * This initializes the Pytools External Dependencies
* Build BaseTools using "`python EDK2\BaseTools\Edk2ToolsBuild.py [-t <ToolChainTag>]`"
  * This replaces "`edksetup Rebuild`" from the classic build system
  * If you see an exception, such as FileNotFoundError, then you should specify a working ToolChainTag.  This should print a green `PROGRESS - Success`
  * For Windows `<ToolChainTag>` examples, refer to [Windows ToolChain Matrix](https://github.com/tianocore/tianocore.github.io/wiki/Windows-systems-ToolChain-Matrix), defaults to `VS2017` if not specified

### Setup Example

```
git clone https://github.com/out0xb2/edk2-platforms.git edk2-platforms-pytools -b feature/py_platforms
python -m venv venv_edk2-pytools
venv_edk2-pytools\Scripts\activate
cd edk2-platforms-pytools
pip install -r Platform\Intel\KabylakeOpenBoardPkg\pip-requirements.txt
stuart_setup -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py
stuart_update -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py
python EDK2\BaseTools\Edk2ToolsBuild.py -t VS2017
```

## Building

First set the `TOOL_CHAIN_TAG` environment variable or pass it on the commandlines below using "`TOOL_CHAIN_TAG=<value>`" syntax.

`stuart_build -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py`

## Re-Initialize & Update Submodules & Dependencies (when they change)

```
stuart_setup -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py
stuart_update -c Platform\Intel\KabylakeOpenBoardPkg\KabylakeRvp3\PlatformBuild.py
```

NOTE: do this every time you change the Pytools dependencies or pull (which may bring dependency changes)

## Enablement Notes

* Platform/Intel/KabylakeOpenBoardPkg/KabylakeRvp3/PlatformBuild.py Platform Builder
  * Top-level build file defines the platform-specific build configuration
  * Specifies submodule dependencies (consumed by stuart_setup)
    * Versions are pinned via .gitmodules
  * Specifies "scopes" to activate matching Pytools plug-ins and dependencies (consumed by stuart_update)
  * Specifies build environment that is consumed by stuart_build
* Platform/Intel/KabylakeOpenBoardPkg/iasl_ext_dep.yaml
  * Defines a dependency on your *preferred* version of iASL
  * Placed at Board Package level with the intention of sharing across all Kbl Open Board projects
  * scope: 'openkbl_iasl'
* Platform/Intel/MinPlatformPkg/Tools/Fsp/fsp_tools_path_env.json Path Environment
  * Adds Platform/Intel/MinPlatformPkg/Tools/Fsp/ to the path during build
  * scope: 'intel_fsp'
* EDK2/IntelFsp2Pkg/Tools/fsp_tools_path_env.json Path Environment
  * Adds EDK2/IntelFsp2Pkg/Tools/ to the path during build
  * scope: 'intel_fsp'

### Intel Silicon Tools Plug-in

* Silicon/Intel/Tools/Tools_plug_in.yaml
  * Declares the Intel Silicon Tools build plug-in
  * scope: 'intel_silicon_tools'
* Silicon/Intel/Tools/IntelSiliconTools.py
  * The Intel Silicon Tools plug-in implementation
  * During Pre-build it makes all Intel Silicon Tools (e.g. FitGen)
  * During Post-build it invokes FitGen

#### DSC Modifications

* Some modifications made to workaround PyTool issue [#47: DSC parser does not handle conditionals](https://github.com/tianocore/edk2-pytool-library/issues/47)

## References

[Using Pytools](https://github.com/tianocore/edk2-pytool-extensions/blob/master/docs/using.md)
