import pytest

from damru import chrome as chrome_module
from damru.chrome import ChromeManager


class FakeADB:
    def __init__(self, xml_snapshots):
        self.xml_snapshots = list(xml_snapshots)
        self.commands = []

    async def shell(self, command, **kwargs):
        self.commands.append(command)
        if command == "cat /data/local/tmp/damru_ui.xml":
            return self.xml_snapshots.pop(0) if self.xml_snapshots else ""
        return ""


@pytest.mark.asyncio
async def test_dismiss_fre_taps_notification_prompt_before_main_ui_ready(monkeypatch):
    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(chrome_module, "sleep", no_sleep)
    adb = FakeADB([
        '''
        <hierarchy>
          <node resource-id="com.android.chrome:id/compositor_view_holder" bounds="[0,188][954,1936]" />
          <node text="No thanks" resource-id="com.android.chrome:id/negative_button" bounds="[432,1416][579,1508]" />
        </hierarchy>
        ''',
        '''
        <hierarchy>
          <node resource-id="com.android.chrome:id/compositor_view_holder" bounds="[0,188][954,1936]" />
        </hierarchy>
        ''',
    ])

    assert await ChromeManager(adb).dismiss_fre(max_attempts=2) is True

    assert "input tap 505 1462" in adb.commands
