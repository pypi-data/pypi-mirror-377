from typing import Union
from abc import ABC, abstractmethod


class XenseGripper(ABC):
    
    class ControlMode:
        POSITION: int
        SPEED: int
        SAFE: int

    @abstractmethod
    def set_position(self, position: float, vmax: float , fmax: float):
        pass

    @abstractmethod
    def get_gripper_status(self) -> dict:
        pass
    
    @classmethod
    def create(cls, mac_addr=None, **kwargs) -> Union["XenseTCPGripper", "XenseSerialGripper"]:
        """
        创建一个 XenseGripper 实例，自动选择通信方式（串口或 TCP/IP）

        根据传入参数自动决定使用串口实现（`XenseSerialGripper`）或
        网络实现（`XenseTCPGripper`）创建一个夹爪实例。

        Args:
            mac_addr (str, optional): 如果提供 IP 地址，则使用 TCP 连接到远程夹爪。
                                        否则使用本地串口连接。
            **kwargs: 额外参数（如 `port`），仅在串口连接时使用。

        Returns:
            XenseGripper: 实现 `Gripper` 接口的夹爪实例，具体为串口或 TCP 实现。
        """

class XenseSerialGripper(XenseGripper):
    """
    Direct communication with gripper
    """
    def set_position(self, position, vmax=80.0, fmax=27.0):
        """
        Set the target position of the Gripper.

        Args:
            position (float): Target position of the gripper in millimeters (mm). 
                              Must be in the range (0, 85). 
                              0 mm means fully open, 85 mm means fully closed.
            vmax (float, optional): Maximum speed of motion in mm/s. 
                                    Must be in the range (0, 350). 
                                    Default is 80 mm/s.
            fmax (float, optional): Maximum output force in Newtons (N). 
                                    Must be in the range (0, 60). 
                                    Default is 27 N.

        Raises:
            ValueError: If any of the input arguments are outside their allowed physical limits.

        """

    def get_gripper_status(self) -> dict:
        """Retrieve the gripper status, including motor temperature, output force, speed, and position.

        Returns:
            dict: gripper status including: position, velocity, force and temperature 
        """
    
    
class XenseTCPGripper(XenseGripper):
    """
    Direct communication with gripper
    """
    def set_position(self, position: float, vmax: float = 80.0, fmax: float = 27.0) -> None:
        """
        Set the target position of the Gripper.

        Args:
            position (float): Target position of the gripper in millimeters (mm). 
                              Must be in the range (0, 85). 
                              85 mm means fully open, 0 mm means fully closed.
            vmax (float, optional): Maximum speed of motion in mm/s. 
                                    Must be in the range (0, 350). 
                                    Default is 80 mm/s.
            fmax (float, optional): Maximum output force in Newtons (N). 
                                    Must be in the range (0, 60). 
                                    Default is 27 N.

        Raises:
            ValueError: If any of the input arguments are outside their allowed physical limits.

        """
    def enable_mode(self, mode: 'ControlMode', serial_number: str = None) -> None:
        """
        切换控制模式。
        Args:
            mode (ControlMode): 目标控制模式。
            serial_number (str, optional): SAFE模式下传感器序列号。
        """
        ...

    def disable_mode(self) -> None:
        """
        停止当前控制模式（如停止速度控制或安全控制）。
        """
        ...

    def mode(self, mode: 'ControlMode | str', serial_number: str = None):
        """
        上下文管理器：进入时切换到指定模式，退出时恢复原模式。
        Args:
            mode (ControlMode | str): 目标控制模式。
            serial_number (str, optional): SAFE模式下传感器序列号。
        """
        ...

    def get_gripper_status(self) -> dict:
        """
        Read status from gripper

        Returns:
        - dict, {position, velocity, force, temperature}
        """

    def open_gripper(self) -> None:
        """
        Open Gripper with default v and f.
        """
        ...

    def close_gripper(self) -> None:
        """
        Close Gripper with default v and f.
        """
        ...

    def set_led_color(self, r: int, g: int, b: int) -> None:
        """
        Set the color of the gripper's LED.

        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).
        """
        ...

    def set_speed(self, speed: float) -> None:
        """
        Set the speed of the gripper. Requires SPEED Control Mode.

        Args:
            speed (float): Speed in mm/s. Must be in the range (0, 0).
        """
        ...

    def set_position_sync(self, position: float, vmax: float, fmax: float, tolerance: float = 0.01, timeout: float = 5.0, poll_interval: float = 0.05) -> bool:
        """
        Move the gripper to a target position and block until the target is reached or timeout occurs.

        Args:
            position (float): Target position of the gripper in millimeters (mm).
            vmax (float): Maximum speed of motion in mm/s.
            fmax (float): Maximum output force in Newtons (N).
            tolerance (float, optional): Acceptable error margin to consider the target reached. Default is 0.01 mm.
            timeout (float, optional): Maximum time to wait for the movement to complete, in seconds. Default is 5.0 seconds.
            poll_interval (float, optional): Time interval to check if the target is reached, in seconds. Default is 0.05 seconds.

        Returns:
            bool: True if target reached, False if timeout.
        """
        ...

    def set_control_param(self, stiffness: float = None, kp: float = None, ki: float = None, kd: float = None) -> None:
        """
        Set controller parameters for SAFE mode.

        Args:
            stiffness (float, optional): Target force.
            kp (float, optional): PID Kp.
            ki (float, optional): PID Ki.
            kd (float, optional): PID Kd.
        """
        ...

    def get_control_param(self) -> dict:
        """
        Get controller parameters for SAFE mode.

        Returns:
            dict: Controller parameters including stiffness, kp, ki, kd.
        """
        ...