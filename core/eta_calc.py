class EtaAndSpeedCalc:  # todo document and confirm
    def __init__(self, seconds_interval: int, sample_count: int):
        """
        `seconds_interval` is used because the speed and eta functions must be called at a fixed time delta interval.
        `sample_count` is how many progress checkpoints to average the eta calculation. `sample_count` must be greater than 2.
        """
        self.seconds_interval: int = seconds_interval
        self.sample_count: int = sample_count
        self.__bytes_copied_checkpoint: int = 0
        self.__progress_checkpoint: float = 0
        self.__progress_checkpoint_samples: list = []

    def speed(self, bytes_processed: int) -> int:
        """Returns bytes being processed per-second."""
        speed: int = int((bytes_processed - self.__bytes_copied_checkpoint) / self.seconds_interval)
        self.__bytes_copied_checkpoint = bytes_processed
        return speed

    def eta(self, current_progress: float) -> int | None:
        """Returns the eta in seconds."""
        self.__progress_checkpoint_samples.append(current_progress - self.__progress_checkpoint)
        progress_checkpoint_samples_count: int = len(self.__progress_checkpoint_samples)
        if progress_checkpoint_samples_count == self.sample_count:
            self.__progress_checkpoint_samples.pop(0)
            progress_checkpoint_samples_count -= 1
        aggregate_progress_deltas: float = sum(self.__progress_checkpoint_samples)
        output: int | None = int((progress_checkpoint_samples_count*self.seconds_interval*(1-current_progress))/aggregate_progress_deltas) if aggregate_progress_deltas > 0 else None
        self.__progress_checkpoint = current_progress
        return output

    def reset_eta_and_speed_vars(self) -> None:
        self.__progress_checkpoint = 0
        self.__bytes_copied_checkpoint = 0
        self.__progress_checkpoint_samples.clear()
