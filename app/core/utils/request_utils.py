from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Any

class RequestUtils:
    @staticmethod
    def run_parallel_tasks(task_funcs: List[Callable], max_workers: int = 2) -> List[Any]:
        """
        Executa uma lista de funções simultaneamente em threads.

        :param task_funcs: Lista de funções sem argumentos (funções prontas para execução).
        :param max_workers: Número máximo de workers.
        :return: Lista com os resultados das funções na mesma ordem.
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(func) for func in task_funcs]
            return [f.result() for f in futures]
