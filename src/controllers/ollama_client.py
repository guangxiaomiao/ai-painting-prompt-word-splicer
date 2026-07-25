import requests
import json
import time
from typing import List, Dict, Optional, Callable, Generator

class OllamaClient:
    def __init__(self, base_url: str = 'http://localhost:11434', timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _get_url(self, endpoint: str) -> str:
        return f'{self.base_url}{endpoint}'

    def list_models(self) -> List[Dict]:
        try:
            url = self._get_url('/api/tags')
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.ConnectionError:
            raise Exception('无法连接到 Ollama 服务，请检查服务是否启动')
        except requests.Timeout:
            raise Exception('连接超时，请检查服务地址是否正确')
        except Exception as e:
            raise Exception(f'获取模型列表失败: {str(e)}')

    def test_connection(self) -> tuple[bool, str]:
        try:
            models = self.list_models()
            return True, f'连接成功，已获取到 {len(models)} 个本地模型'
        except Exception as e:
            return False, str(e)

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
        options: Optional[Dict] = None
    ) -> str:
        try:
            url = self._get_url('/api/chat')
            payload = {
                'model': model,
                'messages': messages,
                'stream': stream
            }
            if options:
                payload['options'] = options

            if stream:
                return self._chat_stream(url, payload, callback)
            else:
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return data.get('message', {}).get('content', '')
        except requests.ConnectionError:
            raise Exception('本地 Ollama 服务连接中断，请检查服务状态')
        except requests.Timeout:
            raise Exception(f'请求超时（{self.timeout}秒），请检查服务是否正常或增加超时时间')
        except Exception as e:
            raise Exception(f'请求失败: {str(e)}')

    def _chat_stream(self, url: str, payload: Dict, callback: Optional[Callable[[str], None]] = None) -> str:
        full_response = ''
        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        line_str = line.decode('utf-8')
                        data = json.loads(line_str)
                        content = data.get('message', {}).get('content', '')
                        if content:
                            full_response += content
                            if callback:
                                callback(content)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

            return full_response
        except requests.ConnectionError:
            raise Exception('本地 Ollama 服务连接中断，请检查服务状态')
        except requests.Timeout:
            raise Exception(f'请求超时（{self.timeout}秒），请检查服务是否正常或增加超时时间')
        except Exception as e:
            raise Exception(f'流式请求失败: {str(e)}')

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
        options: Optional[Dict] = None
    ) -> str:
        try:
            url = self._get_url('/api/generate')
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': stream
            }
            if system:
                payload['system'] = system
            if options:
                payload['options'] = options

            if stream:
                return self._generate_stream(url, payload, callback)
            else:
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return data.get('response', '')
        except requests.ConnectionError:
            raise Exception('本地 Ollama 服务连接中断，请检查服务状态')
        except requests.Timeout:
            raise Exception(f'请求超时（{self.timeout}秒），请检查服务是否正常或增加超时时间')
        except Exception as e:
            raise Exception(f'请求失败: {str(e)}')

    def _generate_stream(self, url: str, payload: Dict, callback: Optional[Callable[[str], None]] = None) -> str:
        full_response = ''
        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        line_str = line.decode('utf-8')
                        data = json.loads(line_str)
                        content = data.get('response', '')
                        if content:
                            full_response += content
                            if callback:
                                callback(content)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue

            return full_response
        except requests.ConnectionError:
            raise Exception('本地 Ollama 服务连接中断，请检查服务状态')
        except requests.Timeout:
            raise Exception(f'请求超时（{self.timeout}秒），请检查服务是否正常或增加超时时间')
        except Exception as e:
            raise Exception(f'流式请求失败: {str(e)}')

    def check_model_exists(self, model_name: str) -> bool:
        try:
            models = self.list_models()
            for model in models:
                if model.get('name') == model_name:
                    return True
            return False
        except Exception:
            return False

    def batch_generate(
        self,
        model: str,
        prompts: List[str],
        system: Optional[str] = None,
        stream: bool = False,
        callback: Optional[Callable[[str, int, int], None]] = None,
        batch_interval: int = 10,
        options: Optional[Dict] = None
    ) -> List[str]:
        results = []
        total = len(prompts)
        
        for i, prompt in enumerate(prompts):
            try:
                if system:
                    result = self.generate(model, prompt, system=system, stream=stream, options=options)
                else:
                    result = self.generate(model, prompt, stream=stream, options=options)
                results.append(result)
                
                if callback:
                    callback(result, i + 1, total)
                
                if i < total - 1 and batch_interval > 0:
                    time.sleep(batch_interval)
                    
            except Exception as e:
                results.append(f'[错误] {str(e)}')
                if callback:
                    callback(f'[错误] {str(e)}', i + 1, total)
                if i < total - 1 and batch_interval > 0:
                    time.sleep(batch_interval)
        
        return results
