import asyncio
import sys
import traceback
from collections import namedtuple
import time
import json
import argparse
import concurrent.futures

from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService
from pymobiledevice3.services.dvt.instruments.graphics import Graphics
from pymobiledevice3.services.dvt.instruments.sysmontap import Sysmontap
from pymobiledevice3.services.os_trace import OsTraceService
from pymobiledevice3.services.installation_proxy import InstallationProxyService


class MonitorSysmon:
    process_info = namedtuple('process', 'pid name cpuUsage physFootprint memVirtualSize memRPrvt memRShrd threadCount')

    def __init__(self, udid, pid, rsd_address=None, rsd_port=None, interval=0.5):
        self.udid = udid
        self.pid = pid
        self.rsd_address = rsd_address
        self.rsd_port = rsd_port
        self.interval = interval
        self.lockdown = None

    async def sysmon_process_single(self):
        if self.rsd_address is not None and self.rsd_port is not None:
            print(f'iOS 17以上系统采集性能数据，隧道协议Address: {self.rsd_address}，Port:{self.rsd_port}')
            self.lockdown = RemoteServiceDiscoveryService((self.rsd_address, int(self.rsd_port)))
            await self.lockdown.connect()
        else:
            print('iOS 17以下系统采集性能数据')
            self.lockdown = create_using_usbmux(serial=self.udid)

        if self.lockdown is None:
            raise Exception("无法建立设备连接")

        with DvtSecureSocketProxyService(lockdown=self.lockdown) as dvt:
            with Sysmontap(dvt) as sysmon:
                next_print_time = time.time()
                last_entries = None

                for process_snapshot in sysmon.iter_processes():
                    entries = []
                    for process in process_snapshot:
                        if (process['cpuUsage'] is not None) and (process['cpuUsage'] >= 0):
                            entries.append(
                                self.process_info(pid=process['pid'], name=process['name'],
                                                  cpuUsage=process['cpuUsage'],
                                                  physFootprint=process['physFootprint'],
                                                  memVirtualSize=process['memVirtualSize'],
                                                  threadCount=process['threadCount'],
                                                  memRShrd=process['memRShrd'],
                                                  memRPrvt=process['memRPrvt']))

                    last_entries = entries

                    current_time = time.time()
                    if current_time >= next_print_time:
                        next_print_time += self.interval
                        if next_print_time < current_time:
                            next_print_time = current_time + self.interval
                        yield last_entries

    async def stop_monitor(self):
        if self.lockdown:
            print('停止采集数据')
            if self.rsd_address is not None and self.rsd_port is not None:
                await self.lockdown.close()
            else:
                self.lockdown.close()

    def get_graphics(self):
        with DvtSecureSocketProxyService(lockdown=self.lockdown) as dvt:
            with Graphics(dvt) as graphics:
                for stats in graphics:
                    print(stats)

    async def async_get_graphics(self, timeout=0.3):
        def get_gpu_data_sync():
            try:
                with DvtSecureSocketProxyService(lockdown=self.lockdown) as dvt:
                    with Graphics(dvt) as graphics:
                        for stats in graphics:
                            return {"Device Utilization %": stats["Device Utilization %"],
                                    "Renderer Utilization %": stats["Renderer Utilization %"],
                                    "Tiler Utilization %": stats["Tiler Utilization %"],
                                    "GPU Memory Usage": round(stats["Alloc system memory"] / 1024 / 1024, 2)}

                return None
            except Exception:
                return None
            except KeyboardInterrupt:
                print("GPU 监控已停止")

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(get_gpu_data_sync)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                return {'error': '获取GPU数据超时'}
            except KeyboardInterrupt:
                print("GPU 监控已停止")

    def get_process_list_with_pid(self):
        try:
            try:
                processes_list = OsTraceService(lockdown=self.lockdown).get_pid_list().get('Payload')
                pid_dict = {process_info.get('ProcessName'): pid for pid, process_info in processes_list.items()}
            except Exception as e:
                print(f"获取PID列表时出错: {e}")
                pid_dict = {}
            with InstallationProxyService(self.lockdown) as installation_proxy_service:
                apps = installation_proxy_service.get_apps(application_type='User', calculate_sizes=True)
                combined_process_list = []
                for bundle_id, app_info in apps.items():
                    app_name = app_info.get('CFBundleDisplayName', 'N/A')
                    path = app_info.get("Path", 'N/A')
                    process_name = path.split('/')[-1].split(".")[0]
                    pid = pid_dict.get(process_name, None)

                    process_info = {
                        'pid': pid,
                        'bundle_id': bundle_id,
                        'process_name': process_name,
                        'name': app_name,
                        'version': app_info.get('CFBundleShortVersionString', 'N/A'),
                        'size': app_info.get('ApplicationSize', 'N/A'),
                        'dynamic_size': app_info.get('DynamicDiskUsage', 'N/A'),
                        'static_size': app_info.get('StaticDiskUsage', 'N/A')
                    }
                    print(process_info)
                    combined_process_list.append(process_info)
                return combined_process_list

        except Exception as e:
            print(f"发生错误: {e}")
            traceback.print_exc()
            return None


async def main():
    parser = argparse.ArgumentParser(description='iOS设备进程性能监控工具')
    parser.add_argument('--rsd-address', type=str, required=False, help='RSD地址 (用于iOS 17+)')
    parser.add_argument('--rsd-port', type=int, required=False, help='RSD端口 (用于iOS 17+)')
    parser.add_argument('--pid', type=int, required=True, help='目标进程ID')
    parser.add_argument('--bundle-id', type=str, required=False, help='应用包名')
    parser.add_argument('--udid', type=str, required=False, help='设备UDID')
    parser.add_argument('--interval', type=float, default=1.0, help='输出间隔时间(秒)，默认为1.0秒')
    args = parser.parse_args()
    monitor = MonitorSysmon(udid=args.udid, pid=args.pid, rsd_address=args.rsd_address,
                            rsd_port=args.rsd_port, interval=args.interval)
    try:
        async for entries in monitor.sysmon_process_single():
            for entry in entries:
                if entry.pid == args.pid:
                    # 异步获取GPU数据，设置较短的超时时间
                    gpu_data = await monitor.async_get_graphics()

                    data = {
                        "name": entry.name,
                        "pid": entry.pid,
                        "cpuUsage": round(entry.cpuUsage, 2),
                        "physFootprint": round(entry.physFootprint / 1024 / 1024, 2),
                        "memVirtualSize": round(entry.memVirtualSize / 1024 / 1024, 2),
                        "memRPrvt": round(entry.memRPrvt / 1024 / 1024, 2),
                        "memRShrd": round(entry.memRShrd / 1024 / 1024, 2),
                        "threadCount": entry.threadCount,
                        "gpuData": gpu_data
                    }

                    print(json.dumps(data, ensure_ascii=False))
                    sys.stdout.flush()
                    break
    except KeyboardInterrupt:
        print("监控已停止")
        await monitor.stop_monitor()
    except Exception as e:
        print(f"监控过程中发生错误: {e}")
        await monitor.stop_monitor()


if __name__ == '__main__':
    asyncio.run(main())
