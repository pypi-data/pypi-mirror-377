#!/usr/bin/env python3
# __main__.py
import subprocess
import shutil
import pathlib
import urllib.request

PACKAGE_DIR = pathlib.Path(__file__).parent
CLASH_BINARY = PACKAGE_DIR / "clash"
CONFIG_FILE = PACKAGE_DIR / "config.yaml"
MMDB_FILE = PACKAGE_DIR / "Country.mmdb"
PROXY_SOCKS = "127.0.0.1:7890"
TEST_URL = "https://www.google.com"


# -------------------------------
# 启动 Clash（后台）
# -------------------------------
def start_clash():
    if not CLASH_BINARY.exists():
        print(f"[✘] Clash 可执行文件不存在: {CLASH_BINARY}")
        return

    try:
        output = subprocess.check_output(["pgrep", "-f", str(CLASH_BINARY)], text=True)
        print(f"[*] Clash 已在运行，PID: {output.strip()}")
        return
    except subprocess.CalledProcessError:
        pass

    process = subprocess.Popen(
        [str(CLASH_BINARY), "-f", str(CONFIG_FILE)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    print(f"[✔] Clash 已启动，PID: {process.pid}")


# -------------------------------
# 停止 Clash
# -------------------------------
def stop_clash():
    try:
        output = subprocess.check_output(["pgrep", "-f", str(CLASH_BINARY)], text=True)
        pids = output.strip().splitlines()
        print(f"[*] 停止 Clash, PID: {','.join(pids)}")
        for pid in pids:
            subprocess.run(["kill", pid])
        print("[✔] Clash 已停止")
    except subprocess.CalledProcessError:
        print("[*] Clash 没有运行")


# -------------------------------
# 部署 Country.mmdb
# -------------------------------
def deploy_mmdb():
    target = pathlib.Path.home() / ".config" / "clash" / "Country.mmdb"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not MMDB_FILE.exists():
        print(f"[✘] {MMDB_FILE} 不存在")
        return
    shutil.copy(MMDB_FILE, target)
    print(f"[✔] 已将 {MMDB_FILE} 复制到 {target}")


# -------------------------------
# 部署 config.yaml
# -------------------------------
def deploy_config():
    target = pathlib.Path.home() / ".config" / "clash" / "config.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        print(f"[✘] {CONFIG_FILE} 不存在")
        return
    shutil.copy(CONFIG_FILE, target)
    print(f"[✔] 已将 {CONFIG_FILE} 复制到 {target}")


# -------------------------------
# 输出代理设置指令
# -------------------------------
def setup_proxy():
    print("===============================")
    print("[*] 下面是启用 Clash 代理的指令（复制到当前终端执行即可生效）\n")
    print(f"export ALL_PROXY='socks5://{PROXY_SOCKS}'")
    print(f"export http_proxy='http://{PROXY_SOCKS}'")
    print(f"export https_proxy='http://{PROXY_SOCKS}'")
    print("\n[*] 如果需要关闭代理，请执行：")
    print("unset ALL_PROXY http_proxy https_proxy")
    print("===============================")


# -------------------------------
# 测试翻墙
# -------------------------------
def test_proxy():
    print("[*] 测试翻墙 ...")
    try:
        req = urllib.request.Request(TEST_URL)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print(f"[✔] 翻墙成功，可以访问 {TEST_URL}")
            else:
                print(f"[✘] 翻墙失败，HTTP 状态码: {response.status}")
    except Exception as e:
        print(f"[✘] 翻墙失败: {e}")
        print("[ℹ] 请先确保 Clash 已启动，并已在当前终端设置代理")


# -------------------------------
# 菜单主函数
# -------------------------------
def main():
    while True:
        print("\n===============================")
        print(" Clash 管理脚本（Python版）")
        print("===============================")
        print("1) 启动 Clash（后台运行）")
        print("2) 停止 Clash")
        print("3) 部署 Country.mmdb")
        print("4) 部署 config.yaml")
        print("5) 输出代理环境设置指令")
        print("6) 测试翻墙")
        print("0) 退出")
        choice = input("请选择操作 [0-6]: ").strip()

        if choice == "1":
            start_clash()
        elif choice == "2":
            stop_clash()
        elif choice == "3":
            deploy_mmdb()
        elif choice == "4":
            deploy_config()
        elif choice == "5":
            setup_proxy()
        elif choice == "6":
            test_proxy()
        elif choice == "0":
            print("退出")
            break
        else:
            print("[✘] 无效选择")
