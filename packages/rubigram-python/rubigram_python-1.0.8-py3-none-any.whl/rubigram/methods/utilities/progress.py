
import sys
import time
from .colors import Colors


class Progress:
    def __init__(self, client=None, object_guid=None):
        self.client = client
        self.object_guid = object_guid
        self.start_time = time.time()
        self.total_size = None
        self.last_uploaded = 0
        self.last_time = self.start_time
        self.msg = None

    async def setup(self):
        if self.client and self.object_guid:
            self.msg = await self.client.send_message(
                self.object_guid,
                "CreateTask.Progress"
            )

    async def __call__(self, total_size: int, uploaded_bytes: int) -> None:
        if self.total_size is None:
            self.total_size = total_size

        now = time.time()
        delta_bytes = uploaded_bytes - self.last_uploaded
        delta_time = now - self.last_time
        speed_bps = delta_bytes / delta_time if delta_time > 0 else 0

        speed_val = speed_bps / (1024 * 1024)
        percent = min(uploaded_bytes / self.total_size * 100, 100)
        current_mb = uploaded_bytes / (1024 ** 2)
        total_mb = self.total_size / (1024 ** 2)
        current_mb = min(current_mb, total_mb)

        percent_str = f"{percent:6.2f}%"
        current_mb_str = f"{current_mb:6.2f}MB"
        total_mb_str = f"{total_mb:.2f}MB"
        tps_str = "TPS"
        speed_str = f"{speed_val:6.2f} Mb/s"

        sys.stdout.write(
            f"\r{percent_str}  [{current_mb_str} / {total_mb_str}]  {tps_str} {speed_str}"
        )
        sys.stdout.flush()

        if self.client and self.object_guid and self.msg:
            await self.client.edit_message(
                self.object_guid,
                self.msg.message_update.message_id,
                f"{percent_str} [{current_mb_str}/{total_mb_str}] {speed_str}"
            )

        self.last_uploaded = uploaded_bytes
        self.last_time = now

        if uploaded_bytes >= self.total_size:
            print()
