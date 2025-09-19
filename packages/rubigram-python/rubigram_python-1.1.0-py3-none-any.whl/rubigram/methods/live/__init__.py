
from .add_live_comment import AddLiveComment
from .get_live_comments import GetLiveComments
from .get_live_status import GetLiveStatus
from .set_live_setting import SetLiveSetting
from .send_live import SendLive
from .stop_live import StopLive

class Lives(
    AddLiveComment,
    GetLiveComments,
    GetLiveStatus,
    SetLiveSetting,
    SendLive,
    StopLive
):
    pass
