from apminsight import constants
from apminsight.instrumentation.wrapper import default_wrapper, background_wrapper
from apminsight.context import is_no_active_txn, get_cur_txn
from apminsight.agentfactory import get_agent
from apminsight.logger import agentlogger


def celery_task_schedule_wrapper(original, module, method_info):
    def wrapper(*args, **kwargs):
        try:
            module = args[0].__class__.__module__
            method_info[constants.class_str] = ""
            method_info[constants.method_str] = args[0].__class__.__module__
        except Exception as exc:
            agentlogger.info("Exception at celery_task_schedule_wrapper")

        return default_wrapper(original, module, method_info)(*args, **kwargs)

    # special handling for flask route decorator
    wrapper.__name__ = original.__name__
    return wrapper


def get_celery_app_name(task):
    return task.app.main


def build_tracer_wrapper(original, module, method_info):
    def wrap_celery_task(task_name, task_addr):
        if hasattr(task_addr, "run"):
            try:
                module = task_addr.__class__.__module__
                method_info[constants.class_str] = task_addr.__class__.__name__
                method_info[constants.method_str] = task_name
                original = getattr(task_addr, "run")
                task_wrapper = background_wrapper(original, task_name, module, method_info.copy())
                setattr(task_addr, "run", task_wrapper)
            except Exception as exc:
                agentlogger.info("Exception when wrapping celery task " + task_name)

    def wrapper(*args, **kwargs):
        try:
            wrap_celery_task(args[0], args[1])
            return original(*args, **kwargs)
        except Exception as exc:
            raise exc

    return wrapper


module_info = {
    "celery.app.trace": [
        {
            constants.method_str: "build_tracer",
            constants.wrapper_str: build_tracer_wrapper,
            constants.component_str: constants.celery,
        }
    ],
    "celery.app.task": [
        {
            constants.class_str: "BaseTask",
            constants.method_str: "apply_async",
            constants.wrapper_str: celery_task_schedule_wrapper,
            constants.component_str: constants.celery,
        }
    ],
}
