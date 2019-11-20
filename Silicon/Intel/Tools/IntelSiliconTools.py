import logging
import os
import builtins
import struct

from edk2toolext.environment.plugintypes.uefi_build_plugin import IUefiBuildPlugin
import edk2toollib.windows.locate_tools as locate_tools
from edk2toolext.environment import shell_environment
from edk2toollib.utility_functions import RunCmd

class IntelSiliconTools(IUefiBuildPlugin):
    '''
    Builds the Intel Silicon Tools.  
    This script assumes it is in the same directory as the Intel Silicon Tools makefile

    Environment:
        If "BIOS_INFO_GUID" is set, FitGen will be called to generate a FIT table containing the GUID

    '''


    ##
    # Run Pre Build Operations
    #
    # @param thebuilder - UefiBuild object to get env information
    #
    # @return 0 for success NonZero for error.
    ##
    def do_pre_build(self, thebuilder):
        logging.info("PreBuild: Building the Intel Silicon Tools")

        shell_environment.CheckpointBuildVars()  # save/push current environment

        interesting_keys = ["ExtensionSdkDir", "INCLUDE", "LIB", "LIBPATH", "UniversalCRTSdkDir",
                            "UCRTVersion", "WindowsLibPath", "WindowsSdkBinPath", "WindowsSdkDir", "WindowsSdkVerBinPath",
                            "WindowsSDKVersion","VCToolsInstallDir","PATH"]
        vs_vars = locate_tools.QueryVcVariables(interesting_keys, "x86")
        for (k,v) in vs_vars.items():
            if k.upper() == "PATH":
                shell_environment.GetEnvironment().append_path(v)
            else:
                shell_environment.GetEnvironment().set_shell_var(k, v)

        workingdir = os.path.dirname(__file__)
        ret = RunCmd('nmake.exe', "", workingdir = workingdir)

        shell_environment.RevertBuildVars()  # restore/pop the original environment

        return ret


    ##
    # Run Post Build Operations
    #
    # @param thebuilder - UefiBuild object to get env information
    #
    # @return 0 for success NonZero for error.
    ##
    def do_post_build(self, thebuilder):

        BiosInfoGuid = thebuilder.env.GetValue("BIOS_INFO_GUID")
        if BiosInfoGuid is None:
            logging.info("BIOS_INFO_GUID not supplied, skipping FIT generation")
            ret = 0
        else:
            logging.info("Generating FIT...")

            fdFinal = os.path.join(thebuilder.env.GetValue("BUILD_OUTPUT_BASE"), "FV", thebuilder.env.GetValue("BOARD").upper() + ".fd")
            fdTemp  = os.path.join(thebuilder.env.GetValue("BUILD_OUTPUT_BASE"), "FV", "Temp.fd")
            logging.debug("fdFinal: " + fdFinal + "\n" + "fdTemp: " + fdTemp)

            params = "-D " + fdFinal + " " + fdTemp + " -NA -I " + BiosInfoGuid
            ret = RunCmd('FitGen.exe', params)

            if ret != 0:
                logging.critical("FitGen returned: " + ret)
            return ret
            
        return ret