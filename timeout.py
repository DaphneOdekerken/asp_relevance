from concurrent import futures as futures


def timeout(timelimit):
    def decorator(func):
        def decorated(*args, **kwargs):
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timelimit)
                except futures.TimeoutError:
                    raise TimeoutError from None
                executor._threads.clear()
                futures.thread._threads_queues.clear()
                return result
        return decorated
    return decorator
