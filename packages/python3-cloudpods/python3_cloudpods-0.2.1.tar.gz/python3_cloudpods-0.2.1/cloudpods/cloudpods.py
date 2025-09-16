import requests
import urllib3
import time
import functools
from log import log
from typing import List, Dict, Any, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enter_and_leave_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if args:
            if kwargs:
                log.info(f"begin to run function {func.__name__},args is {args},kwargs is {kwargs}")
            else:
                log.info(f"begin to run function {func.__name__},args is {args}")
        else:
            if kwargs:
                log.info(f"begin to run function {func.__name__},kwargs is {kwargs}")
            else:
                log.info(f"begin to run function {func.__name__}")
        try:
            result = func(*args, **kwargs)
            log_str=f"finish run function {func.__name__},result type is {type(result)}, and result is {result}"
            log.info(log_str)
            return result
        except Exception as e:
            log.error(f"failed to run functon {func.__name__} error message is : {e}")
            raise e
    return wrapper


class CloudPods:
    def __init__(self,keystone_url,username,password,domain="default",project="system"):
        self.__keystone_url = keystone_url
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.__project = project
        self.__session = self.__get_session()
        self.__endpoints = self.__get_endpoint()
        self.__compute_url = f"{self.__endpoints['region2']}/"
        self.__sku = {
            1: [1, 2, 4, 8],
            2: [2, 4, 8, 12, 16],
            4: [4, 12, 16, 24, 32],
            8: [8, 16, 24, 32, 64],
            12: [12, 16, 24, 32, 64],
            16: [16, 24, 32, 48, 64],
            24: [24, 32, 48, 64, 128],
            32: [32, 48, 64, 128]
        }

    @property
    def sku(self):
        return self.__sku

    @enter_and_leave_function
    def __get_session(self):
        session = requests.Session()
        headers = {
            "User-Agent": "yunioncloud-go/201708"
        }
        session.headers.update(headers)
        url = self.__keystone_url + "/auth/tokens"
        data = {
            "auth": {
                "context": {
                    "source": "cli"
                },
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": self.__username,
                            "password": self.__password
                        }
                    }
                },
                "scope": {
                    "project": {
                        "domain": {
                            "name": self.__domain
                        },
                        "name": self.__project
                    }
                }
            }
        }
        try:
            rs = session.post(url=url, json=data, verify=False, timeout=600)
            if rs.status_code != 200:
                log.error(f"Failed to get /auth/tokens: Error. err msg is {str(rs.text)}")
                return None
            if "X-Subject-Token" not in rs.headers.keys():
                log.error(f"Failed to get /auth/tokens for X-Subject-Token not in rs.headers.keys(): Error. err msg is {str(rs.text)}")
                return None
            token = rs.headers["X-Subject-Token"]
            if not token:
                log.error(f"Failed to get /auth/tokens for token is None: Error. err msg is {str(rs.text)}")
                return None
            log.info(f"Get /auth/tokens success. token is {token}")
            headers['X-Auth-Token'] = token
            session.headers.update(headers)
            return session
        except Exception as e:
            log.error(f"Failed to get /auth/tokens: Error. err msg is {str(e)}", exc_info=True)
            return None

    @enter_and_leave_function
    def __get_endpoint(self):
        try:
            get_endpoints_url = "/endpoints"
            url = self.__keystone_url + get_endpoints_url
            rs = self.__session.get(url=url, verify=False, timeout=600)
            if rs.status_code != 200:
                log.error(f"Failed to get /endpoints: Error. err msg is {str(rs.text)}")
                return None
            try:
                rs_data = rs.json()
            except Exception as e:
                log.error(f"Failed to get /endpoints: Error. err msg is {str(e)}", exc_info=True)
                return None
            endpoints=dict({})
            if "endpoints" not in rs_data.keys():
                log.error(f"Failed to get /endpoints for endpoints not in rs_data.keys(): Error. rs.text is {str(rs.text)}")
                return None
            for elem in rs_data["endpoints"]:
                if "service_name" not in elem.keys():
                    log.error(f"Failed to get /endpoints for service_name not in elem.keys(): Error. rs.text is {str(rs.text)}")
                    return None
                if "url" not in elem.keys():
                    log.error(f"Failed to get /endpoints for url not in elem.keys(): Error. rs.text is {str(rs.text)}")
                    return None
                if elem["service_name"] not in endpoints.keys():
                    endpoints[elem["service_name"]]=elem["url"]
            return endpoints
        except Exception as e:
            log.error(f"Failed to get /endpoints: Error. err msg is {str(e)}", exc_info=True)

    @enter_and_leave_function
    def __create_server(self, server: Dict[str, Any], count: int = 1) -> Optional[Dict[str, Any]]:
        """
        内部方法：向API发送请求创建服务器

        参数:
            server: 服务器配置字典，包含创建服务器所需的各项参数
            count: 要创建的服务器数量，默认为1

        返回:
            成功时返回API响应的JSON数据（字典类型）
            失败时返回None，并记录错误日志
        """
        try:
            # 构建请求URL（基于基础计算服务URL）
            request_url = f"{self.__compute_url}/servers"

            # 构建请求数据结构
            request_data = {
                "count": count,  # 创建数量
                "server": server  # 服务器配置详情
            }

            # 发送POST请求创建服务器
            # 注意：verify=False会禁用SSL证书验证，生产环境需谨慎使用
            response = self.__session.post(
                url=request_url,
                json=request_data,
                verify=False,  # 禁用SSL验证（根据环境需求调整）
                timeout=600  # 设置较长超时时间（10分钟），适应服务器创建耗时操作
            )

            # 检查HTTP响应状态码
            if response.status_code != 200:
                # 记录错误响应详情（状态码和响应内容）
                log.error(
                    f"服务器创建失败: HTTP状态码 {response.status_code}, "
                    f"错误信息: {response.text[:500]}..."  # 限制日志长度
                )
                return None

            # 解析JSON响应数据
            try:
                response_data = response.json()
                log.debug(f"服务器创建请求成功，响应数据: {response_data}")
                return response_data

            except ValueError as e:
                # 处理JSON解析失败的情况
                log.error(
                    f"服务器创建成功但响应解析失败: {str(e)}, "
                    f"原始响应内容: {response.text[:500]}..."
                )
                return None

        except Exception as e:
            # 捕获所有其他异常（如网络错误、超时等）
            log.error(f"服务器创建请求发生异常: {str(e)}", exc_info=True)
            return None

    @enter_and_leave_function
    def create_server_by_guest_image(
            self,
            guest_image_id: str,
            disk_image_id: str,
            arch: str,
            disk_size: int,
            disks: List[int],
            nets_list: List[str],
            vm_name: str,
            sku: str = "",
            count: int = 1,
            reset_new_password: str = "",
            hypervisor: str = "kvm",
            bios: str = "bios",
            cpu: int = 256,
            mem: int = 1048576,
            storage_conf: str = "none",
            storage_drive: str = "AdaptecRaid",
            storage_count: int = 1,
            storage_adapter: int = 1,
            storage_type: str = "ssd"
    ) -> List[str]:
        """
        根据 guest 镜像创建虚拟化服务器（支持KVM和裸金属类型）

        参数:
            guest_image_id:  guest 镜像ID
            disk_image_id: 磁盘镜像ID
            arch: 操作系统架构（如x86_64）
            disk_size: 系统盘大小
            disks: 数据盘大小列表（单位需注意与代码中转换一致）
            nets_list: 网络列表，每个元素为网络标识
            vm_name: 虚拟机名称
            sku: 服务器SKU型号（可选）
            count: 要创建的服务器数量，默认为1
            reset_new_password: 重置的新密码（为空则不重置）
            hypervisor: 虚拟化类型，支持"kvm"和"baremetal"，默认为"kvm"
            bios: BIOS类型，默认为"bios"
            cpu: CPU核心数（主要用于裸金属）
            mem: 内存大小（字节，主要用于裸金属）
            storage_conf: 存储配置（主要用于裸金属）
            storage_drive: 存储驱动类型（主要用于裸金属）
            storage_count: 存储设备数量（主要用于裸金属）
            storage_adapter: 存储适配器数量（主要用于裸金属）
            storage_type: 存储类型（如ssd，主要用于裸金属）

        返回:
            成功创建的服务器ID列表，失败时返回空列表
        """
        # 转换网络列表为API要求的格式
        nets = [{"network": net} for net in nets_list]

        # 初始化服务器基础配置
        server_config: Dict[str, Any] = {
            "auto_start": True,  # 服务器是否自动启动
            "generate_name": vm_name,  # 服务器名称
            "hypervisor": hypervisor,  # 虚拟化类型
            "disable_delete": False,  # 是否禁止删除
            "__count__": count,  # 创建数量
            "deploy_telegraf": True,  # 是否部署监控代理
            "os_arch": arch,  # 操作系统架构
            "nets": nets,  # 网络配置
            "prefer_region": "default",  # 首选区域
            "bios": bios  # BIOS类型
        }

        # 根据虚拟化类型配置不同参数
        if hypervisor == "kvm":
            # KVM类型服务器配置
            server_config["guest_image_id"] = guest_image_id
            server_config["sku"] = sku
            # 调度标签配置（排除特定节点）
            server_config["schedtags"] = [
                {"id": "094cfe0f-7fbf-451f-879d-d44151539240", "strategy": "exclude"}
            ]

            # 系统盘配置
            storage_medium_type = "ssd"  # 假设存储介质类型为SSD，可根据实际情况调整
            server_config["disks"] = [{
                "disk_type": "sys",  # 系统盘
                "index": 0,  # 磁盘索引
                "backend": "local",  # 存储后端
                "size": disk_size,  # 磁盘大小
                "image_id": disk_image_id,  # 磁盘镜像ID
                "medium": storage_medium_type  # 存储介质类型
            }]

            # 添加数据盘配置
            for i, disk_size_gb in enumerate(disks):
                server_config["disks"].append({
                    "disk_type": "data",  # 数据盘
                    "index": i + 1,  # 索引从1开始（0已用于系统盘）
                    "backend": "local",
                    "size": disk_size_gb * 1024,  # 转换单位（假设输入为GB，转为MB）
                    "medium": storage_medium_type
                })

        elif hypervisor == "baremetal":
            # 裸金属服务器配置
            server_config["disks"] = [{
                "size": -1,  # 表示使用全部可用空间
                "image_id": disk_image_id
            }]
            server_config["vcpu_count"] = cpu  # CPU核心数
            server_config["vmem_size"] = mem  # 内存大小（字节）
            # 存储配置
            server_config["baremetal_disk_configs"] = [{
                "conf": storage_conf,
                "driver": storage_drive,
                "count": storage_count,
                "range": list(range(0, storage_count)),  # 存储设备范围
                "adapter": storage_adapter,
                "type": storage_type
            }]

        # 密码重置配置
        if reset_new_password:
            server_config["password"] = reset_new_password
            server_config["reset_password"] = True
        else:
            server_config["reset_password"] = False

        # 调用内部方法创建服务器
        create_result = self.__create_server(server_config, count)

        # 解析返回结果，提取服务器ID
        server_ids: List[str] = []
        if "server" in create_result and "id" in create_result["server"]:
            # 单服务器创建成功
            server_ids.append(create_result["server"]["id"])
        elif "servers" in create_result:
            # 多服务器创建成功
            for server_info in create_result["servers"]:
                server_ids.append(server_info["body"]["id"])
        else:
            # 未找到服务器ID，记录警告
            log.warn(f"创建服务器失败，未获取到server_id，返回结果: {create_result}")

        return server_ids

    @enter_and_leave_function
    def get_server_detail(self, server_id):
        try:
            url = self.__compute_url + f"/servers/{server_id}"
            rs = self.__session.get(url=url, verify=False, timeout=600)
            if rs.status_code != 200:
                log.warn(f"Failed to request /servers/{server_id}: Error. err msg is {str(rs.text)}")
                return None
            try:
                rs_data = rs.json()
                return rs_data
            except Exception as e:
                log.warn(f"Failed to request /servers/{server_id}: Error. err msg is {str(e)}")
                return None
        except Exception as e:
            log.warn(f"Failed to request /servers/{server_id}: Error.\rerr msg is {str(e)}")
            return None

    @enter_and_leave_function
    def get_server_ip(self, server_id):
        server = self.get_server_detail(server_id)
        if "server" not in server.keys():
            log.warn(f"failed get server info by server name {server_id}, server info is {server}.")
            return None
        if "nics" not in server["server"].keys():
            log.warn(f"nics not in server['server'], server['server'] is {server['server']}")
            return None
        if len(server["server"]["nics"])<1:
            log.warn(f"server['server']['nics'] has no elem, its length is 0")
            return None
        if "ip_addr" not in server["server"]["nics"][0].keys():
            log.warn(f"ip_addr do not in server['server']['nics'][0], server['server']['nics'][0] is {server['server']['nics'][0]}")
            return None
        return server["server"]["nics"][0]["ip_addr"]

    @enter_and_leave_function
    def wait_for_server_is_on(self, server_id,timeout=1800):
        time_cost=0
        running_status_count = 0
        while True:
            if time_cost>=timeout:
                log.warn(f"Timeout Error: {timeout} seconds passed but server still not online: Error.")
                return False
            server_detail = self.get_server_detail(server_id)
            if "server" in server_detail.keys() and "status" in server_detail["server"].keys():
                if server_detail["server"]["status"] == "disk_fail":
                    log.warn(f"server_id: {server_id} disk_fail")
                    return False
                if server_detail["server"]["status"] == "deploy_fail":
                    log.warn(f"server_id: {server_id} deploy_fail")
                    return False
                if server_detail["server"]["status"] == "ready":
                    log.warn(f"server_id: {server_id} ready")
                    return False
                if "_fail" in server_detail["server"]["status"]:
                    log.warn(f"server_id: {server_id} {server_detail['server']['status']}")
                    return False
                if server_detail["server"]["status"] == "running":
                    log.info(f"server_id: {server_id} running")
                    running_status_count += 1
                    if running_status_count > 5:
                        log.info(f"server_id: {server_id} running for 5 times check.")
                        return True
                    else:
                        log.warn(f"just {running_status_count} times check: server_id: {server_id} running status: {server_detail['server']['status']}")
                        time.sleep(1)
                        time_cost+=1
                        continue
                else:
                    running_status_count = 0
                time.sleep(5)
                time_cost+=5
            else:
                log.warn(f"Failed to get server_detail: Error. server_detail is: {server_detail}")
                return False

    @enter_and_leave_function
    def host_has_baremetal_server(self, host_id):
        try:
            url=self.__compute_url+"/servers"
            payload = {
                "scope": "system",
                "hypervisor": "baremetal",
                "host": host_id,
                "details": True,
                "baremetal": True,
                "with_meta": True,
                "summary_stats": True
            }
            rs = self.__session.get(url=url, params=payload, verify=False, timeout=600)
            try:
                rs_data = rs.json()
                if "servers" not in rs_data.keys():
                    log.warn(f"Failed to get server_detail: Error. server_detail is: {rs_data}")
                    return False
                return bool(rs_data["servers"])
            except Exception as e:
                log.warn(f"Failed to get server_detail: Error. server_detail is: {str(e)}")
                return False
        except Exception as e:
            log.error(f"Failed to request /servers: Error.\rerr msg is {str(e)}",exc_info=True)
            return False

    @enter_and_leave_function
    def get_host_spec(self,host_id):
        try:
            url=self.__compute_url+"/hosts/"+host_id+"/spec"
            payload = {
                "scope": "system",
                "details": True,
                "baremetal": True,
                "with_meta": True,
                "summary_stats": True
            }
            rs = self.__session.get(url=url, params=payload, verify=False, timeout=600)
            try:
                rs_data = rs.json()
                return rs_data
            except Exception as e:
                log.warn(f"Failed to get host spec: Error. rs is {rs.text}.\rerr msg is {str(e)}",exc_info=True)
                return None
        except Exception as e:
            log.error(f"Failed to request /hosts/{host_id}/spec: Error.\rerr msg is {str(e)}",exc_info=True)
            return None

    @enter_and_leave_function
    def get_baremetal_hosts(self):
        try:
            get_all_baremetal_hosts = f"/hosts"
            url = self.__compute_url + get_all_baremetal_hosts
            payload = {
                "scope": "system",
                "details": True,
                "baremetal": True,
                "with_meta": True,
                "summary_stats":  True
            }
            rs = self.__session.get(url=url, params=payload, verify=False, timeout=600)
            try:
                rs_data = rs.json()
                return rs_data
            except Exception as e:
                log.warn(f"Failed to get baremetal hosts: Error. rs is {rs.text}.\rerr msg is {str(e)}",exc_info=True)
                return None
        except Exception as e:
            log.warn(f"Failed to request /hosts: Error.\rerr msg is {str(e)}",exc_info=True)
            return None

    @enter_and_leave_function
    def get_baremetal_servers(self):
        try:
            get_all_baremetal_servers = f"/servers"
            url = self.__compute_url + get_all_baremetal_servers
            payload = {
                "scope": "system",
                "hypervisor": "baremetal",
                "details": True,
                "with_meta": True,
                "summary_stats": True
            }
            rs = self.__session.get(url=url, params=payload, verify=False, timeout=600)
            try:
                rs_data = rs.json()
                return rs_data
            except Exception as e:
                log.warn(f"Failed to get baremetal servers: Error. rs is {rs.text}.\rerr msg is {str(e)}",exc_info=True)
                return None
        except Exception as e:
            log.error(f"Failed to request /servers: Error.\rerr msg is {str(e)}", exc_info=True)
            return None

    @enter_and_leave_function
    def delete_server(self, server_id):
        try:
            delete_server_url = f"/servers/{server_id}"
            url = self.__compute_url + delete_server_url
            params = {
                "OverridePendingDelete": True
            }
            rs = self.__session.delete(url=url,params=params, verify=False, timeout=600)
            if rs.status_code == 200:
                return True
            else:
                log.error(f"Failed to delete server {server_id}: Error.\nresponse msg is {rs.text}")
                return False
        except Exception as e:
            log.error(f"Failed to delete server {server_id}: Error.\nerr msg is {str(e)}",exc_info=True)
            return False


if __name__ == '__main__':
    # cloudpods = CloudPods('https://10.30.18.1:30500/v3','admin','jSj@2008')
    # server_ip = cloudpods.get_server_ip("e3b76ec7-c4f9-4065-8ce2-9d833b51368c")
    # print(server_ip)
    # cloudpods = CloudPods('https://10.240.30.110:30500/v3', 'admin', 'jSj@2008')
    cloudpods = CloudPods('https://10.20.40.101:30500/v3', 'admin', 'jSj@2008')
    # rs=cloudpods.get_baremetal_hosts()
    # print(rs)
    # print(len(rs["hosts"]))
    # rs=cloudpods.get_baremetal_servers()
    # print(rs)
    # print(len(rs["servers"]))
    # rs=cloudpods.delete_server("8c925c8e-752f-4358-8c3e-a80847732d91")
    # print(rs)
    # rs=cloudpods.host_has_baremetal_server("fa09da4e-b6d7-4a07-855d-d690abea66a9")
    # print(rs)
    # rs=cloudpods.host_has_baremetal_server("701f77bf-8cac-4b20-8787-41dc3ddc3f77")
    # print(rs)
    # rs=cloudpods.get_host_spec("5969cfe2-3a47-4a78-8ed5-36f373199d0f")
    # print(rs)
    rs=cloudpods.create_server_by_guest_image("ab370e36-6fd2-49b8-8cbe-d6af6a03d3b2","b193a66d-be6f-49c0-8c19-df43333856db",
                                              "x86_64",20480,[20],["7ff50bd9-8fbd-4c57-8687-e47933419214"],"demo",hypervisor="baremetal",bios="UEFI",
                                              storage_type="ssd",
                                              storage_conf="raid1",
                                              storage_count=2,
                                              storage_drive="AdaptecRaid",
                                              storage_adapter=1
                                              )
    print(rs)
    # rs = cloudpods.create_server_by_guest_image("8572ed8a-6ffe-451a-80ac-c04da95e777f",
    #                                             "1fdfbc15-e319-4f59-8e2b-cc45bc3517cb",
    #                                             "x86_64", 20480, [20], ["265005a2-b3a4-42e3-8154-471bdd694487"],
    #                                             "demo2", hypervisor="baremetal", bios="UEFI"
    #                                             )
    # print(rs)
    # rs=cloudpods.get_host_spec("25ca9007-111b-401e-82a0-34a4d208805b")
    # print(rs)
    # print(rs["host"]["cpu"])
    # print(rs["host"]["mem"])
    # rs = cloudpods.get_host_spec("3bf62f0b-d231-438e-8212-25f8c35f4b6f")
    # print(rs["host"]["cpu"])
    # print(rs["host"]["mem"])
    pass

