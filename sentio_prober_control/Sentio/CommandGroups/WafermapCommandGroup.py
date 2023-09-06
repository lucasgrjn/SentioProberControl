from typing import Tuple
from deprecated import deprecated

from sentio_prober_control.Sentio.CommandGroups.ModuleCommandGroupBase import ModuleCommandGroupBase
from sentio_prober_control.Sentio.Response import Response
from sentio_prober_control.Sentio.ProberBase import ProberException
from sentio_prober_control.Sentio.CommandGroups.CommandGroupBase import CommandGroupBase
from sentio_prober_control.Sentio.CommandGroups.WafermapBinsCommandGroup import  WafermapBinsCommandGroup
from sentio_prober_control.Sentio.CommandGroups.WafermapPathCommandGroup import  WafermapPathCommandGroup
from sentio_prober_control.Sentio.CommandGroups.WafermapPoiCommandGroup import  WafermapPoiCommandGroup
from sentio_prober_control.Sentio.CommandGroups.WafermapSubsiteCommandGroup import  WafermapSubsiteGroup
from sentio_prober_control.Sentio.CommandGroups.WafermapCompensationCommandGroup import  WafermapCompensationCommandGroup
from sentio_prober_control.Sentio.CommandGroups.WafermapDieCommandGroup import  WafermapDieCommandGroup
from sentio_prober_control.Sentio.Enumerations import *


class WafermapCommandGroup(ModuleCommandGroupBase):
    """ This class represents the SENTIO command group for wafermap related commands. 
    
        You are not meant to instantiate objects of this class directly! This class
        is instantiated by the prober implementation.

        Example:
        >>> from sentio_prober_control.Sentio.ProberSentio import *
        >>> from sentio_prober_control.Communication.CommunicatorTcpIp import CommunicatorTcpIp
        >>> prober = SentioProber(CommunicatorTcpIp.create("127.0.0.1:35555"))
        >>> prober.map.create(200)
    """

    def __init__(self, comm):
        """ Creates the wafermap command group. 
        
            The wafermap command group contains several other command groups that handle
            aspects of the wafermap and stepping.

            @private
        """
        super().__init__(comm, 'map')
        self.__end_of_route: bool = False

        self.bins : WafermapBinsCommandGroup = WafermapBinsCommandGroup(comm)
        """ A group to set up the binning."""

        self.compensation : WafermapCompensationCommandGroup = WafermapCompensationCommandGroup(comm)
        """ A command group with functions for setting up and executing x,y and z compensation.
            
            .. deprecated:: 23.2 Use VisionCompensationGroup instead
        """

        self.die : WafermapDieCommandGroup = WafermapDieCommandGroup(comm)
        """ A group to set up specific dies on the wafermap (add/remove them)."""

        self.path : WafermapPathCommandGroup = WafermapPathCommandGroup(comm)
        """ A group the handle setting up tests paths. """

        self.poi : WafermapPoiCommandGroup = WafermapPoiCommandGroup(comm)
        """ A group for working with points of interest."""

        self.subsites : WafermapSubsiteGroup = WafermapSubsiteGroup(comm, self)
        """ A group the handle subsites. """


    def bin_step_next_die(self, bin_value: int, site: int = None) -> Tuple[int, int, int]:
        """ Bin the current die and step to the naxt die. 
        
            This command wraps the "map:bin_step_next_die" remote command.

            :param bin_value: The bin value to set for the current die.
            :param site: The subsite index of the next die to move to. Defaults to None. By default the current subsite is retained.
            :raises: ProberException if an error occured.
            :return: A tuple with the column, row and site index representing the position after the step command.
        """
        # 2021-09-17: bugfix: when no site is given current site must be retained
        if site is None:
            self._comm.send(f'map:bin_step_next_die {bin_value}')
        else:
            self._comm.send(f'map:bin_step_next_die {bin_value}, {site}')

        resp = Response.parse_resp(self._comm.read_line())
        self.__end_of_route = (resp.status() & StatusBits.EndOfRoute) == StatusBits.EndOfRoute

        # i.e. Stepping while at the end of the route
        if not resp.ok():
            raise ProberException(resp.message(), resp.errc())

        tok = resp.message().split(",")
        return int(tok[0]), int(tok[1]), int(tok[2])


    def create(self, diameter: float):
        """ Create a new round wafer map. 
        
            Wraps Sentios "map:create" remote command.

            :param diameter: The diameter of the wafer.
            :raises: ProberException if an error occured.            
        """
        self._comm.send(f"map:create {diameter}")
        Response.check_resp(self._comm.read_line())


    def create_rect(self, cols: int, rows: int):
        """ Create a new rectangular wafer map.

            Wraps Sentios "map:create_rect" remote command.

            :param cols: The number of columns.
            :param rows: The number of rows.
            :raises: ProberException if an error occured.
        """
        self._comm.send("map:create_rect {0}, {1}".format(cols, rows))
        Response.check_resp(self._comm.read_line())


    def die_reference_is_set(self) -> bool:
        """ Returns true if the die reference offset is set.
         
            In simple terms the die reference offset is the distance of site 0 from
            the lower left corner of the die. This position defines where
            the die is located with respect to the die in particular and 
            the wafer map grid in extension.

            When the chuck is at site 0 and the probe card is properly in contact
            at the home position, then the die reference offset is the distance between 
            a user defined reference tip of the probe card and the lower left corner 
            of the die.

            Without a properly trained die reference position SENTIO is unable
            to accurately deterine the die coordinates from a chuck position.
            Most of the time this is not a problem. 
            
            When a die reference is trained Sentio will use the die reference offset 
            to calculate the die coordinates of the die which is under the reference 
            tip of the probe card. The reference tip can be any tip of the probe card.

            Wraps Sentios "map:get_prop die_reference_is_set" remote command.

            :raises: ProberException if an error occured.
            :return: True if the die reference offset is set.
        """
        self._comm.send("map:get_prop die_reference_is_set")
        resp = Response.check_resp(self._comm.read_line())
        return resp.message().lower()=='true'


    def end_of_route(self):
        """ Returns True if the last stepping command reached the end of the route. 

            The end of route flag is checked and set by the stepping commands.
            They will evaluate and parse the end of route status from the remote 
            command response and internally set this flag.

            Calling the function is only usefull after a step command was issued.

            :return: True if the last step command reached the end of the route.
        """
        return self.__end_of_route


    def get_axis_orient(self) -> AxisOrient:
        """ Get axis orientation of the wafer map. 
        
            Wraps Sentios "map:get_axis_orient" remote command.

            :raises: ProberException if an error occured.
            :return: The axis orientation.
        """

        self._comm.send("map:get_axis_orient")
        resp = Response.check_resp(self._comm.read_line())

        if resp.message().upper()=="UL":
            return AxisOrient.UpLeft

        if resp.message().upper()=="UR":
            return AxisOrient.UpRight

        if resp.message().upper()=="DR":
            return AxisOrient.DownRight

        if resp.message().upper()=="DL":
            return AxisOrient.DownLeft


    def get_diameter(self) -> float:
        """ Get diameter of the wafer map im millimeter. 
            
            Wraps Sentios "map:get_diameter" remote command.
        
            :raises: ProberException if an error occured.
            :returns: The diameter of the wafer map in millimeter.
        """
        self._comm.send("map:get_diameter")
        resp = Response.check_resp(self._comm.read_line())

        dia = int(resp.message())
        return dia


    def get_die_reference(self) -> Tuple[float, float]:
        """ Get the die reference offset. 
            
            In simple terms the die reference offset is the distance of site 0 from
            the lower left corner of the die. This position defines where
            the die is located with respect to the die in particular and 
            the wafer map grid in extension.

            When the chuck is at site 0 and the probe card is properly in contact
            at the home position, then the die reference offset is the distance between 
            a user defined reference tip of the probe card and the lower left corner 
            of the die.

            Without a properly trained die reference position SENTIO is unable
            to accurately deterine the die coordinates from a chuck position.
            Most of the time this is not a problem. 
            
            When a die reference is trained Sentio will use the die reference offset 
            to calculate the die coordinates of the die which is under the reference 
            tip of the probe card. The reference tip can be any tip of the probe card.

            Wraps SENTIO's "map:get_prop die_reference" remote command.

            :raises: ProberException if an error occured.
            :returns: A tuple with the x and y offset in micrometer. 
        """
        self._comm.send("map:get_prop die_reference")
        resp = Response.check_resp(self._comm.read_line())

        tok = resp.message().split(",")
        return float(tok[0]), float(tok[1])


    def get_die_seq(self) -> int:
        """ Returns the sequence number of the current die. 
        
            The sequence number id the index of the die in the 
            current stepping sequence. The stepping sequence 
            contains the dies selected for test. 
            The sequence number is zero based and is also displayed 
            in the wafermap when zoomin into a die.

            Wraps Sentios "map:get_die_seq" remote command.

            :raises: ProberException if an error occured.
            :return: The sequence number of the current die.
        """
        self._comm.send("map:get_die_seq")
        resp = Response.check_resp(self._comm.read_line())
        return resp.message()  # 0:Result+status, 1:Command ID, 2:Response


    def get_grid_origin(self) -> Tuple[int, int]:
        """ Get origin of the wafermap grid. 

            Wraps Sentios "map:get_grid_origin" remote command.

            :raises: ProberException if an error occured.
            :returns: A tuple with the column and row indices of the origin. 
         """
        self._comm.send("map:get_grid_origin")
        resp = Response.check_resp(self._comm.read_line())
        tok = resp.message().split(",")

        return int(tok[0]), int(tok[1])


    def get_index_size(self) -> Tuple[float, float]:
        """ Return the die size set up in the wafer map.
         
            :raises: ProberException if an error occured.
            :returns: A tuple with the die width and height in micrometer.
         """
        self._comm.send("map:get_index_size")
        resp = Response.check_resp(self._comm.read_line())
        tok = resp.message().split(",")
        return float(tok[0]), float(tok[1])


    def get_num_dies(self, selection: DieNumber) -> int:
        """ Returns the number of dies in the wafer map. 
        
            :param selection: The selection of dies to count.
            :raises: ProberException if an error occured.
            :return: The number of dies.
        """
        switcher = {
            DieNumber.Present: "Present",
            DieNumber.Selected: "Selected"
        }

        what = switcher.get(selection, "Invalid die number selector")

        self._comm.send("map:get_num_dies {0}".format(what))
        resp = Response.check_resp(self._comm.read_line())
        return int(resp.message())


    def get_street_size(self) -> Tuple[int, int]:
        """ Returns the street size set up in the wafer map.
         
            In SENTIO the street size is merely a visual aid. It is not used for 
            any calculations. The only purpose is rendering the diese in a more
            realistic manner.

            :raises: ProberException if an error occured.
            :return: A tuple with the street width and height in micrometer.
        """
        self._comm.send("map:get_street_size")
        resp = Response.check_resp(self._comm.read_line())
        tok = resp.message().split(",")

        return int(tok[0]), int(tok[1])


    def set_axis_orient(self, orient: AxisOrient) -> None:
        """ Set the acis orientation of the custom coordinate system. 
        
            SENTIO's internal coordinate system is placing the origin at the center of the wafer and
            assumes the y-axis is pointing upwards and the x-axis is pointing to the right. With 
            this command you can change the orientation of the coordinate system.

            Wraps Sentios "map:set_axis_orient" remote command.

            :param orient: The axis orientation.
            :raises: ProberException if an error occured.
        """
        self._comm.send(f"map:set_axis_orient {orient.toSentioAbbr()}")
        Response.check_resp(self._comm.read_line())


    def set_color_scheme(self, scheme: ColorScheme) -> None:
        """ Set color scheme of the wafermap.

            The wafermap colorscheme determines how dies are colored.
            The only two options are color from bin or color from value.
            The first one will use the binning table to color the die the second
            one will apply a color scale based on a numeric value associated with 
            the die. (Each die can have a singe temporary numerical value assigned 
            to it.)

            Wraps Sentios "map:set_color_scheme" remote command.

            :param scheme: The color scheme.
            :raises: ProberException if an error occured.
        """
        self._comm.send(f'map:set_color_scheme {scheme.toSentioAbbr()}')
        Response.check_resp(self._comm.read_line())


    def set_flat_params(self, angle: float, width: float):
        """ Set the flat parameters of the wafer map.
         
            Sets the parameters of the flat wafer orientation marker for 
            display in the wafermap.

            :param angle: The angle of the flat in degrees.
            :param width: The width of the flat in micrometer.
            :raises: ProberException if an error occured.
        """
        self._comm.send("map:set_flat_params {0}, {1}".format(angle, width))
        Response.check_resp(self._comm.read_line())


    def set_grid_origin(self, x: int, y: int) -> None:
        """ Set a user defined grid origin.

            SENTIO's internal coordinate system is placing the origin at the center of the wafer and 
            assumes the y-axis is pointing upwards and the x-axis is pointing to the right. You may 
            want to use a custom coordinate system for your wafermap. Coordinates with customized 
            grid origin are referred to as custom coordinates.

            Wraps Sentios "map:set_grid_origin" remote command.

            :param x: The x coordinate of the grid origin in SENTIO's native grid coordinate system.
            :param y: The y coordinate of the grid origin in SENTIO's native grid coordinate system.
            :raises: ProberException if an error occured.
        """
        self._comm.send(f"map:set_grid_origin {x}, {y}")
        Response.check_resp(self._comm.read_line())


    def set_grid_params(self, ix: float, iy: float, offx: float, offy: float, edge: int):
        """ Set wafermap grid parameters. This function defines the wafermapo grid layout which means setting the 
            size of a die. Setting the grid offset and the size of the edge exclusion zone.

            By default SENTIO assumes that the grid is oriented in a way that the center of the wafer
            grid is exactly at the lower left corner of the die located in the center. This would 
            therefore also be the position of site 0.

            It is not recommended to set the grid offset to 0,0 because this may pose problems
            when computing the current die index from a chuck position. Due to inaccuracies in the chuck
            motion the computation may end up in the wrong die because with grid offset of 0,0 
            this position is at the edge of 4 dies.

            It is recommended to either determine the correct value of the die reference offset or
            to use half the die size as grid offset.

            Wraps Sentios "map:set_grid_params" remote command.

            :param ix: The width of a single die in micrometer.  
            :param iy: The height of a single die in micrometer.  
            :param offx: The x offset of the grid in micrometer.  
            :param offy: The y offset of the grid in micrometer.  
            :param edge: The size of the edge exclusion zone in micrometer.
            :raises: ProberException if an error occured.
        """
        self._comm.send("map:set_grid_params {0}, {1}, {2}, {3}, {4}".format(ix, iy, offx, offy, edge))
        Response.check_resp(self._comm.read_line())


    def set_home_die(self, x: int, y: int) -> None:
        """" Sets the home die coordinates in custom coordinates.

            Wraps Sentios "map:set_home_die" remote command. 

            :param x: The x coordinate of the home die in custom coordinates.
            :param y: The y coordinate of the home die in custom coordinates.
            :raises: ProberException if an error occured.     
        """
        self._comm.send(f"map:set_home_die {x}, {y}")
        Response.check_resp(self._comm.read_line())


    def set_index_size(self, x: float, y: float) -> None:
        """ Set the size of a die. 
         
            Wraps Sentios "map:set_index_size" remote command.

            :param x: The width of the die in micrometer.
            :param y: The height of the die in micrometer.
            :raises: ProberException if an error occured.
        """
        self._comm.send("map:set_index_size {0}, {1}".format(x, y))
        Response.check_resp(self._comm.read_line())


    def set_street_size(self, x: float, y: float) -> None:
        """ Set size of streetlines.
         
            In SENTIO the street size is merely a visual aid. It is not used for
            any calculations. The only purpose is rendering the diese in a more
            realistic manner.

            :param x: The width of the street in micrometer.
            :param y: The height of the street in micrometer.
        """
        self._comm.send("map:set_street_size {0}, {1}".format(x, y))
        Response.check_resp(self._comm.read_line())


    def step_die(self, col:int, row:int, site: int = 0) -> Tuple[int, int, int]:
        """ Step to a specific die (or subsite) which is identified by its column, 
            row and subsite number.  

            When the stepping command is issued on the last die of the route, the
            end of route flag is set and can be queried with the end_of_route member function. 

            Wraps Sentios "map:step_die" remote command.

            :param col: The column index of the die. 
            :param row: The row index of the die.
            :param site: The subsite index of the die. Defaults to 0. 
            :raises: ProberException if an error occured.
            :return: A tuple with the column, row and site index representing the position after the step command.
        """
        self._comm.send("map:step_die {0}, {1}, {2}".format(col, row, site))
        resp = Response.parse_resp(self._comm.read_line())

        self.__end_of_route = (resp.status() & StatusBits.EndOfRoute) == StatusBits.EndOfRoute

        if not resp.ok():
            raise ProberException(resp.message(), resp.errc())

        tok = resp.message().split(",")
        return int(tok[0]), int(tok[1]), int(tok[2])


    def step_die_seq(self, seq: int, site: int) -> Tuple[int, int, int]:
        """ Step to a specific die in the stepping sequence.

            Wraps Sentios "map:step_die_seq" remote command.

            :param seq: The sequence number of the die to step to.
            :param site: The subsite index of the die.     
            :raises: ProberException if an error occured.
            :return: A tuple with the column, row and site index representing the position after the step command.
        """

        self._comm.send("map:step_die_seq {}, {}".format(seq, site))
        resp = Response.check_resp(self._comm.read_line())
        tok = resp.message().split(",")

        # i.e. Stepping while at the end of the route
        if not resp.ok():
            raise ProberException(resp.message())

        return int(tok[0]), int(tok[1]), int(tok[2])
    

    def step_first_die(self, site: int=None) -> Tuple[int, int, int]:
        """ Step to the first die in the stepping sequence.

            Wraps Sentios "map:step_first_die" remote command.

            :param site: The subsite index of the die. If omitted SENTIO will step to the first active site.
            :raises: ProberException if an error occured.
            :return: A tuple with the column, row and site index representing the position after the step command.
        """

        if site == None:
            self._comm.send("map:step_first_die")
        else:
            self._comm.send(f"map:step_first_die {site}")
            
        resp = Response.parse_resp(self._comm.read_line())
        
        self.__end_of_route = (resp.status() & StatusBits.EndOfRoute) == StatusBits.EndOfRoute
        
        if not resp.ok():
            raise ProberException(resp.message(), resp.errc())
            
        tok = resp.message().split(",")

        return int(tok[0]), int(tok[1]), int(tok[2])


    def step_next_die(self, site: int = None) -> Tuple[int, int, int]:
        """ Step to the next die in the stepping sequence.
         
            Sentio will stay on the current subsite.

            :raises: ProberException if an error occured.
            :return: A tuple with the column, row and site index representing the position after the step command.
        """

        # 2021-09-17: bugfix: when no site is given current site must be retained
        if site is None:
            self._comm.send(f'map:step_next_die')
        else:
            self._comm.send(f'map:step_next_die {site}')

        resp = Response.parse_resp(self._comm.read_line())
        self.__end_of_route = (resp.status() & StatusBits.EndOfRoute) == StatusBits.EndOfRoute

        # i.e. Stepping while at the end of the route
        if not resp.ok():
            raise ProberException(resp.message(), resp.errc())

        tok = resp.message().split(",")
        return int(tok[0]), int(tok[1]), int(tok[2])


