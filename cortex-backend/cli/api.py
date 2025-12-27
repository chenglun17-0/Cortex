import requests
import typer
from cli.config import API_URL, ACCESS_TOKEN, get_config_value


class APIClient:
    def __init__(self):
        self.token = get_config_value(ACCESS_TOKEN)
        self.api_url = get_config_value(API_URL)
        if not self.token:
            typer.echo("Error: Not logged in. Please run 'ctx auth login' first.")
            raise typer.Exit(code=1)

    def get(self, endpoint: str):
        """发送 GET 请求"""
        headers = {"Authorization": f"Bearer {self.token}"}
        return requests.get(f"{self.api_url}{endpoint}", headers=headers)

    def post(self, endpoint: str, json_data: dict):
        """发送 POST 请求"""
        headers = {"Authorization": f"Bearer {self.token}"}
        return requests.post(f"{self.api_url}{endpoint}", headers=headers, json=json_data)

    def patch(self, endpoint: str, json_data: dict):
        """发送 PATCH 请求"""
        headers = {"Authorization": f"Bearer {self.token}"}
        return requests.patch(f"{self.api_url}{endpoint}", headers=headers, json=json_data)
# 全局单例
client = APIClient