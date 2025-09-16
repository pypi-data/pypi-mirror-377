import asyncio
import subprocess
from typing import Any, List, Literal, Optional, Union

import numpy as np
from loguru import logger
from piper_sdk import C_PiperInterface_V2

from phosphobot.hardware.base import BaseManipulator
from phosphobot.models import BaseRobotConfig
from phosphobot.models.robot import RobotConfigStatus
from phosphobot.utils import get_resources_path, is_running_on_linux


class PiperHardware(BaseManipulator):
    name = "agilex-piper"
    device_name = "agilex-piper"

    URDF_FILE_PATH = str(
        get_resources_path() / "urdf" / "piper" / "urdf" / "piper.urdf"
    )

    AXIS_ORIENTATION = [0, 0, 0, 1]  # TODO : Verify the axis orientation

    END_EFFECTOR_LINK_INDEX = 5
    GRIPPER_JOINT_INDEX = 6

    SERVO_IDS = [1, 2, 3, 4, 5, 6, 7, 8]

    RESOLUTION = 360 * 1000  # In 0.001 degree

    SLEEP_POSITION = [0, 0, 0, 0, 0, 0]
    CALIBRATION_POSITION = [0, 0, 0, 0, 0, 0]

    is_object_gripped = False
    is_moving = False
    robot_connected = False

    GRIPPER_MAX_ANGLE = 100  # In degree
    ENABLE_GRIPPER = 0x01
    DISABLE_GRIPPER = 0x00

    GRIPPER_SERVO_ID = 7
    # When using the set zero of gripper control, we observe that current position is set to -1800 and not to zero
    GRIPPER_ZERO_POSITION = -1800
    # Strength with which the gripper will close. Similar to the gripping threshold value of other robots,
    GRIPPER_EFFORT = 300

    calibration_max_steps: int = 2

    # Reference: https://github.com/agilexrobotics/piper_sdk/blob/master/asserts/V2/INTERFACE_V2.MD#jointctrl
    #  |joint_name|     limit(rad)     |    limit(angle)    |
    # |----------|     ----------     |     ----------     |
    # |joint1    |   [-2.618, 2.618]  |    [-150.0, 150.0] |
    # |joint2    |   [0, 3.14]        |    [0, 180.0]      |
    # |joint3    |   [-2.967, 0]      |    [-170, 0]       |
    # |joint4    |   [-1.745, 1.745]  |    [-100.0, 100.0] |
    # |joint5    |   [-1.22, 1.22]    |    [-70.0, 70.0]   |
    # |joint6    |   [-2.0944, 2.0944]|    [-120.0, 120.0] |
    piper_limits_rad: dict = {
        1: {"min_angle_limit": -2.618, "max_angle_limit": 2.618},
        2: {"min_angle_limit": 0, "max_angle_limit": 3.14},
        3: {"min_angle_limit": -2.967, "max_angle_limit": 0},
        4: {"min_angle_limit": -1.745, "max_angle_limit": 1.745},
        5: {"min_angle_limit": -1.22, "max_angle_limit": 1.22},
        6: {"min_angle_limit": -2.0944, "max_angle_limit": 2.0944},
    }
    piper_limits_degrees: dict = {
        1: {"min_angle_limit": -150.0, "max_angle_limit": 150.0},
        2: {"min_angle_limit": 0, "max_angle_limit": 180.0},
        3: {"min_angle_limit": -170, "max_angle_limit": 0},
        4: {"min_angle_limit": -100.0, "max_angle_limit": 100.0},
        5: {"min_angle_limit": -70.0, "max_angle_limit": 70.0},
        6: {"min_angle_limit": -120.0, "max_angle_limit": 120.0},
    }

    def __init__(
        self,
        can_name: str = "can0",
        only_simulation: bool = False,
        axis: Optional[List[float]] = None,
    ) -> None:
        self.can_name = can_name
        super().__init__(only_simulation=only_simulation, axis=axis)
        self.SERIAL_ID = can_name
        self.is_torqued = False

    @classmethod
    def from_can_port(cls, can_name: str = "can0") -> Optional["PiperHardware"]:
        try:
            piper = cls(can_name=can_name)
            return piper
        except Exception as e:
            logger.warning(e)
            return None

    async def connect(self) -> None:
        """
        Setup the robot.
        can_number : 0 if only one robot is connected, 1 to connect to second robot
        """
        self.is_connected = False

        logger.info(f"Connecting to Agilex Piper on {self.can_name}")

        if not is_running_on_linux():
            logger.warning("Robot can only be connected on a Linux machine.")
            return

        try:
            proc = subprocess.Popen(
                ["bash", str(get_resources_path() / "agilex_can_activate.sh")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if proc.stdout is None or proc.stderr is None:
                logger.error("Failed to start the CAN activation script.")
                return

            # Example: read lines one by one, log them
            for line in proc.stdout:
                logger.debug("[can-script] " + line.rstrip())

            for line in proc.stderr:
                logger.error("[can-script] " + line.rstrip())

            proc.wait(timeout=10)
            if proc.returncode != 0:
                logger.error("Script exited with %d", proc.returncode)
                return
        except subprocess.CalledProcessError as e:
            logger.warning(
                f"CAN Activation Failed!\nError: {e}\nOutput:\n{e.stdout}\nErrors:\n{e.stderr}"
            )
            return

        logger.debug(f"Attempting to connect to Agilex Piper on {self.can_name}")
        self.motors_bus = C_PiperInterface_V2(
            can_name=self.can_name, judge_flag=True, can_auto_init=True
        )
        await asyncio.sleep(0.1)
        # Check if CAN bus is OK
        is_ok = self.motors_bus.isOk()
        if not is_ok:
            logger.debug(
                f"Could not connect to Agilex Piper on {self.can_name}: CAN bus is not OK."
            )
            return

        self.motors_bus.ConnectPort(can_init=True)
        await asyncio.sleep(0.1)
        self.motors_bus.ArmParamEnquiryAndConfig(
            param_setting=0x01,
            # data_feedback_0x48x=0x02,
            end_load_param_setting_effective=0,
            set_end_load=0x0,
        )
        await asyncio.sleep(0.1)
        # First, start standby mode (ctrl_mode=0x00). Then, switch to CAN command control mode (ctrl_mode=0x01)
        # Source: https://static.generation-robots.com/media/agilex-piper-user-manual.pdf
        self.motors_bus.MotionCtrl_2(
            ctrl_mode=0x00, move_mode=0x01, move_spd_rate_ctrl=100, is_mit_mode=0x00
        )
        await asyncio.sleep(0.1)
        self.motors_bus.MotionCtrl_2(
            ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=100, is_mit_mode=0x00
        )
        await asyncio.sleep(0.2)

        self.is_connected = True
        self.init_config()

    def get_default_base_robot_config(
        self, voltage: str, raise_if_none: bool = False
    ) -> Union[BaseRobotConfig, None]:
        return BaseRobotConfig(
            name=self.name,
            servos_voltage=12.0,
            servos_offsets=[0] * len(self.SERVO_IDS),
            servos_calibration_position=[1e-6] * len(self.SERVO_IDS),
            servos_offsets_signs=[1] * len(self.SERVO_IDS),
            gripping_threshold=4500,
            non_gripping_threshold=500,
        )

    def disconnect(self) -> None:
        """
        Disconnect the robot.
        """

        if not self.is_connected:
            return

        self.motors_bus.DisconnectPort()
        self.is_connected = False

    def init_config(self) -> None:
        """
        Load the config file.
        """
        self.config = BaseRobotConfig(
            name=self.name,
            servos_voltage=12.0,
            servos_offsets=[0] * len(self.SERVO_IDS),
            servos_offsets_signs=[1] * len(self.SERVO_IDS),
            servos_calibration_position=[1e-6] * len(self.SERVO_IDS),
            gripping_threshold=1000,
            non_gripping_threshold=10,
        )

    def enable_torque(self) -> None:
        if not self.is_connected:
            return
        self.motors_bus.EnablePiper()
        self.is_torqued = True

    def disable_torque(self) -> None:
        # Disable torque
        if not self.is_connected:
            return
        self.motors_bus.DisableArm(7)
        # Disable the gripper with no change of zero position
        self.motors_bus.GripperCtrl(0, self.GRIPPER_EFFORT, self.DISABLE_GRIPPER, 0)
        self.is_torqued = False

    def read_motor_torque(self, servo_id: int) -> Optional[float]:
        """
        Read the torque of a motor

        raise: Exception if the routine has not been implemented
        """
        if servo_id >= self.GRIPPER_SERVO_ID or servo_id < 1:
            gripper_state = self.motors_bus.GetArmGripperMsgs().gripper_state
            return gripper_state.grippers_effort
        else:
            return 100 if self.is_torqued else 0

    def read_motor_voltage(self, servo_id: int) -> Optional[float]:
        """
        Read the voltage of a motor

        raise: Exception if the routine has not been implemented
        """
        # Not implemented
        return None

    def write_motor_position(self, servo_id: int, units: int, **kwargs: Any) -> None:
        """
        Move the motor to the specified position.

        Args:
            servo_id: The ID of the motor to move.
            units: The position to move the motor to. This is in the range 0 -> (self.RESOLUTION -1).
        Each position is mapped to an angle.
        """
        # If servo_id is 7 (gripper), write the gripper command
        if servo_id == self.GRIPPER_SERVO_ID:
            self.write_gripper_command(units)
            return

        # Otherwise, we need to write the position to the motor. We can only write all motors at once.
        current_position = self.read_joints_position(unit="motor_units", source="robot")
        # The last position is the gripper, so we drop it
        current_position = current_position[:-1]

        # Override the position of the specified servo_id
        current_position[servo_id - 1] = units

        logger.debug(f"Piper: Moving servo {servo_id} to position {units}")
        # Clamp the position in the allowed range for the motors using self.piper_limits
        logger.debug(
            f"Piper: Clipping position {servo_id} to {self.piper_limits_degrees[servo_id]}"
        )
        if servo_id in self.piper_limits_degrees:
            min_limit = self.piper_limits_degrees[servo_id]["min_angle_limit"] * 1000
            max_limit = self.piper_limits_degrees[servo_id]["max_angle_limit"] * 1000
            current_position[servo_id - 1] = np.clip(
                current_position[servo_id - 1], min_limit, max_limit
            )

        # Move robot
        self.motors_bus.ModeCtrl(
            ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=100, is_mit_mode=0x00
        )
        self.joint_position = current_position.tolist()
        self.motors_bus.JointCtrl(*[int(q) for q in current_position])

    def write_group_motor_position(
        self, q_target: np.ndarray, enable_gripper: bool
    ) -> None:
        # First 6 values of q_target are the joints position.
        # Clamp joints in the allowed range for the motors using self.piper_limits_degrees * 1000
        clamped_joints = []
        for i, joint in enumerate(q_target):
            # in self.piper_limits_degrees, there are only indexes 1 to 6
            servo_id = i + 1
            if servo_id in self.piper_limits_degrees:
                min_limit = self.piper_limits_degrees[i + 1]["min_angle_limit"] * 1000
                max_limit = self.piper_limits_degrees[i + 1]["max_angle_limit"] * 1000
                # q_target[i] = np.clip(joint, min_limit, max_limit)  # noqa: F821
                clamped_joints.append(int(np.clip(joint, min_limit, max_limit)))

        self.motors_bus.ModeCtrl(
            ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=100, is_mit_mode=0x00
        )
        self.motors_bus.JointCtrl(*clamped_joints)

        # Move the gripper if it is enabled
        if enable_gripper and len(q_target) >= self.GRIPPER_SERVO_ID:
            self.write_gripper_command(q_target[-1])

    def read_motor_position(self, servo_id: int, **kwargs: Any) -> Optional[int]:
        """
        Read the position of the motor. This should return the position in motor units.
        """
        return self.read_group_motor_position()[servo_id - 1]

    def read_joints_position(
        self,
        unit: Literal["rad", "motor_units", "degrees", "other"] = "rad",
        source: Literal["sim", "robot"] = "robot",
        joints_ids: Optional[List[int]] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> np.ndarray:
        """
        Read the position of the joints. This should return the position in motor units.
        """
        # The parent method reads the joints, but not the gripper.
        joints = super().read_joints_position(
            unit=unit,
            source=source,
            joints_ids=joints_ids,
            min_value=min_value,
            max_value=max_value,
        )

        # Add the gripper position if it is not already present
        if len(joints) < self.GRIPPER_SERVO_ID and (
            joints_ids is None or self.GRIPPER_SERVO_ID in joints_ids
        ):
            gripper_position = self.read_gripper_command(
                source=source, unit=unit, min_value=min_value, max_value=max_value
            )

            joints = np.array(joints.tolist() + [gripper_position]).astype(np.float32)
        return joints

    def read_group_motor_position(self) -> np.ndarray:
        """
        Read the position of all the motors. This should return the position in motor units.
        """
        joint_state = self.motors_bus.GetArmJointMsgs().joint_state
        # in 0.001 deg
        position_unit = np.array(
            [
                joint_state.joint_1,
                joint_state.joint_2,
                joint_state.joint_3,
                joint_state.joint_4,
                joint_state.joint_5,
                joint_state.joint_6,
            ]
        )

        return position_unit

    def calibrate_motors(self, **kwargs: Any) -> None:
        """
        This is called during the calibration phase of the robot.
        It sets the offset of all motors to self.RESOLUTION/2.
        """
        # Set zero positions for motors and gripper
        self.motors_bus.JointConfig(set_zero=0xAE)  # Set zero position of motors
        # Set zero position of gripper
        self.motors_bus.GripperCtrl(0, self.GRIPPER_EFFORT, 0x00, 0xAE)

    def _units_vec_to_radians(self, units: np.ndarray) -> np.ndarray:
        """
        Convert from motor discrete units (0 -> RESOLUTION) to radians
        """
        position_deg = units * 2 * np.pi / self.RESOLUTION  # in 0.001 deg
        return position_deg  # in deg

    def _radians_to_units_vec(self, radians: np.ndarray) -> np.ndarray:
        """
        Convert from radians to motor discrete units (0 -> RESOLUTION)
        """
        position_deg = self.RESOLUTION * radians / (2 * np.pi)
        return position_deg.astype(int)

    async def calibrate(self) -> tuple[Literal["success", "in_progress", "error"], str]:
        """
        This is called during the calibration phase of the robot.
        CAUTION :
        Set the robot in a sleep mode where falling wont be an issue and close the gripper.
        """
        if not self.is_connected:
            logger.warning("Robot is not connected. Cannot calibrate.")
            return "error", "Robot is not connected. Cannot calibrate."

        if self.calibration_current_step == 0:
            self.calibration_current_step = 1
            return (
                "in_progress",
                "STEP 1/3: NEXT STEP, THE ROBOT WILL FALL. HOLD THE ROBOT to prevent it from falling.",
            )
        elif self.calibration_current_step == 1:
            self.disable_torque()
            self.calibration_current_step = 2
            return (
                "in_progress",
                "STEP 2/3: Move the robot to its sleep position. Close the gripper fully.",
            )
        elif self.calibration_current_step == 2:
            self.calibration_current_step = 0
            self.calibrate_motors()
            self.enable_torque()
            return (
                "success",
                "STEP 3/3: Calibration completed successfully. Offsets and signs saved to the robot.",
            )

        return (
            "error",
            "Calibration failed. Please try again.",
        )

    def read_gripper_command(
        self,
        source: Literal["sim", "robot"] = "robot",
        unit: Literal["motor_units", "rad", "degrees", "other"] = "motor_units",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> float:
        """
        Read if gripper is open or closed.
        """

        if not self.is_connected:
            logger.warning("Robot not connected")
            return 0

        if source == "robot":
            gripper_ctrl = self.motors_bus.GetArmGripperMsgs().gripper_state
            gripper_position = gripper_ctrl.grippers_angle
        elif source == "sim":
            raise NotImplementedError(
                "Reading gripper command from simulation is not implemented for Piper."
            )
        else:
            raise ValueError(f"Unknown source: {source}")

        # Calculate normalized gripper position [0, 1]
        normalized = (gripper_position - self.GRIPPER_ZERO_POSITION) / (
            self.GRIPPER_MAX_ANGLE * 1000
        )

        if unit == "motor_units":
            # Don't do anything
            pass
        elif unit == "rad":
            # Convert the gripper from (0, GRIPPER_MAX_ANGLE) to (0, pi / 2)
            gripper_units = normalized * (np.pi / 2)
        elif unit == "degrees":
            # Convert the gripper from (0, GRIPPER_MAX_ANGLE) to (0, 90)
            gripper_units = normalized * 90
        elif unit == "other":
            # Convert the gripper from (0, GRIPPER_MAX_ANGLE) to (min_value, max_value)
            if min_value is None or max_value is None:
                raise ValueError(
                    "min_value and max_value must be provided for 'other' unit."
                )
            gripper_units = normalized * (max_value - min_value) + min_value
        else:
            raise ValueError(f"Unknown unit: {unit}")

        logger.debug(
            f"Piper: Converted gripper position {gripper_position} to {gripper_units} in {unit}"
        )
        return gripper_units

    def _rad_to_open_command(self, radians: float) -> float:
        """
        Convert radians to an open command for the gripper.
        The open command is in the range [0, 1], where 0 is fully closed and 1 is fully open.
        """
        # Clip to valid range and normalize to [0, 1]
        clipped_radians = np.clip(radians, 0, np.pi / 2)  # Max 90 degrees (π/2 rad)
        open_command = clipped_radians / (np.pi / 2)  # Normalize to [0, 1]
        logger.debug(
            f"Piper: Converting radians {radians} to open command {open_command}"
        )
        return open_command

    def write_gripper_command(self, command: float) -> None:
        """
        Open or close the gripper.

        command: 0 to close, 1 to open
        """
        if not self.is_connected:
            logger.debug("Robot not connected, cannot write gripper command")
            return
        # Gripper -> Convert from 0->RESOLUTION to 0->GRIPPER_MAX_ANGLE
        logger.debug(f"Piper: Writing gripper command {command}")
        unit_degree = command * self.GRIPPER_MAX_ANGLE
        unit_command = self.GRIPPER_ZERO_POSITION + int(unit_degree * 1000)
        self.motors_bus.GripperCtrl(
            gripper_angle=unit_command,
            gripper_effort=self.GRIPPER_EFFORT,
            gripper_code=self.ENABLE_GRIPPER,
            set_zero=0,
        )
        self.update_object_gripping_status()

    def is_powered_on(self) -> bool:
        """
        Check if the robot is powered on.
        """
        return self.is_connected

    def status(self) -> RobotConfigStatus:
        """
        Get the status of the robot.

        Returns:
            RobotConfigStatus object
        """
        return RobotConfigStatus(
            name=self.name, device_name=self.can_name, robot_type="manipulator"
        )
