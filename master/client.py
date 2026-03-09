import requests
import json
import argparse
import sys


def run_task(server_url: str, uid: str, brief: str):
    """执行即时任务"""
    url = f"{server_url}/run"
    
    payload = {
        "uid": uid,
        "brief": brief
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {url}...")
    print(f"UID: {uid}")
    print(f"Brief: {brief}")
    print()
    
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            if response.status_code == 200:
                print("=" * 50)
                print("Response:")
                print("=" * 50)
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        print(chunk, end="", flush=True)
                print()
                print("=" * 50)
            else:
                print(f"Request Failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to server.")
        print(f"Make sure the server is running on {server_url}")
        print("Run 'python master/server.py' first.")


def schedule_task(server_url: str, uid: str, task_name: str, task_instruction: str, scheduled_time: str, repeat: str = "none"):
    """创建定时任务"""
    url = f"{server_url}/schedule"
    
    payload = {
        "uid": uid,
        "task_name": task_name,
        "task_instruction": task_instruction,
        "scheduled_time": scheduled_time,
        "repeat": repeat
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Creating scheduled task...")
    print(f"UID: {uid}")
    print(f"Task: {task_name}")
    print(f"Scheduled Time: {scheduled_time}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nTask created successfully!")
            print(f"Task ID: {result.get('task_id')}")
            print(f"Message: {result.get('message')}")
        else:
            print(f"\nRequest Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to server.")


def list_tasks(server_url: str, uid: str):
    """查看定时任务列表"""
    url = f"{server_url}/tasks/{uid}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            tasks = result.get("tasks", [])
            
            if not tasks:
                print("No pending tasks.")
                return
            
            print(f"\nPending Tasks ({len(tasks)}):")
            print("-" * 60)
            for t in tasks:
                print(f"ID: {t['task_id']} | {t['task_name']}")
                print(f"Time: {t['scheduled_time']} | Repeat: {t['repeat']}")
                print(f"Instruction: {t['task_instruction'][:50]}...")
                print("-" * 60)
        else:
            print(f"Request Failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to server.")


def cancel_task(server_url: str, uid: str, task_id: str):
    """取消定时任务"""
    url = f"{server_url}/tasks/{uid}/{task_id}"
    
    try:
        response = requests.delete(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Task cancelled: {result.get('message')}")
        else:
            print(f"Request Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to server.")


def health_check(server_url: str):
    """健康检查"""
    url = f"{server_url}/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Server Status: {result.get('status')}")
            print(f"Scheduler Running: {result.get('scheduler_running')}")
        else:
            print(f"Server Unhealthy: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Server is not running.")


def main():
    parser = argparse.ArgumentParser(description="AutoVen Client")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    parser.add_argument("--uid", default="test_user", help="User ID")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("brief", help="Task brief/instruction")
    
    # schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Create a scheduled task")
    schedule_parser.add_argument("--name", required=True, help="Task name")
    schedule_parser.add_argument("--instruction", required=True, help="Task instruction")
    schedule_parser.add_argument("--time", required=True, help="Scheduled time (YYYY-MM-DD HH:MM:SS)")
    schedule_parser.add_argument("--repeat", default="none", choices=["none", "daily", "weekly", "monthly"], help="Repeat mode")
    
    # list command
    subparsers.add_parser("list", help="List scheduled tasks")
    
    # cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a scheduled task")
    cancel_parser.add_argument("task_id", help="Task ID to cancel")
    
    # health command
    subparsers.add_parser("health", help="Health check")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_task(args.server, args.uid, args.brief)
    elif args.command == "schedule":
        schedule_task(args.server, args.uid, args.name, args.instruction, args.time, args.repeat)
    elif args.command == "list":
        list_tasks(args.server, args.uid)
    elif args.command == "cancel":
        cancel_task(args.server, args.uid, args.task_id)
    elif args.command == "health":
        health_check(args.server)
    else:
        # Default: interactive mode
        print("AutoVen Client")
        print("=" * 50)
        print(f"Server: {args.server}")
        print(f"UID: {args.uid}")
        print()
        print("Commands:")
        print("  python master/client.py run '你的任务描述'")
        print("  python master/client.py schedule --name '任务名' --instruction '任务说明' --time '2026-03-02 09:00:00'")
        print("  python master/client.py list")
        print("  python master/client.py cancel <task_id>")
        print("  python master/client.py health")
        print()
        
        # Default demo
        print("Running demo task...")
        run_task(args.server, args.uid, "你看你生成一个真实探店内容，都没有去调研...是skill写的不对吗")


if __name__ == "__main__":
    main()
