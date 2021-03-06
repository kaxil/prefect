import warnings

from prefect.client.secrets import Secret as _Secret
from prefect.core.task import Task
from prefect.engine.results import SecretResult
from prefect.utilities.tasks import defaults_from_attrs


class SecretBase(Task):
    """
    Base Secrets Task.  This task does not perform any action but rather serves as the base
    task class which should be inherited from when writing new Secret Tasks.

    Users should subclass this Task and override its `run` method for plugging into other
    Secret stores, as it is handled differently during execution to ensure the underlying
    secret value is not accidentally persisted in a non-safe location.

    Args:
        - **kwargs (Any, optional): additional keyword arguments to pass to the Task constructor

    Raises:
        - ValueError: if a `result` keyword is passed
    """

    def __init__(self, **kwargs):
        if kwargs.get("result"):
            raise ValueError("Result types for Secrets are not configurable.")
        kwargs["checkpoint"] = False
        super().__init__(**kwargs)
        self.result = SecretResult(secret_task=self)


class PrefectSecret(SecretBase):
    """
    Prefect Secrets Task.  This task retrieves the underlying secret through
    the Prefect Secrets API (which has the ability to toggle between local vs. Cloud secrets).

    Args:
        - name (str): The name of the underlying secret
        - **kwargs (Any, optional): additional keyword arguments to pass to the Task constructor

    Raises:
        - ValueError: if a `result` keyword is passed
    """

    def __init__(self, name, **kwargs):
        kwargs["name"] = name
        super().__init__(**kwargs)

    @defaults_from_attrs("name")
    def run(self, name: str = None):
        """
        The run method for Secret Tasks.  This method actually retrieves and returns the
        underlying secret value using the `Secret.get()` method.  Note that this method first
        checks context for the secret value, and if not found either raises an error or queries
        Prefect Cloud, depending on whether `config.cloud.use_local_secrets` is `True` or
        `False`.

        Args:
            - name (str, optional): the name of the underlying Secret to retrieve. Defaults
                to the name provided at initialization.

        Returns:
            - Any: the underlying value of the Prefect Secret
        """
        return _Secret(name).get()


class Secret(PrefectSecret):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "The `Secret` task is deprecated and has been renamed `PrefectSecret`.",
            UserWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
