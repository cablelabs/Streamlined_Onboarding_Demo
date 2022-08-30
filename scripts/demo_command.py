#!/usr/bin/env python3
from textual.app import App
from textual.widgets import Header, Footer, ScrollView, Placeholder
from textual.reactive import Reactive
from textual.widget import Widget
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
import subprocess
import libtmux
global cmd,ap
ap=0
cmd=3


class CommandApp(App):
    async def on_load(self) -> None:
        """Sent before going in to application mode."""
        self.server = libtmux.Server()
        self.session = self.server.get_by_id('$0')
        self.window = self.session.attached_window


        # Bind our basic keys
        await self.bind("h", "hostapd", "Restart Hostapd")
        await self.bind("d", "demo", "Restart Demo")
        await self.bind("l", "lamp", "Restart Lamp")
        await self.bind("q", "quit", "Quit")

    async def action_hostapd(self) -> None:
        
        hostap = self.window.select_pane(ap)
        hostap.send_keys('q', enter=True)
        hostap.send_keys('clear', enter=True)
        hostap.send_keys('echo Restarting Hostapd', enter=True)
        hostap.send_keys('sudo service hostapd restart', enter=True)
        hostap.send_keys('sudo /usr/sbin/hostapd_cli -i wlan1', enter=True)
        self.window.select_pane(cmd)

    
    async def action_quit(self) -> None:
        result = subprocess.run(["pkill","-f","tmux"])

    async def on_mount(self) -> None:
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        self.body = ScrollView()



CommandApp.run(title="Demo Command", log="textual.log")
