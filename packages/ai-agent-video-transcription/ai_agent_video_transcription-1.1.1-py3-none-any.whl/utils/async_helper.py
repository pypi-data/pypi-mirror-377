#!/usr/bin/env python3
"""
Async Helper - Utilities for handling asyncio in different contexts
"""

import asyncio
import sys
from typing import Any, Awaitable, TypeVar

T = TypeVar('T')


def run_async(coro: Awaitable[T]) -> T:
    """
    Ejecuta una corrutina de forma segura, manejando tanto contextos con bucle de eventos
    como contextos sin él.
    
    Args:
        coro: La corrutina a ejecutar
        
    Returns:
        El resultado de la corrutina
        
    Raises:
        RuntimeError: Si hay problemas ejecutando la corrutina
    """
    try:
        # Intentar obtener el bucle de eventos actual
        loop = asyncio.get_running_loop()
        
        # Si llegamos aquí, ya hay un bucle ejecutándose
        # Crear una nueva tarea en el bucle actual
        if loop.is_running():
            # El bucle está ejecutándose, crear tarea
            task = asyncio.create_task(coro)
            
            # Si estamos en un entorno como Jupyter, necesitamos manejar esto diferente
            if _is_jupyter_or_ipython():
                return _run_in_jupyter(coro)
            else:
                # Para otros casos, podemos usar asyncio.ensure_future
                future = asyncio.ensure_future(coro)
                
                # Esperar hasta que termine usando run_until_complete
                # pero de forma segura
                return _wait_for_completion(future, loop)
        else:
            # El bucle existe pero no está ejecutándose
            return loop.run_until_complete(coro)
            
    except RuntimeError as e:
        if "no running event loop" in str(e).lower():
            # No hay bucle de eventos, crear uno nuevo
            try:
                return asyncio.run(coro)
            except RuntimeError as nested_e:
                if "asyncio.run() cannot be called from a running event loop" in str(nested_e):
                    # Intentar crear un nuevo bucle en un hilo separado
                    import threading
                    import concurrent.futures
                    
                    result = None
                    exception = None
                    
                    def run_in_thread():
                        nonlocal result, exception
                        try:
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            result = new_loop.run_until_complete(coro)
                            new_loop.close()
                        except Exception as e:
                            exception = e
                    
                    thread = threading.Thread(target=run_in_thread)
                    thread.start()
                    thread.join()
                    
                    if exception:
                        raise exception
                    return result
                else:
                    raise nested_e
        else:
            raise e


def _is_jupyter_or_ipython() -> bool:
    """Detecta si estamos ejecutando en Jupyter/IPython"""
    try:
        # Verificar si estamos en IPython
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    
    # Verificar si estamos en Jupyter por otros medios
    try:
        if 'ipykernel' in sys.modules:
            return True
    except:
        pass
        
    return False


def _run_in_jupyter(coro: Awaitable[T]) -> T:
    """Ejecuta una corrutina en entorno Jupyter"""
    try:
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(coro)
    except ImportError:
        # Si nest_asyncio no está disponible, usar un enfoque alternativo
        import threading
        import concurrent.futures
        
        result = None
        exception = None
        
        def run_in_thread():
            nonlocal result, exception
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result = new_loop.run_until_complete(coro)
                new_loop.close()
            except Exception as e:
                exception = e
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()
        
        if exception:
            raise exception
        return result


def _wait_for_completion(future, loop) -> T:
    """Espera la finalización de un future de forma segura"""
    import time
    
    # Esperar a que termine el future
    while not future.done():
        time.sleep(0.01)  # Pequeña pausa para evitar usar 100% CPU
        
    return future.result()


def is_async_context() -> bool:
    """
    Verifica si estamos en un contexto asíncrono
    
    Returns:
        True si hay un bucle de eventos ejecutándose, False en caso contrario
    """
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False


def get_or_create_loop():
    """
    Obtiene el bucle de eventos actual o crea uno nuevo si no existe
    
    Returns:
        El bucle de eventos
    """
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


# Funciones de conveniencia para casos comunes
def safe_run(coro: Awaitable[T]) -> T:
    """Alias para run_async - ejecuta una corrutina de forma segura"""
    return run_async(coro)


async def ensure_async(func_or_coro, *args, **kwargs):
    """
    Asegura que una función o corrutina se ejecute de forma asíncrona
    
    Args:
        func_or_coro: Función o corrutina a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos con nombre
        
    Returns:
        El resultado de la ejecución
    """
    if asyncio.iscoroutinefunction(func_or_coro):
        return await func_or_coro(*args, **kwargs)
    elif asyncio.iscoroutine(func_or_coro):
        return await func_or_coro
    else:
        # Es una función normal, ejecutarla
        return func_or_coro(*args, **kwargs)
