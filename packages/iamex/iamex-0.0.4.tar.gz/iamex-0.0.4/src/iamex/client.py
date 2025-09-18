"""
Cliente principal para consumir la API de modelos de inferencia
"""

import requests
from typing import Dict, Any, Optional


class PromptClient:
    """Cliente para enviar prompts a modelos de inferencia"""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el cliente
        
        Args:
            api_key: Clave de API para autenticación (opcional por ahora)
        """
        self.api_key = api_key
        # Endpoint real de iam-hub
        self.base_url = "https://iam-hub.iamexprogramers.site/api/v1"
        self.session = requests.Session()
        
        # Configurar headers básicos
        self.session.headers.update({
            'accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def send_prompt(self, prompt: str, model: str = "IAM-advanced", system_prompt: str = None, full_response: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Envía un prompt al modelo especificado
        
        Args:
            prompt: El prompt del usuario a enviar
            model: Modelo a usar (por defecto 'IAM-advanced')
            system_prompt: Prompt del sistema (opcional)
            full_response: Si True retorna respuesta completa, si False solo el content (default: False)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Si full_response=False: Solo el contenido de la respuesta (str)
            Si full_response=True: Respuesta completa de la API (dict)
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        payload = self._prepare_payload(prompt, model, system_prompt, **kwargs)
        
        try:
            response = self.session.post(
                f"{self.base_url}/prompt-model",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            json_response = response.json()
            
            # Si full_response es False, extraer solo el content
            if not full_response:
                return self._extract_content(json_response)
            
            return json_response
        except requests.RequestException as e:
            # Manejar errores HTTP específicos
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('detail', str(e))
                    status_code = e.response.status_code
                    raise Exception(f"Error {status_code}: {error_message}")
                except ValueError:
                    # Si no es JSON, usar el texto de la respuesta
                    error_message = e.response.text or str(e)
                    status_code = e.response.status_code
                    raise Exception(f"Error {status_code}: {error_message}")
            else:
                raise Exception(f"Error al enviar prompt: {str(e)}")
    
    def send_messages(self, messages: list, model: str = "IAM-advanced", full_response: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Envía mensajes al modelo especificado usando formato de conversación
        
        Args:
            messages: Lista de mensajes con formato [{"role": "system/user/assistant", "content": "mensaje"}]
            model: Modelo a usar (por defecto 'IAM-advanced')
            full_response: Si True retorna respuesta completa, si False solo el content (default: False)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Si full_response=False: Solo el contenido de la respuesta (str)
            Si full_response=True: Respuesta completa de la API (dict)
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        payload = self._prepare_messages_payload(messages, model, **kwargs)
        
        try:
            response = self.session.post(
                f"{self.base_url}/prompt-model",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            json_response = response.json()
            
            # Si full_response es False, extraer solo el content
            if not full_response:
                return self._extract_content(json_response)
            
            return json_response
        except requests.RequestException as e:
            # Manejar errores HTTP específicos
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('detail', str(e))
                    status_code = e.response.status_code
                    raise Exception(f"Error {status_code}: {error_message}")
                except ValueError:
                    # Si no es JSON, usar el texto de la respuesta
                    error_message = e.response.text or str(e)
                    status_code = e.response.status_code
                    raise Exception(f"Error {status_code}: {error_message}")
            else:
                raise Exception(f"Error al enviar mensajes: {str(e)}")
    
    def _prepare_payload(self, prompt: str, model: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Prepara el payload para la API de iam-hub con formato de prompt"""
        # Estructura exacta que espera la API para prompts
        payload = {
            'apikey': self.api_key,
            'model': model,
            'prompt': prompt
        }
        
        # Agregar parámetros adicionales si se proporcionan
        if system_prompt:
            payload['system_prompt'] = system_prompt
        
        # Agregar otros parámetros si se proporcionan
        for key, value in kwargs.items():
            if key not in ['apikey', 'model', 'prompt', 'system_prompt']:
                payload[key] = value
        
        return payload
    
    def _prepare_messages_payload(self, messages: list, model: str, **kwargs) -> Dict[str, Any]:
        """Prepara el payload para la API de iam-hub con formato de mensajes"""
        # Estructura que espera la API con messages
        payload = {
            'apikey': self.api_key,
            'model': model,
            'messages': messages
        }
        
        # Agregar otros parámetros si se proporcionan
        for key, value in kwargs.items():
            if key not in ['apikey', 'model', 'messages']:
                payload[key] = value
        
        return payload
    
    def _extract_content(self, json_response: Dict[str, Any]) -> str:
        """
        Extrae solo el contenido de la respuesta de la API
        
        Args:
            json_response: Respuesta completa de la API
            
        Returns:
            Solo el contenido/texto de la respuesta
        """
        try:
            # Formato de iamex API: data.response.choices[0].message.content
            if 'data' in json_response and 'response' in json_response['data']:
                response_data = json_response['data']['response']
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    choice = response_data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        return choice['message']['content']
            
            # Formato estándar de respuesta: choices[0].message.content
            if 'choices' in json_response and len(json_response['choices']) > 0:
                choice = json_response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
            
            # Formato alternativo: directamente en 'content'
            if 'content' in json_response:
                return json_response['content']
            
            # Si no encuentra el formato esperado, devolver la respuesta completa
            return str(json_response)
        except (KeyError, IndexError, TypeError):
            # En caso de error, devolver la respuesta completa como string
            return str(json_response)
    
    def get_models(self) -> Dict[str, Any]:
        """Obtiene la lista de modelos disponibles"""
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Error al obtener modelos: {str(e)}")
