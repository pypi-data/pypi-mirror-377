from mcp.server.fastmcp import FastMCP
import requests
import json
from datetime import datetime
from typing import Dict, Optional, Union

mcp = FastMCP('Find the location of Yang Jianfei')

# 位置查询相关配置
BASE_URL = "http://39.98.54.173:40013/VocalBuddy/API"
PHP_SCRIPT = "get_latest_locations.php"
FULL_URL = f"{BASE_URL}/{PHP_SCRIPT}"

def _format_datetime(datetime_str: Optional[str]) -> str:
    """
    格式化日期时间字符串
    
    Args:
        datetime_str: 日期时间字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if not datetime_str:
        return '未知时间'
    
    try:
        # 尝试解析不同的日期时间格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(datetime_str, fmt)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        # 如果所有格式都失败，返回原始字符串
        return datetime_str
    except Exception:
        return datetime_str

def get_latest_locations(user_id: Optional[int] = None, limit: int = 3) -> Dict[str, Union[bool, str, int, list]]:
    """
    获取最新位置记录
    
    Args:
        user_id: 用户ID,如果为None则查询所有猫猫用户
        limit: 返回记录数量限制
        
    Returns:
        包含查询结果的字典
    """
    try:
        # 构建查询参数
        params = {'limit': limit}
        if user_id is not None:
            params['user_id'] = user_id
        
        # 发送GET请求
        response = requests.get(FULL_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # 解析JSON响应
        result = response.json()
        
        # 格式化返回数据
        if result.get('success') and 'data' in result:
            formatted_data = []
            for item in result['data']:
                formatted_item = {
                    'id': item.get('id'),
                    'user_id': item.get('user_id'),
                    'latitude': item.get('latitude'),
                    'longitude': item.get('longitude'),
                    'address': item.get('address', '未提供'),
                    'recorded_at': item.get('recorded_at'),
                    'formatted_time': _format_datetime(item.get('recorded_at'))
                }
                formatted_data.append(formatted_item)
            
            result['data'] = formatted_data
            result['message'] = '查询成功'
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'网络错误: {str(e)}',
            'data': [],
            'count': 0
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'message': f'JSON解析错误: {str(e)}',
            'data': [],
            'count': 0
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'未知错误: {str(e)}',
            'data': [],
            'count': 0
        }

@mcp.tool()
def get_user_latest_location() -> str:

    """
    获取"杨建飞(Yang Jianfei)用户的最新位置记录
    
    Args:
        user_id: 用户ID，默认为1
        limit: 返回记录数量限制，默认为1
        
    Returns:
        JSON格式的位置信息
    """
    user_id: int=1
    limit: int = 1
    result = get_latest_locations(user_id=user_id, limit=limit)
    
    return json.dumps(result, ensure_ascii=False, indent=2)  # 返回格式化的 JSON 字符串


def main() -> None:
    mcp.run(transport='stdio')
