# @file
# Script to Build KBL RVP3 UEFI firmware
#
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
import os
import logging

from edk2toolext.environment import shell_environment
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
    ProductName = "KblRvp3"
    BoardPackage = "KabylakeOpenBoardPkg"
    Project = "KabylakeRvp3"
    Platform = "OpenBoardPkg.dsc"
    PackagesSupported = (BoardPackage,)
    ArchSupported = ("IA32", "X64")
    TargetsSupported = ("DEBUG", "RELEASE", "NOOPT")
    Scopes = ('edk2-build','kbl','intel_fsp')
    FspBinPath = "Silicon/Intel/FSPS/AmberLakeFspBinPkg/"
    FspRebaseScript = os.path.join("Platform","Intel","MinPlatformPkg","Tools","Fsp","RebaseFspBinBaseAddress.py")
    FlashMap = os.path.join("Platform","Intel",BoardPackage,Project,
                            "Include","Fdf","FlashMapInclude.fdf")


    # ####################################################################################### #
    #                         Configuration for Update & Setup                                #
    # ####################################################################################### #
class SettingsManager(UpdateSettingsManager, SetupSettingsManager):

    def GetPackagesSupported(self):
        ''' return iterable of edk2 packages supported by this build.
        These should be edk2 workspace relative paths '''
        return CommonPlatform.PackagesSupported

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
        rs.append(RequiredSubmodule(
            "EDK2", True))
        return rs

    def SetArchitectures(self, list_of_requested_architectures):
        ''' Confirm the requests architecture list is valid and configure SettingsManager
        to run only the requested architectures.

        Raise Exception if a list_of_requested_architectures is not supported
        '''
        unsupported = set(list_of_requested_architectures) - set(self.GetArchitecturesSupported())
        if(len(unsupported) > 0):
            errorString = ( "Unsupported Architecture Requested: " + " ".join(unsupported))
            logging.critical( errorString )
            raise Exception( errorString )
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
class PlatformBuilder( UefiBuilder, BuildSettingsManager):
    def __init__(self):
        UefiBuilder.__init__(self)

    def SetPlatformEnv(self):
        logging.debug("PlatformBuilder SetPlatformEnv")
        Project = "/".join((CommonPlatform.BoardPackage,CommonPlatform.Project))
        Platform = "/".join((Project,CommonPlatform.Platform))
        self.env.SetValue("PRODUCT_NAME",                 CommonPlatform.ProductName,             "Platform Hardcoded")
        self.env.SetValue("TARGET_ARCH",                  " ".join((CommonPlatform.ArchSupported)), "Platform Hardcoded")
        self.env.SetValue("BLD_*_PLATFORM_BOARD_PACKAGE", CommonPlatform.BoardPackage,            "Platform Hardcoded")
        self.env.SetValue("BLD_*_PROJECT",                Project,                                "Platform Hardcoded")
        self.env.SetValue("ACTIVE_PLATFORM",              Platform,                               "Platform Hardcoded")
        self.env.SetValue("FSP_BINARY_PATH",              CommonPlatform.FspBinPath,              "Platform Hardcoded")
        self.env.SetValue("TOOL_CHAIN_TAG",               "VS2017",                               "Default tool chain")
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
            'EDK2-NON-OSI\Silicon\Intel'
            ]
        fullPaths = [ os.path.join(CommonPlatform.WorkspaceRoot, l) for l in paths ] 
        return fullPaths

    def GetActiveScopes(self):
        ''' return tuple containing scopes that should be active for this process '''
        return CommonPlatform.Scopes

    def GetName(self):
        ''' Get the name of the repo, platform, or product being build '''
        ''' Used for naming the log file, among others '''
        return CommonPlatform.ProductName

    def GetLoggingLevel(self, loggerType):
        ''' Get the logging level for a given type
        base == lowest logging level supported
        con  == Screen logging
        txt  == plain text file logging
        md   == markdown file logging
        '''
        return logging.DEBUG

    def PlatformPreBuild(self):
        params = " ".join((CommonPlatform.FlashMap, CommonPlatform.FspBinPath, "Fsp.fd", "0x0"))
        ret = RunPythonScript( CommonPlatform.FspRebaseScript, params)
        return ret

    def PlatformPostBuild(self):
        return 0
