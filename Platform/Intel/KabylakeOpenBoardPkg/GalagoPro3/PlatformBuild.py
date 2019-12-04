# @file
# Script to Build UEFI for System 76 GalagoPro3
#
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
import os
import logging

from edk2toolext.environment.uefi_build import UefiBuilder
from edk2toolext.invocables.edk2_platform_build import BuildSettingsManager
from edk2toolext.invocables.edk2_setup import SetupSettingsManager, RequiredSubmodule
from edk2toolext.invocables.edk2_update import UpdateSettingsManager
from edk2toollib.utility_functions import RunPythonScript

    # ####################################################################################### #
    #                                Common Configuration                                     #
    # ####################################################################################### #


class CommonPlatform():
    ''' Common settings for this platform.  Define static data here and use
        for the different parts of stuart
    '''
    WorkspaceRoot = os.path.realpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..\..\..\.."))
    ProductName = "GalagoPro3"
    BoardPackage = "KabylakeOpenBoardPkg"
    ArchSupported = ("IA32", "X64")
    TargetsSupported = ("DEBUG", "RELEASE", "NOOPT")
    Scopes = ('edk2-build', 'intel_silicon_tools', 'intel_fsp', 'openkbl_iasl')

    # ####################################################################################### #
    #                         Configuration for Update & Setup                                #
    # ####################################################################################### #
class SettingsManager(UpdateSettingsManager, SetupSettingsManager):

    def GetPackagesSupported(self):
        ''' return iterable of edk2 packages supported by this build.
        These should be edk2 workspace relative paths '''
        return (CommonPlatform.BoardPackage,)

    def GetArchitecturesSupported(self):
        ''' return iterable of edk2 architectures supported by this build '''
        return CommonPlatform.ArchSupported

    def GetTargetsSupported(self):
        ''' return iterable of edk2 target tags supported by this build '''
        return CommonPlatform.TargetsSupported

    def GetRequiredSubmodules(self):
        ''' return iterable containing RequiredSubmodule objects.
        If no RequiredSubmodules return an empty iterable
        '''
        rs = []
        rs.append(RequiredSubmodule("EDK2", True))
        rs.append(RequiredSubmodule("EDK2-NON-OSI", True))
        rs.append(RequiredSubmodule("Silicon/Intel/FSPs", True))
        return rs

    def SetArchitectures(self, list_of_requested_architectures):
        ''' Confirm the requests architecture list is valid and configure SettingsManager
        to run only the requested architectures.

        Raise Exception if a list_of_requested_architectures is not supported
        '''
        unsupported = set(list_of_requested_architectures) - set(self.GetArchitecturesSupported())
        if(len(unsupported) > 0):
            errorString = ("Unsupported Architecture Requested: " + " ".join(unsupported))
            logging.critical(errorString)
            raise Exception(errorString)
        self.ActualArchitectures = list_of_requested_architectures

    def GetWorkspaceRoot(self):
        ''' get WorkspacePath '''
        return CommonPlatform.WorkspaceRoot

    def GetActiveScopes(self):
        ''' return tuple containing scopes that should be active for this process '''
        return CommonPlatform.Scopes

    # ####################################################################################### #
    #                         Actual Configuration for Platform Build                         #
    # ####################################################################################### #
class PlatformBuilder(UefiBuilder, BuildSettingsManager):
    def __init__(self):
        UefiBuilder.__init__(self)

    def SetPlatformEnv(self):
        logging.debug("PlatformBuilder SetPlatformEnv")

        Project = CommonPlatform.BoardPackage + "/" + CommonPlatform.ProductName
        ActivePlatform = Project + "/OpenBoardPkg.dsc"

        self.env.SetValue("BLD_*_PLATFORM_BOARD_PACKAGE", CommonPlatform.BoardPackage, "Platform Hardcoded")
        self.env.SetValue("PRODUCT_NAME", CommonPlatform.ProductName, "Platform Hardcoded")
        self.env.SetValue("BLD_*_PROJECT", Project, "Platform Hardcoded")
        self.env.SetValue("ACTIVE_PLATFORM", ActivePlatform, "Platform Hardcoded")
        self.env.SetValue("FLASH_MAP_FDF",
                          "Platform/Intel/KabylakeOpenBoardPkg/GalagoPro3/Include/Fdf/FlashMapInclude.fdf",
                          "Platform Hardcoded")
        self.env.SetValue("BIOS_SIZE_OPTION", "SIZE_70", "Platform Hardcoded")
        self.env.SetValue("FSP_WRAPPER_BUILD", "TRUE", "Platform Hardcoded")
        self.env.SetValue("FSP_BINARY_BUILD", "FALSE", "Platform Hardcoded")
        self.env.SetValue("FSP_BINARY_PATH", "Silicon/Intel/FSPS/KabylakeFspBinPkg/", "Platform Hardcoded")
        self.env.SetValue("WORKSPACE_SILICON", "Silicon\Intel\Tools", "Platform Hardcoded")
        self.env.SetValue("WORKSPACE_PLATFORM_BIN", 
                          "edk2-non-osi/Platform/Intel/KabylakeOpenBoardBinPkg",
                          "Platform Hardcoded")
        self.env.SetValue("BIOS_INFO_GUID", "C83BCE0E-6F16-4D3C-8D9F-4D6F5A032929", "Platform Hardcoded")
        self.env.SetValue("TARGET_ARCH", " ".join((CommonPlatform.ArchSupported)), "Platform Hardcoded")
        self.env.SetValue("TOOL_CHAIN_TAG", "VS2017", "Default tool chain")
        self.env.SetValue("BOARD_PKG_PCD_DSC",
                          "KabylakeOpenBoardPkg/GalagoPro3/OpenBoardPkgPcd.dsc",
                          "Platform Hardcoded")
        # JJC HACK: use John's hack to pass PCDs on the commandline
        pcds = " --pcd gIntelFsp2WrapperTokenSpaceGuid.PcdFspModeSelection=1"
        self.env.SetValue("BLD_*_DUMMY_PCDS", "DUMMY" + pcds, "Platorm HardcodedHack") 
        return 0

    def AddCommandLineOptions(self, parserObj):
        ''' Add command line options to the argparser '''
        UefiBuilder.AddCommandLineOptions(self, parserObj)
        parserObj.add_argument('--production', dest="production", action='store_true', default=False)

    def RetrieveCommandLineOptions(self, args):
        '''  Retrieve command line options from the argparser '''
        UefiBuilder.RetrieveCommandLineOptions(self, args)
        self.production = args.production

    def GetWorkspaceRoot(self):
        ''' get WorkspacePath '''
        return CommonPlatform.WorkspaceRoot

    def GetPackagesPath(self):
        ''' Return a list of workspace relative paths that should be mapped as edk2 PackagesPath '''
        paths = [
            'EDK2',
            'Platform\Intel',
            'Silicon\Intel',
            'Silicon\Intel\FSPs',
            'EDK2-NON-OSI\Silicon\Intel',
            'EDK2-NON-OSI\Platform\Intel\KabylakeOpenBoardBinPkg' ########## HACK?  
        ]
        fullPaths = [os.path.join(CommonPlatform.WorkspaceRoot, l) for l in paths]
        return fullPaths

    def GetActiveScopes(self):
        ''' return tuple containing scopes that should be active for this process '''
        return CommonPlatform.Scopes

    def GetName(self):
        ''' Get the name of the repo, platform, or product being build '''
        ''' Used for naming the log file, among others '''
        return CommonPlatform.ProductName  # CommonPlat used because environment not ready when this is called

    def GetLoggingLevel(self, loggerType):
        ''' Get the logging level for a given type
        base == lowest logging level supported
        con  == Screen logging
        txt  == plain text file logging
        md   == markdown file logging
        '''
        return logging.DEBUG

    def PlatformPreBuild(self):
        logging.info("Rebasing FSP")
        # not necessary to delete the old copies like build_bios.py does, the Rebase script overwrites them
        flashMap = os.path.realpath(self.env.GetValue("FLASH_MAP_FDF"))
        fspPath = os.path.realpath(self.env.GetValue("FSP_BINARY_PATH"))
        params = flashMap + " " + fspPath + " Fsp.fd 0x0"
        ret = RunPythonScript("RebaseFspBinBaseAddress.py", params)
        if ret != 0:
            errorString = "RebaseFspBinBaseAddress.py returned failure!"
            logging.critical(errorString)
            raise Exception(errorString)
        # not necessary to concatenate the Rebased FSPs like build_bios.py does, the Rebase script does that
        return ret

#    def PlatformPostBuild(self):
#        return 0
