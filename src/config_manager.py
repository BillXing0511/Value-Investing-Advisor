"""
配置管理模块 - 管理投资标准和系统配置
"""
import json
import os
from typing import Dict, Any
from datetime import datetime


class ConfigManager:
    """管理投资标准配置"""

    def __init__(self, config_path: str = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'investment_criteria.json'
            )
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return self._get_default_config()

    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            self.config['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_criteria(self) -> Dict[str, Any]:
        """获取投资标准"""
        return self.config.get('criteria', {})

    def update_criteria(self, criterion: str, **kwargs) -> bool:
        """
        更新单个投资标准

        Args:
            criterion: 标准名称
            **kwargs: 要更新的字段
        """
        if criterion not in self.config['criteria']:
            print(f"标准不存在: {criterion}")
            return False

        self.config['criteria'][criterion].update(kwargs)
        return self.save_config()

    def enable_criterion(self, criterion: str) -> bool:
        """启用某个投资标准"""
        return self.update_criteria(criterion, enabled=True)

    def disable_criterion(self, criterion: str) -> bool:
        """禁用某个投资标准"""
        return self.update_criteria(criterion, enabled=False)

    def get_enabled_criteria(self) -> Dict[str, Any]:
        """获取所有启用的投资标准"""
        return {
            name: criteria
            for name, criteria in self.config['criteria'].items()
            if criteria.get('enabled', False)
        }

    def get_markets(self) -> Dict[str, bool]:
        """获取市场配置"""
        return self.config.get('markets', {'us': True, 'hk': True, 'cn': True})

    def update_market(self, market: str, enabled: bool) -> bool:
        """更新市场配置"""
        if market not in ['us', 'hk', 'cn']:
            print(f"无效的市场: {market}")
            return False

        if 'markets' not in self.config:
            self.config['markets'] = {}

        self.config['markets'][market] = enabled
        return self.save_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "criteria": {
                "pe_ratio": {
                    "enabled": True,
                    "min": 0,
                    "max": 15,
                    "description": "市盈率 (Price-to-Earnings Ratio)"
                }
            },
            "markets": {
                "us": True,
                "hk": True,
                "cn": True
            },
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def display_config(self) -> str:
        """以友好格式显示配置"""
        lines = ["=" * 60]
        lines.append("投资标准配置")
        lines.append("=" * 60)

        criteria = self.get_criteria()
        for name, criterion in criteria.items():
            status = "✓" if criterion.get('enabled', False) else "✗"
            lines.append(f"\n{status} {criterion.get('description', name)}")

            if 'min' in criterion and 'max' in criterion:
                lines.append(f"  范围: {criterion['min']} - {criterion['max']}")
            elif 'value' in criterion:
                lines.append(f"  值: {criterion['value']}")

        lines.append("\n" + "=" * 60)
        lines.append("目标市场")
        lines.append("=" * 60)
        markets = self.get_markets()
        market_names = {'us': '美国', 'hk': '香港', 'cn': '中国'}
        for code, enabled in markets.items():
            status = "✓" if enabled else "✗"
            lines.append(f"{status} {market_names.get(code, code)}")

        lines.append("\n更新时间: " + self.config.get('last_updated', 'N/A'))
        lines.append("=" * 60)

        return "\n".join(lines)


if __name__ == "__main__":
    # 测试配置管理器
    config_mgr = ConfigManager()
    print(config_mgr.display_config())
