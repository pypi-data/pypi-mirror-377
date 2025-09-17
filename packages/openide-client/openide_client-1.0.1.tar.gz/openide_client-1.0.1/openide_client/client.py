#!/usr/bin/env python3
"""
OpenIDE Client Library
Python библиотека для взаимодействия с OpenIDE API
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class OpenIDEConfig:
    """Конфигурация OpenIDE клиента"""
    api_key: str
    openide_path: str = None
    openide_directory: str = None  # Директория OpenIDE
    timeout: int = 30

class OpenIDEClient:
    """Клиент для взаимодействия с OpenIDE API"""
    
    def __init__(self, config: OpenIDEConfig):
        self.config = config
        self.openide_directory = config.openide_directory or self._find_openide_directory()
        self.openide_path = config.openide_path or self._find_openide()
    
    def _find_openide_directory(self) -> str:
        """Поиск директории OpenIDE"""
        # Ищем директорию с openide.py
        current = Path.cwd()
        for path in [current] + list(current.parents):
            openide_file = path / "openide.py"
            if openide_file.exists():
                return str(path)
        
        # Если не найден, используем текущую директорию
        return str(Path.cwd())
        
    def _find_openide(self) -> str:
        """Поиск пути к OpenIDE"""
        # Ищем openide.py в текущей директории и родительских
        current = Path.cwd()
        for path in [current] + list(current.parents):
            openide_file = path / "openide.py"
            if openide_file.exists():
                return str(openide_file)
        
        # Если не найден, предполагаем что в PATH
        return "openide.py"
    
    def _execute_openide(self, command: str, args: Dict = None) -> Dict:
        """Выполнение команды OpenIDE"""
        if args is None:
            args = {}
        
        cmd = ["python", self.openide_path, command]
        
        # Добавляем аргументы
        for key, value in args.items():
            if isinstance(value, bool) and value:
                cmd.append(f"--{key}")
            elif not isinstance(value, bool):
                cmd.append(f"--{key}")
                cmd.append(str(value))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=self.config.timeout,
                cwd=self.openide_directory
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Timeout expired",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def run_container(self, image: str, command: str, **kwargs) -> Dict:
        """Запуск контейнера"""
        cmd = ["python", self.openide_path, "run", image, command]
        
        # Добавляем именованные аргументы
        for key, value in kwargs.items():
            if isinstance(value, bool) and value:
                cmd.append(f"--{key}")
            elif not isinstance(value, bool):
                cmd.append(f"--{key}")
                cmd.append(str(value))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=self.config.timeout,
                cwd=self.openide_directory
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Timeout expired",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def list_containers(self) -> Dict:
        """Список контейнеров"""
        return self._execute_openide("ps")
    
    def stop_container(self, container_id: str) -> Dict:
        """Остановка контейнера"""
        return self._execute_openide("stop", {"container_id": container_id})
    
    def remove_container(self, container_id: str) -> Dict:
        """Удаление контейнера"""
        return self._execute_openide("rm", {"container_id": container_id})
    
    def inspect_container(self, container_id: str) -> Dict:
        """Информация о контейнере"""
        return self._execute_openide("inspect", {"container_id": container_id})
    
    def exec_container(self, container_id: str, command: str) -> Dict:
        """Выполнение команды в контейнере"""
        return self._execute_openide("exec", {
            "container_id": container_id,
            "command": command
        })
    
    def simple_commands(self, container_id: str, commands: List[str]) -> List[Dict]:
        """Выполнение упрощенных команд в контейнере"""
        results = []
        for cmd in commands:
            result = self._execute_openide("simple", {
                "container_id": container_id,
                "command": cmd
            })
            results.append({
                "command": cmd,
                "result": result
            })
        return results
    
    def build_image(self, dockerfile_path: str, tag: str = "latest") -> Dict:
        """Сборка образа"""
        return self._execute_openide("build", {
            "dockerfile_path": dockerfile_path,
            "tag": tag
        })
    
    def list_images(self) -> Dict:
        """Список образов"""
        return self._execute_openide("images")
    
    def cleanup_containers(self) -> Dict:
        """Очистка контейнеров"""
        return self._execute_openide("cleanup")
    
    def list_archives(self) -> Dict:
        """Список архивов"""
        return self._execute_openide("archives")
    
    def restore_archive(self, archive_name: str) -> Dict:
        """Восстановление из архива"""
        return self._execute_openide("restore", {"archive_name": archive_name})
    
    def system_info(self) -> Dict:
        """Информация о системе"""
        return self._execute_openide("system")
    
    def stress_test(self, **kwargs) -> Dict:
        """Тестирование производительности"""
        return self._execute_openide("stress", kwargs)

class OpenIDEAPIClient:
    """Клиент для работы с OpenIDE API (асинхронный)"""
    
    def __init__(self, config: OpenIDEConfig):
        self.config = config
        self.openide_directory = config.openide_directory or self._find_openide_directory()
        self.openide_path = config.openide_path or self._find_openide()
    
    def _find_openide_directory(self) -> str:
        """Поиск директории OpenIDE"""
        current = Path.cwd()
        for path in [current] + list(current.parents):
            openide_file = path / "openide.py"
            if openide_file.exists():
                return str(path)
        return str(Path.cwd())
    
    def _find_openide(self) -> str:
        """Поиск пути к OpenIDE"""
        current = Path.cwd()
        for path in [current] + list(current.parents):
            openide_file = path / "openide.py"
            if openide_file.exists():
                return str(openide_file)
        return "openide.py"
    
    def create_request(self, command: str, args: Dict = None) -> str:
        """Создание API запроса"""
        if args is None:
            args = {}
        
        args_json = json.dumps(args) if args else None
        
        cmd = ["python", self.openide_path, "api-request", command, "--api-key", self.config.api_key]
        if args_json:
            cmd.extend(["--args", args_json])
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', cwd=self.openide_directory)
        
        if result.returncode == 0:
            # Извлекаем request_id из вывода
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith("📤 Запрос создан:"):
                    return line.split(": ")[1].strip()
        
        raise Exception(f"Ошибка создания запроса: {result.stderr}")
    
    def get_request_status(self, request_id: str) -> Dict:
        """Получение статуса запроса"""
        result = subprocess.run([
            "python", self.openide_path, "api-status",
            request_id
        ], capture_output=True, text=True, encoding='utf-8', cwd=self.openide_directory)
        
        if result.returncode == 0:
            # Парсим результат
            lines = result.stdout.strip().split('\n')
            status = {}
            for line in lines:
                if "Статус:" in line:
                    status["status"] = line.split(": ")[1].strip()
                elif "Результат:" in line:
                    status["result"] = line.split(": ")[1].strip()
                elif "Ошибка:" in line:
                    status["error"] = line.split(": ")[1].strip()
            return status
        
        return {"error": result.stderr}
    
    def wait_for_completion(self, request_id: str, timeout: int = 60) -> Dict:
        """Ожидание завершения запроса"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_request_status(request_id)
            
            if status.get("status") in ["completed", "error"]:
                return status
            
            time.sleep(1)
        
        return {"error": "Timeout", "status": "timeout"}

# Удобные функции для быстрого использования
def create_client(api_key: str, openide_path: str = None, openide_directory: str = None) -> OpenIDEClient:
    """Создание клиента OpenIDE"""
    config = OpenIDEConfig(api_key=api_key, openide_path=openide_path, openide_directory=openide_directory)
    return OpenIDEClient(config)

def create_api_client(api_key: str, openide_path: str = None, openide_directory: str = None) -> OpenIDEAPIClient:
    """Создание API клиента OpenIDE"""
    config = OpenIDEConfig(api_key=api_key, openide_path=openide_path, openide_directory=openide_directory)
    return OpenIDEAPIClient(config)

def main():
    """Основная функция для консольного использования"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenIDE Client")
    parser.add_argument("--api-key", required=True, help="API ключ")
    parser.add_argument("--openide-path", help="Путь к openide.py")
    parser.add_argument("--openide-directory", help="Директория OpenIDE")
    parser.add_argument("command", help="Команда для выполнения")
    parser.add_argument("args", nargs="*", help="Аргументы команды")
    
    args = parser.parse_args()
    
    client = create_client(
        api_key=args.api_key,
        openide_path=args.openide_path,
        openide_directory=args.openide_directory
    )
    
    # Выполняем команду
    if args.command == "run":
        if len(args.args) < 2:
            print("❌ Команда run требует: image command")
            return
        
        result = client.run_container(args.args[0], args.args[1])
        print(result["stdout"])
        if result["stderr"]:
            print(result["stderr"])
    
    elif args.command == "ps":
        result = client.list_containers()
        print(result["stdout"])
        if result["stderr"]:
            print(result["stderr"])
    
    else:
        print(f"❌ Неизвестная команда: {args.command}")

# Пример использования
if __name__ == "__main__":
    main()