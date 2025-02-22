from sentio_prober_control.Sentio.CommandGroups.CommandGroupBase import *
from sentio_prober_control.Sentio.CommandGroups.ModuleCommandGroupBase import ModuleCommandGroupBase
from sentio_prober_control.Sentio.Response import *
from sentio_prober_control.Sentio.Enumerations import *


class ServiceCommandGroup(ModuleCommandGroupBase):
    """ A command group for accessing service module functions. """
    
    def __init__(self, comm):
        super().__init__(comm, 'service')


    def set_compensation_mode(self, status: bool) -> Response:
        """ Turn chuck compensation on or off.

            Args:
                status: True to turn on, False to turn off.

            Returns:
                A Response object.
        """

        self._comm.send(f"service:chuck_compensation {status}")
        Response.check_resp(self._comm.read_line())


    def set_software_fence(self, fence: SoftwareFence) -> Response:
        """ Set the software fence.
         
            The software fence is a virtual fence that is used to 
            limit the movement of the chuck. The fences purpose
            is to prevent the chuck from moving into physical 
            obstructions such as the machine casing or other 
            hardware.

            Args:
                fence: The type of fence to use.

            Returns:
                A Response object.
        """

        self._comm.send(f"service:chuck_fence {fence.toSentioArg()}")
        return Response.check_resp(self._comm.read_line())