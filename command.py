import time

def retry_on_exception(max_attempts=3, interval=1, ignore_exception=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args,**kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Caught exception: {e} during {attempts} times trying.")
                    if attempts >= max_attempts:
                        if ignore_exception:
                            break
                        else:
                            raise
                    print(f"Retrying in {attempts + 1}/{max_attempts} times, in {interval} seconds")
                    time.sleep(interval)
        return wrapper
    return decorator