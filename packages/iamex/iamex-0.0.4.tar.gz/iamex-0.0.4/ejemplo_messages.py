#!/usr/bin/env python3
"""
Ejemplos de uso de iamex con ambos formatos:
1. send_prompt - Para consultas simples
2. send_messages - Para conversaciones complejas
"""

from iamex import send_prompt, send_messages, PromptClient

def ejemplo_send_prompt():
    """Ejemplo usando la función send_prompt para consultas simples"""
    print("=== Ejemplo con send_prompt ===")
    
    try:
        response = send_prompt(
            prompt="Explica qué es la inteligencia artificial en una frase",
            api_key="tu_api_key_aqui",  # Reemplaza con tu API key real
            model="IAM-advanced",
            max_tokens=100
        )
        
        print("Respuesta:")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_send_messages():
    """Ejemplo usando la función send_messages"""
    print("=== Ejemplo con send_messages ===")
    
    # Definir los mensajes
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are some fun things to do in New York?"},
    ]
    
    # Enviar mensajes
    try:
        response = send_messages(
            messages=messages,
            api_key="tu_api_key_aqui",  # Reemplaza con tu API key real
            model="IAM-advanced",
            max_tokens=200
        )
        
        print("Respuesta:")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_conversacion():
    """Ejemplo de conversación con múltiples mensajes"""
    print("\n=== Ejemplo de conversación ===")
    
    # Conversación más compleja
    messages = [
        {"role": "system", "content": "Eres un asistente experto en programación Python."},
        {"role": "user", "content": "¿Qué es una función lambda en Python?"},
        {"role": "assistant", "content": "Una función lambda es una función anónima que se define en una sola línea."},
        {"role": "user", "content": "¿Puedes darme un ejemplo práctico?"}
    ]
    
    try:
        response = send_messages(
            messages=messages,
            api_key="tu_api_key_aqui",  # Reemplaza con tu API key real
            model="IAM-advanced",
            max_tokens=300
        )
        
        print("Respuesta:")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_con_cliente():
    """Ejemplo usando PromptClient"""
    print("\n=== Ejemplo con PromptClient ===")
    
    # Crear cliente
    client = PromptClient(api_key="tu_api_key_aqui")  # Reemplaza con tu API key real
    
    # Mensajes
    messages = [
        {"role": "system", "content": "You are a creative writing assistant."},
        {"role": "user", "content": "Write a short story about a robot learning to paint."}
    ]
    
    try:
        response = client.send_messages(
            messages=messages,
            model="IAM-advanced",
            max_tokens=400,
            temperature=0.8
        )
        
        print("Respuesta:")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_con_parametros():
    """Ejemplo con parámetros adicionales"""
    print("\n=== Ejemplo con parámetros adicionales ===")
    
    messages = [
        {"role": "system", "content": "Eres un asistente técnico especializado en desarrollo web."},
        {"role": "user", "content": "Explica qué es React y sus ventajas principales."}
    ]
    
    try:
        response = send_messages(
            messages=messages,
            api_key="tu_api_key_aqui",  # Reemplaza con tu API key real
            model="IAM-advanced",
            max_tokens=250,
            temperature=0.7,
            top_p=0.9
        )
        
        print("Respuesta:")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Ejemplos de uso de iamex - Prompts y Conversaciones")
    print("=" * 60)
    
    # Ejecutar ejemplos
    ejemplo_send_prompt()
    ejemplo_send_messages()
    ejemplo_conversacion()
    ejemplo_con_cliente()
    ejemplo_con_parametros()
    
    print("\n" + "=" * 60)
    print("¡Ejemplos completados!")
    print("\nNota: Recuerda reemplazar 'tu_api_key_aqui' con tu API key real de dev.iamex.io")
