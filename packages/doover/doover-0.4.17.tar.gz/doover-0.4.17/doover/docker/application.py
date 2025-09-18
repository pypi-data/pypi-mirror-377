import asyncio
import argparse
import json
import os
import logging
import time
from collections import deque

from datetime import datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING, Awaitable, Callable

try:
    from aiohttp.web import Response, Server, ServerRunner, TCPSite
except ImportError:
    RUN_HEALTHCHECK = False
else:
    RUN_HEALTHCHECK = True

from .device_agent import DeviceAgentInterface
from .modbus import ModbusInterface
from .platform import PlatformInterface

from ..ui import UIManager
from ..utils import (
    call_maybe_async,
    get_is_async,
    maybe_async,
    setup_logging as utils_setup_logging,
    apply_diff,
    generate_diff,
)

if TYPE_CHECKING:
    from ..config import Schema

log = logging.getLogger(__name__)

MaybeAsyncMainLoopMethod = Callable[[], Awaitable[None]] | Callable[[], None]

TAG_CLOUD_MAX_AGE = 60 * 60  # 1 hour
TAG_CHANNEL_NAME = "tag_values"


class Application:
    """Base class for a Doover application. All apps will inherit from this class, and override the setup and main_loop methods.

    You generally don't need to worry about initiating parameters to this class as that will be done through `run_app`.

    Examples
    --------

    The following is an incredibly simple example of a Doover application that shows how to initiate this Application class.
    However, in practice, it is suggested to use the template application repository for a more structured, complex scaffold
    for building apps.

    A basic application::

        from pydoover.docker import Application, run_app
        from pydoover.config import Schema

        class MyApp(Application):
            def setup(self):
                self.set_tag("my_app_ready", True)

            def main_loop(self):
                # Your main loop logic here
                pass

        if __name__ == "__main__":
            run_app(MyApp(config=Schema()))


    Attributes
    ----------
    config : Schema
        The configuration schema for the application. See [] for more information about config schemas.
    device_agent : DeviceAgentInterface
        The interface to the Doover Device Agent, which allows the app to communicate with the Doover cloud and other devices.
    platform_iface : PlatformInterface
        The interface to the Doover Platform, which allows the app to interact with the device's hardware.
    modbus_iface : ModbusInterface
        The interface to the Modbus communication protocol, allowing the app to read and write Modbus registers.
    ui_manager : UIManager
        The UI manager for the application, which handles the user interface elements and commands.
    app_key : str
        The application key for the app, used to identify it in the Doover cloud. This is globally unique.
    """

    def __init__(
        self,
        config: "Schema",
        app_key: str = None,
        is_async: bool = None,
        device_agent: DeviceAgentInterface = None,
        platform_iface: PlatformInterface = None,
        modbus_iface: ModbusInterface = None,
        name: str = None,
        test_mode: bool = False,
        config_fp: str = None,
        healthcheck_port: int = None,
    ):
        self.config = config

        if config_fp:
            path = Path(config_fp)
            if not path.exists() or not path.is_file():
                raise RuntimeError(f"Config file {config_fp} does not exist")
            self._config_fp = path
        else:
            self._config_fp = None

        self.device_agent = device_agent or DeviceAgentInterface(app_key, "", is_async)
        self.platform_iface = platform_iface or PlatformInterface(app_key, "", is_async)
        self.modbus_iface = modbus_iface or ModbusInterface(
            app_key, "", is_async, config
        )

        self.ui_manager = UIManager(
            app_key=app_key,
            client=self.device_agent,
            is_async=is_async,
        )

        self.app_key = app_key
        self.app_display_name = ""

        self._is_async = get_is_async(is_async)
        self._ready = asyncio.Event()

        self._tag_values = {}
        self._tag_subscriptions = {}
        self._tag_ready = asyncio.Event()

        self._shutdown_at = None
        self.force_log_on_shutdown = False

        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

        self.loop_target_period = 1
        self._error_wait_period = 10
        self.dda_startup_timeout: int = 300

        self._last_interval_time: float | None = None
        self._last_loop_time_warning: float | None = None
        self._loop_times = deque(maxlen=20)

        self._test_next_event = asyncio.Event()
        self._test_next_loop_done = asyncio.Event()
        self.test_mode = test_mode

        self._is_healthy = False
        self._healthcheck_port = healthcheck_port

    async def _handle_healthcheck(self, _request):
        if self._is_healthy:
            return Response(text="OK", status=200)
        else:
            return Response(text="ERROR", status=503)

    async def _on_deployment_config_update(self, _, config: dict[str, Any]):
        try:
            app_config = config["applications"][self.app_key]
        except KeyError:
            log.warning(
                f"Application key {self.app_key} not found in deployment config"
            )
            app_config = {}

        self.device_agent.agent_id = app_config.get("AGENT_ID")
        log.info(f"Agent ID set: {self.device_agent.agent_id}")

        self.app_display_name = app_config.get("APP_DISPLAY_NAME", "")
        log.info(f"Application display name set: {self.app_display_name}")

        log.info(f"Deployment Config Updated: {app_config}")
        self.config._inject_deployment_config(app_config)

    async def __aenter__(self):
        # any more setup here...
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_type, (KeyboardInterrupt, asyncio.CancelledError)):
            log.info("Exiting app manager")
        else:
            log.error(f"Error in main loop: {exc_val}", exc_info=exc_tb)

        self._ready.clear()
        await self.close()

    async def next(self):
        """Increment a main loop iteration. This is only available in test mode.

        Normally, the main loop runs in an infinite cycle every `loop_target_period` seconds.

        During testing, it is helpful to be able to control the flow of the main loop, so this method allows you to
        increment the main loop iteration manually. Simply call this method to run the next iteration of the main loop.

        Examples
        --------

        A simple example::

            from pydoover.docker import Application, run_app
            from pydoover.config import Schema

            async def test_app():
                app = MyApp(config=Schema(), test_mode=True)
                asyncio.create_task(run_app(app, start=False))

                # wait for app to start
                await app.wait_until_ready()

                # increment the main loop once
                await app.next()

        Raises
        -------
        RuntimeError
            If this method is called when the app is not in test mode. This method is only available in test mode.
        """
        if not self.test_mode:
            raise RuntimeError("You can only use `app.next()` in test mode.")

        self._test_next_event.set()
        self._test_next_loop_done.clear()
        await self._test_next_loop_done.wait()

    async def _run(self):
        if RUN_HEALTHCHECK:
            try:
                log.info(
                    f"Starting healthcheck server on http://127.0.0.1:{self._healthcheck_port}"
                )
                server = Server(self._handle_healthcheck)
                runner = ServerRunner(server)
                await runner.setup()
                site = TCPSite(runner, "127.0.0.1", self._healthcheck_port)
                await site.start()
            except Exception as e:
                log.error(f"Error starting healthcheck server: {e}", exc_info=e)
        else:
            log.info("`aiohttp` not installed, skipping healthcheck server.")

        log.info(
            f"Waiting for DDA to start with a timeout of {self.dda_startup_timeout} seconds."
        )
        await self.device_agent.await_dda_available_async(self.dda_startup_timeout)

        if self._config_fp is not None:
            data = json.loads(self._config_fp.read_text())
            self.config._inject_deployment_config(data)
        else:
            self.device_agent.add_subscription(
                "deployment_config", self._on_deployment_config_update
            )
            await self.device_agent.wait_for_channels_sync_async(["deployment_config"])

        await self.modbus_iface.setup()

        try:
            await self._setup()
            ## Don't run setup in executor, to give the user the
            # ability to set up async stuff in the setup function
            await call_maybe_async(self.setup, in_executor=False)
        except Exception as e:
            log.error(f"Error in setup function: {e}", exc_info=e)
            log.warning(
                f"\n\nWaiting {self._error_wait_period} seconds before restarting app\n\n"
            )
            await asyncio.sleep(self._error_wait_period)
            return

        self.ui_manager.start_comms()
        await self.ui_manager.await_comms_sync(15)
        self._ready.set()

        try:
            shutdown_at = self._tag_values["shutdown_at"]
        except KeyError:
            pass
        else:
            await self._check_shutdown_at(shutdown_at)

        ## allow for other async tasks to run between setup and loop
        await asyncio.sleep(0.2)

        while True:
            if self.test_mode:
                await self._test_next_event.wait()
                self._test_next_event.clear()  # clear it for the next iteration...

            try:
                await self._main_loop()
                await call_maybe_async(self.main_loop)
            except Exception as e:
                log.error(f"Error in loop function: {e}", exc_info=e)
                log.warning(
                    f"\n\n\nWaiting {self._error_wait_period} seconds before restarting app\n\n"
                )
                self._is_healthy = False
                await asyncio.sleep(self._error_wait_period)
                break
            else:
                if self.test_mode is False:
                    # slow down the loop in live mode.
                    # await asyncio.sleep(self.loop_target_period)
                    await self.wait_for_interval(self.loop_target_period)
                else:
                    # allow other async tasks to run if the user has done a doozy and chained a whole heap of .next()s
                    await asyncio.sleep(0.01)

                self._is_healthy = True

            if self.test_mode is True:
                # signal that the loop is done.
                self._test_next_loop_done.set()

    async def wait_for_interval(self, target_time: float):
        """
        Waits for the necessary amount of time to maintain a consistent interval
        of `target_time` seconds between calls to this method.
        """

        current_time = time.time()
        if self._last_interval_time is None:
            self._last_interval_time = current_time
            ## Wait for half the target time on the first call
            await asyncio.sleep(target_time / 2)
            return

        elapsed = current_time - self._last_interval_time
        await self._assess_loop_time(
            elapsed, target_time
        )  ## This will display a warning if the loop is running slower than target
        elapsed = current_time - self._last_interval_time
        remaining = target_time - elapsed
        log.debug(f"Last loop time: {elapsed}, target_time: {target_time}")
        if remaining > 0:
            log.debug(f"Sleeping for {remaining} seconds to maintain target loop time")
            await asyncio.sleep(remaining)
        self._last_interval_time = time.time()

    async def _assess_loop_time(self, last_loop_time: float, target_time: float):
        """
        Assess the loop time and adjust the target time if necessary.
        """
        self._loop_times.append(last_loop_time)
        average_loop_time = sum(self._loop_times) / len(self._loop_times)
        log.debug(f"Average loop time: {average_loop_time}, target_time: {target_time}")

        ## If the loop time is greater than 20% above the target time, display a warning every 6 seconds or so
        if average_loop_time > (target_time * 1.2):
            if (
                not hasattr(self, "_last_loop_time_warning")
                or self._last_loop_time_warning is None
            ):
                self._last_loop_time_warning = time.time()
            elif time.time() - self._last_loop_time_warning > 6:
                log.warning(
                    f"Loop is running slower than target. Average loop time: {average_loop_time}, target_time: {target_time}"
                )
                self._last_loop_time_warning = time.time()

    async def close(self):
        log.info(
            "\n########################################"
            "\n\nClosing app manager...\n\n"
            "########################################\n"
        )

        await self.device_agent.close()
        await self.platform_iface.close()
        await self.modbus_iface.close()

        for task in asyncio.all_tasks():
            task.cancel()

    @property
    def is_ready(self) -> bool:
        """Check if the application is ready.

        The application is ready when all initialization tasks have completed and the UI is set up.
        In practice, this means your `setup` method has completed and the application is connected to the cloud.

        Returns
        -------
        bool
            True if the application is ready, False otherwise.
        """
        return self._ready.is_set()

    async def wait_until_ready(self):
        """Wait until the application is ready.

        This method waits (blocks) the current loop until the application is ready.
        """
        await self._ready.wait()

    ## Agent Interface Functions (DDA)

    def get_is_dda_available(self):
        return self.device_agent.get_is_dda_available()

    def get_is_dda_online(self):
        return self.device_agent.get_is_dda_online()

    def get_has_dda_been_online(self):
        return self.device_agent.get_has_dda_been_online()

    def subscribe_to_channel(
        self,
        channel_name: str,
        callback: (
            Callable[[str, dict[str, Any]], Awaitable[Any]]
            | Callable[[str, dict[str, Any]], Any]
        ),
    ):
        return self.device_agent.add_subscription(channel_name, callback)

    def publish_to_channel(self, channel_name: str, data: str | dict[str, Any]):
        return self.device_agent.publish_to_channel(channel_name, data)

    def get_channel_aggregate(self, channel_name: str):
        return self.device_agent.get_channel_aggregate(channel_name)

    ## UI Manager Functions

    def set_ui_elements(self, elements):
        return self.ui_manager.set_children(elements)

    def get_command(self, name):
        return self.ui_manager.get_command(name)

    def coerce_command(self, name, value):
        return self.ui_manager.coerce_command(name, value)

    def record_critical_value(self, name, value):
        return self.ui_manager.record_critical_value(name, value)

    def set_ui_status_icon(self, icon):
        return self.ui_manager.set_status_icon(icon)

    def start_ui_comms(self):
        return self.ui_manager.start_comms()

    async def await_ui_comms_sync(self, timeout=10):
        log.debug("Awaiting UI comms sync")
        result = await self.ui_manager.await_comms_sync(timeout=timeout)
        if result is False:
            log.warning("UI comms sync timed out")
        else:
            log.debug("UI comms sync complete")
        return result

    def set_ui(self, ui):
        self.ui_manager.set_children(ui)

    async def _update_ui(self, force_log: bool = False):
        await self.ui_manager.handle_comms_async(force_log)

    ## Platform Interface Functions

    def get_di(self, di):
        return self.platform_iface.get_di(di)

    def get_ai(self, ai):
        return self.platform_iface.get_ai(ai)

    def get_do(self, do):
        return self.platform_iface.get_do(do)

    def set_do(self, do, value):
        return self.platform_iface.set_do(do, value)

    def schedule_do(self, do, value, delay_secs):
        return self.platform_iface.schedule_do(do, value, delay_secs)

    def get_ao(self, ao):
        return self.platform_iface.get_ao(ao)

    def set_ao(self, ao, value):
        return self.platform_iface.set_ao(ao, value)

    def schedule_ao(self, ao, value, delay_secs):
        return self.platform_iface.schedule_ao(ao, value, delay_secs)

    ## Modbus Interface Functions

    def read_modbus_registers(
        self, address, count, register_type, modbus_id=None, bus_id=None
    ):
        return self.modbus_iface.read_registers(
            bus_id=bus_id,
            modbus_id=modbus_id,
            start_address=address,
            num_registers=count,
            register_type=register_type,
        )

    def write_modbus_registers(
        self, address, values, register_type, modbus_id=None, bus_id=None
    ):
        return self.modbus_iface.write_registers(
            bus_id=bus_id,
            modbus_id=modbus_id,
            start_address=address,
            values=values,
            register_type=register_type,
        )

    def add_new_modbus_read_subscription(
        self,
        address,
        count,
        register_type,
        callback,
        poll_secs=None,
        modbus_id=None,
        bus_id=None,
    ):
        return self.modbus_iface.add_read_register_subscription(
            bus_id=bus_id,
            modbus_id=modbus_id,
            start_address=address,
            num_registers=count,
            register_type=register_type,
            poll_secs=poll_secs,
            callback=callback,
        )

    # state

    @property
    def _shutdown_requested(self):
        try:
            return self._tag_values["shutdown_requested"]
        except (KeyError, TypeError):
            return False

    async def _on_tag_update(self, _, tag_values: dict[str, Any]):
        diff = generate_diff(self._tag_values, tag_values, do_delete=False)
        self._tag_values = tag_values or {}
        await self.fulfill_tag_subscriptions(diff)

        # signifies the first tag update (or any subsequent tag update) has run and we are ready to start.
        self._tag_ready.set()

        try:
            shutdown_at = tag_values["shutdown_at"]
        except (KeyError, TypeError):
            pass
        else:
            await self._check_shutdown_at(shutdown_at)

    async def _check_shutdown_at(self, shutdown_at):
        if not self.is_ready:
            log.info("Ignoring check shutdown request, app not ready yet.")
            return

        dt = datetime.fromtimestamp(shutdown_at)
        if self._shutdown_at is None or (
            dt > self._shutdown_at and dt > datetime.now()
        ):
            # shutdown should be in the future and not already scheduled
            log.info(f"Shutdown scheduled at {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            self._shutdown_at = dt
            await call_maybe_async(self.on_shutdown_at, dt)

    async def fulfill_tag_subscriptions(self, diff):
        if diff is None or len(diff) == 0:
            return

        async def _wrap_callback(callback, tag_key, new_value):
            try:
                await asyncio.wait_for(
                    call_maybe_async(callback, tag_key, new_value), timeout=1
                )
            except Exception as e:
                log.exception(f"Error in {callback.__name__}: {e}", exc_info=e)

        for k, callback in self._tag_subscriptions.items():
            if isinstance(k, tuple):
                app_key, tag_key = k
                if app_key in diff and tag_key in diff[app_key]:
                    new_value = (
                        self._tag_values[app_key][tag_key]
                        if app_key in self._tag_values
                        and tag_key in self._tag_values[app_key]
                        else None
                    )
                    await _wrap_callback(callback, tag_key, new_value)
            else:
                if k in diff:
                    new_value = self._tag_values[k] if k in self._tag_values else None
                    await _wrap_callback(callback, k, new_value)

    def subscribe_to_tag(
        self,
        tag_key: str,
        callback: Callable[[str, dict[str, Any]], Awaitable[Any]]
        | Callable[[str, dict[str, Any]], Any],
        app_key: str = None,
        global_tag: bool = False,
    ):
        if global_tag:
            self._tag_subscriptions[tag_key] = callback
        else:
            if app_key is None:
                app_key = self.app_key
            self._tag_subscriptions[(app_key, tag_key)] = callback

    def get_tag(
        self, tag_key: str, app_key: str = None, default: Any = None
    ) -> Any | None:
        """Get a tag value for a specific app.

        If you want to get a global tag, use :meth:`get_global_tag` instead.

        Examples
        --------

        >>> tag_value = self.get_tag("other_tag", "some-other-app-1234")
        >>> print(f"other-tag is {tag_value} for app some-other-app-1234")

        >>> tag_value = self.get_tag("my_tag")
        >>> print(f"my-tag is {tag_value} for current app {self.app_key}")


        Parameters
        ----------
        tag_key: str
            The tag to fetch.
        app_key: str, optional
            The app key to get the tag for. This defaults to the current app.
        default: Any, optional
            The default value to return if the tag does not exist. Defaults to None.


        Returns
        -------
        Any
            The value of the tag, or None if the tag does not exist.
        """
        try:
            if app_key is None:
                app_key = self.app_key
            return self._tag_values[app_key][tag_key]
        except (KeyError, TypeError):
            log.debug(f"Tag {tag_key} not found in current tags")
            return default

    def get_global_tag(self, tag_key: str, default: Any = None) -> Any | None:
        """Get a global tag value.

        Global tags are tags that are not specific to an app, but are shared across all apps.

        Warnings
        --------
        Due to namespacing concerns, it's best practice to use global tags sparingly and only for values that are truly global in nature.
        For example, you might use a global tag for a shutdown request or a system-wide status indicator.
        If you need to get a tag for a specific app, use :meth:`get_tag` instead.

        Examples
        --------
        >>> is_flag_set = self.get_global_tag("my_global_flag")
        >>> print(f"Global flag my_global_flag is set to {is_flag_set}")

        Parameters
        ----------
        tag_key: str
            The global tag to fetch.
        default: Any, optional
            The default value to return if the tag does not exist. Defaults to None.

        Returns
        -------
        Any
            The value of the global tag, or None if the tag does not exist.
        """
        try:
            return self._tag_values[tag_key]
        except (KeyError, TypeError):
            log.debug(f"Global tag {tag_key} not found in current tags")
            return default

    @maybe_async()
    def set_tag(
        self,
        tag_key: str,
        value: Any,
        app_key: str = None,
        only_if_changed: bool = True,
    ) -> None:
        """Set a tag value.

        This method sets a tag value for a specific app. If you want to set a global tag, use :meth:`set_global_tag` instead.

        .. note:: This method can be called in both sync and asynchronous contexts.

        Examples
        --------
        >>> self.set_tag("my_tag", "my_value")
        >>> self.set_tag("other_tag", "other_value", app_key="some-other-app-1234")

        Parameters
        ----------
        tag_key: str
            The tag to set.
        value: Any
            The value to set the tag to.
        app_key: str, optional
            The app key to set the tag for. This defaults to the current app's key.
        only_if_changed: bool, optional
            If True, the tag will only be set if the value is different from the current value. Defaults to True.
        """
        self._do_set_tags(
            {tag_key: value}, app_key=app_key, only_if_changed=only_if_changed
        )

    async def set_tag_async(
        self,
        tag_key: str,
        value: Any,
        app_key: str = None,
        only_if_changed: bool = True,
    ) -> None:
        await self._do_set_tags_async(
            {tag_key: value}, app_key=app_key, only_if_changed=only_if_changed
        )

    @maybe_async()
    def set_tags(
        self, tags: dict[str, Any], app_key: str = None, only_if_changed: bool = True
    ) -> None:
        """Set multiple tags at once."""
        self._do_set_tags(tags, app_key=app_key, only_if_changed=only_if_changed)

    async def set_tags_async(
        self, tags: dict[str, Any], app_key: str = None, only_if_changed: bool = True
    ) -> None:
        await self._do_set_tags_async(
            tags, app_key=app_key, only_if_changed=only_if_changed
        )

    @maybe_async()
    def set_global_tag(
        self, tag_key: str, value: Any, only_if_changed: bool = True
    ) -> None:
        """Set a global tag value.

        As in :meth:`get_global_tag`, global tags are not specific to an app, but are shared across all apps and should be used sparingly as such.

        .. note:: This method can be called in both sync and asynchronous contexts.

        Examples
        --------
        >>> self.set_global_tag("my_global_flag", True)
        >>> self.set_global_tag("system_status", "operational")

        Parameters
        ----------
        tag_key: str
            The global tag to set.
        value: Any
            The value to set the global tag to.
        only_if_changed: bool, optional
            If True, the tag will only be set if the value is different from the current value. Defaults to True.
        """
        self._do_set_tags(
            {tag_key: value},
            app_key=None,
            is_global=True,
            only_if_changed=only_if_changed,
        )

    async def set_global_tag_async(
        self, tag_key: str, value: Any, only_if_changed: bool = True
    ) -> None:
        """Set a global tag value asynchronously. This is a convenience method for setting global tags."""
        await self._do_set_tags_async(
            {tag_key: value},
            app_key=None,
            is_global=True,
            only_if_changed=only_if_changed,
        )

    def _do_set_tags(
        self,
        tags: dict[str, Any],
        app_key: str | None,
        is_global: bool = False,
        only_if_changed: bool = True,
    ):
        if is_global:
            data = tags
        else:
            if app_key is None:
                app_key = self.app_key
            data = {app_key: tags}

        if only_if_changed:
            diff = generate_diff(self._tag_values, data, do_delete=False)
            if len(diff) == 0:
                return

        apply_diff(self._tag_values, data, clone=False)
        self.device_agent.publish_to_channel(
            TAG_CHANNEL_NAME, data, max_age=TAG_CLOUD_MAX_AGE, record_log=True
        )

    async def _do_set_tags_async(
        self,
        tags: dict[str, Any],
        app_key: str | None,
        is_global: bool = False,
        only_if_changed: bool = True,
    ):
        if is_global:
            data = tags
        else:
            if app_key is None:
                app_key = self.app_key
            data = {app_key: tags}

        if only_if_changed:
            diff = generate_diff(self._tag_values, data, do_delete=False)
            if len(diff) == 0:
                return

        apply_diff(self._tag_values, data, clone=False)
        await self.device_agent.publish_to_channel_async(
            TAG_CHANNEL_NAME, data, max_age=TAG_CLOUD_MAX_AGE, record_log=True
        )

    ## Power Manager Functions

    @maybe_async()
    def request_shutdown(self) -> None:
        """Request a system shutdown

        .. note:: This method can be called in both sync and asynchronous contexts.
        """
        log.info("Requesting shutdown")
        self.set_tag("shutdown_requested", True)

    async def request_shutdown_async(self) -> None:
        log.info("Requesting shutdown")
        await self.set_tag_async("shutdown_requested", True)

    async def on_shutdown_at(self, dt: datetime) -> None:
        """Callback for when a shutdown is scheduled.

        See [https://docs.doover.com/docker/shutdown-behaviour] for a detailed explanation of the shutdown behaviour.

        This method is called when a shutdown is scheduled, and can be overridden by an application to perform
        specific actions before the imminent system shutdown.

        By default, this method does nothing.

        Examples
        --------

        Simple logging example::

            class MyApplication(Application):
                # setup, main_loop, etc...

                async def on_shutdown_at(self, dt: datetime):
                    log.info(f"Shutdown scheduled at {dt}. Performing cleanup...")


        Parameters
        ----------
        dt : datetime
            The datetime when the shutdown is scheduled.
        """
        if self.force_log_on_shutdown:
            await self._update_ui(force_log=True)

    async def check_can_shutdown(self) -> bool:
        """Check if the application can shutdown.

        This method is called when the application is requested to shutdown,
        and should be overridden by an application if specific logic is required when a shutdown is requested.

        See [https://docs.doover.com/docker/shutdown-behaviour] for a detailed explanation of the shutdown behaviour.

        This must be implemented as an asynchronous function, take no parameters and return a boolean value.

        A return value of `True` indicates that the application can shutdown, while `False` indicates that it cannot.

        By default, this method always returns `True`, meaning the application can shutdown without any checks.

        Examples
        --------
        Simple example that checks if Digital Output 0 (maybe an engine or fan) is Low before returning True::

            class MyApplication(Application):
                # setup, main_loop, etc...

                async def check_can_shutdown(self) -> bool:
                    if await self.platform_iface.get_do(0) == 0:
                        log.info("Digital Output 0 is Low. Can shutdown.")
                        return True
                    else:
                        log.warning("Digital Output 0 is High. Cannot shutdown.")
                        return False

        """
        return True

    ## App Functions

    async def _setup(self):
        log.info(f"Setting up internal app: {self.name}")
        self.ui_manager.register_callbacks(self)
        self.ui_manager.set_display_name(self.app_display_name)
        self.device_agent.add_subscription(TAG_CHANNEL_NAME, self._on_tag_update)
        await self.ui_manager.clear_ui_async()

        try:
            # wait for tag values to sync from DDA - but only for 10sec.
            await asyncio.wait_for(self._tag_ready.wait(), timeout=10.0)
        except TimeoutError:
            log.warning("Timed out waiting for tag values to be set")

    async def _main_loop(self):
        log.debug(f"Running internal main_loop: {self.name}")
        if self._shutdown_requested:
            try:
                resp = await self.check_can_shutdown()
            except Exception as e:
                log.error(
                    f"Error checking if we can shutdown: {e}. Assuming False.",
                    exc_info=e,
                )
                resp = False

            await self.set_tag_async("shutdown_check_ok", resp)

        await self._update_ui()

    async def setup(self):
        """The main setup function for the application.

        Your application should override this method to perform any setup tasks that need to be done before the main loop starts.

        Generally, that involves setting up UI, registering callbacks, starting state machines, etc.

        This function can be asynchronous or synchronous, depending on your needs.

        You do **not** need to call `super()` inside your setup method; this function does nothing by default.
        """
        return NotImplemented

    async def main_loop(self):
        """The main loop function for the application.

        Your application should override this method to perform the main logic of your application.

        Generally, this involves running and checking any state machines, setting tags, reading sensors, etc. depending on your application.

        This function is called in a continuous loop, so it should generally not perform any long blocking calls, instead deferring to
        checking if a result is ready to be processed in a future loop.

        You can control the speed at which this loop runs by setting the `loop_target_period` attribute of the application instance.
        By default, this is set to a target invocation period of 1 second.

        This function can be asynchronous or synchronous, depending on your needs.

        You do **not** need to call `super()` inside your setup method; this function does nothing by default.
        """
        return NotImplemented


def parse_args():
    parser = argparse.ArgumentParser(description="Doover Docker App Manager")

    parser.add_argument("--app-key", type=str, default=None, help="App Key")
    parser.add_argument(
        "--remote-dev", type=str, default=None, help="Remote device URI"
    )
    parser.add_argument(
        "--dda-uri", type=str, default=None, help="Doover Device Agent URI"
    )
    parser.add_argument(
        "--plt-uri", type=str, default="localhost:50053", help="Platform Interface URI"
    )
    parser.add_argument(
        "--modbus-uri", type=str, default="localhost:50054", help="Modbus Interface URI"
    )
    parser.add_argument(
        "--config-fp",
        type=str,
        default=None,
        help="Config file path to override app config",
    )
    parser.add_argument(
        "--healthcheck-port",
        type=int,
        default=None,
        help="Port for the healthcheck server (default: 49200). This must be overidden per-app to avoid conflicts.",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Debug Mode"
    )

    args = parser.parse_args()

    app_key = args.app_key or os.environ.get("APP_KEY")
    dda_uri = args.dda_uri or os.environ.get("DDA_URI") or "localhost:50051"
    plt_uri = args.plt_uri or os.environ.get("PLT_URI") or "localhost:50053"
    modbus_uri = args.modbus_uri or os.environ.get("MODBUS_URI") or "localhost:50054"
    healthcheck_port = int(
        args.healthcheck_port or os.environ.get("HEALTHCHECK_PORT") or 49200
    )
    config_fp = args.config_fp or os.environ.get("CONFIG_FP")

    remote_dev = args.remote_dev or os.environ.get("REMOTE_DEV")
    if remote_dev is not None:
        dda_uri = dda_uri.replace("localhost", remote_dev)
        plt_uri = plt_uri.replace("localhost", remote_dev)
        modbus_uri = modbus_uri.replace("localhost", remote_dev)

    debug = args.debug or os.environ.get("DEBUG") == "1"
    return (
        app_key,
        dda_uri,
        plt_uri,
        modbus_uri,
        remote_dev,
        config_fp,
        debug,
        healthcheck_port,
    )


def run_app(
    app: Application,
    start: bool = True,
    setup_logging: bool = True,
    log_formatter: logging.Formatter = None,
    log_filters: logging.Filter | list[logging.Filter] = None,
):
    """Run the application.

    This function initializes the application, sets up the interfaces, and runs the main loop.
    If `start` is True, it will run the application in a blocking manner, otherwise it will return an async runner function.
    This is useful for testing or when you want to run the application in an event loop without blocking the main thread, but not recommended for production use.

    Examples
    --------

    The general recommended structure for starting applications in the `__init__.py` file::

        from pydoover.docker import run_app

        from .application import SampleApplication
        from .app_config import SampleConfig

        def main():
            run_app(SampleApplication(config=SampleConfig()))


    Parameters
    ----------
    app : Application
        The application instance to run.
    start : bool, optional
        If True, the application will run in a blocking manner. If False, it will return an async runner function.
        Defaults to True.
    setup_logging : bool, optional
        If True, the logging will be set up. Defaults to True. You can pass a custom logging formatter to the `log_formatter` parameter.
    log_formatter : logging.Formatter, optional
        The logging formatter to use. Defaults to None, which will use a simple custom formatter defined in `pydoover.utils.LogFormatter`.
    log_filters : logging.Filter | list[logging.Filter], optional
        The logging filters to use. Defaults to None, which will not apply any filters.
    """
    (
        app_key,
        dda_uri,
        plt_uri,
        modbus_uri,
        remote_dev,
        config_fp,
        debug,
        healthcheck_port,
    ) = parse_args()

    user_is_async = asyncio.iscoroutinefunction(
        app.setup
    ) or asyncio.iscoroutinefunction(app.main_loop)
    is_async = get_is_async(user_is_async)
    if setup_logging:
        utils_setup_logging(debug=debug, formatter=log_formatter, filters=log_filters)

    for inst in (
        app,
        app.platform_iface,
        app.modbus_iface,
        app.device_agent,
        app.ui_manager,
    ):
        inst.app_key = app_key
        inst._is_async = is_async

    app.platform_iface.uri = plt_uri
    app.modbus_iface.uri = modbus_uri
    app.device_agent.uri = dda_uri
    app._config_fp = config_fp and Path(config_fp)
    app._healthcheck_port = healthcheck_port

    async def runner():
        async with app:
            await app._run()

    if start:
        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass
    else:
        return runner()


def run_app2(
    app_cls: type[Application],
    config: "Schema",
    dda_iface_cls: type[DeviceAgentInterface] = DeviceAgentInterface,
    plt_iface_cls: type[PlatformInterface] = PlatformInterface,
    mb_iface_cls: type[ModbusInterface] = ModbusInterface,
):
    (
        app_key,
        dda_uri,
        plt_uri,
        modbus_uri,
        remote_dev,
        config_fp,
        debug,
        healthcheck_port,
    ) = parse_args()

    user_is_async = asyncio.iscoroutinefunction(
        app_cls.setup
    ) or asyncio.iscoroutinefunction(app_cls.main_loop)
    is_async = get_is_async(user_is_async)
    utils_setup_logging(debug)

    app = app_cls(
        config,
        app_key,
        is_async,
        platform_iface=plt_iface_cls(app_key, plt_uri, is_async),
        modbus_iface=mb_iface_cls(app_key, modbus_uri, is_async, config),
        device_agent=dda_iface_cls(app_key, dda_uri, is_async),
        config_fp=config_fp,
        healthcheck_port=healthcheck_port,
    )

    async def runner():
        async with app:
            await app._run()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        pass
