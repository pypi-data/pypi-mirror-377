from typing import List, Optional, Union, Literal
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class DeviceReadingBase(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __setattr__(self, name, value):
        if name == "timestamp":
            raise TypeError("timestamp is read-only")
        super().__setattr__(name, value)

class RobotPosition(BaseModel):
    amcl_positions: List[float] = Field(..., min_length=3, max_length=3)
    amcl_orientations: List[float] = Field(..., min_length=4, max_length=4)
    odom_pose_positions: List[float] = Field(..., min_length=3, max_length=3)
    odom_pose_orientations: List[float] = Field(..., min_length=4, max_length=4)
    odom_twist_linear: List[float] = Field(..., min_length=3, max_length=3)
    odom_twist_angular: List[float] = Field(..., min_length=3, max_length=3)
    path_positions: List[List[float]] = Field(..., min_length=3, max_length=3)
    path_orientations: List[List[float]] = Field(..., min_length=4, max_length=4)


class RobotData(DeviceReadingBase):
    batery_data: float = Field(..., ge=0, le=100)
    position_data: RobotPosition
    
class Position(BaseModel):
    x: float
    y: float
    z: float
    

class Action(BaseModel):
    name: Literal['ScanObject', 'PickAndPlace', 'Docking', 'Undocking', 'ForcedArmHoming']
    action_id: int
    product_type: Optional[str] = None
    position: Optional[Position] = None
    is_expired: Optional[bool] = False
    
class RobotAction(DeviceReadingBase):
    subtask_id: int
    actions: List[Action]

class Mission(DeviceReadingBase):
    mission: List[RobotAction]
    
class RobotTaskState(DeviceReadingBase):
    state: Literal['IDLE', 'RUNNING', 'FINISHED', 'ABORTED']
    message: str
    
class RobotActionStatus(Enum):
    RECIEVED = 0
    INPROGRESS = 1
    FINISHED = 2
    FAILED = 3

class RobotActionResponse(DeviceReadingBase):
    subtask_id: int
    action_id: int
    status: RobotActionStatus
    log: str
