import tkinter as tk
from src.ui.dialog import Dialog
from src.log.log_utils import get_model_info_for_open_model_dialog

from src.utils.formatting import get_pretty_whole_percentage, get_pretty_large_integer


class OpenFileDialog(Dialog):

    def body(self, master):
        model_logs, model_names = get_model_info_for_open_model_dialog(self.parent.current_track,
                                                                       self.parent.get_log_directory())
        all_best_steps = []
        all_average_steps = []
        all_progress_percent = []
        all_success_percent = []

        show_laps = False
        for log in model_logs.values():
            log_meta = log.get_log_meta()
            if log_meta.episode_stats.average_steps > 0:
                all_best_steps.append(log_meta.episode_stats.best_steps)
                all_average_steps.append(log_meta.episode_stats.average_steps)
                show_laps = True
            all_progress_percent.append(self._get_progress_percent(log_meta))
            all_success_percent.append(self._get_success_percent(log_meta))

        best_best_steps = min(all_best_steps)
        best_average_steps = min(all_average_steps)
        best_progress_percent = max(all_progress_percent)
        best_success_percent = max(all_success_percent)

        self._place_in_grid(0, 3, tk.Label(master, text="Episodes", justify=tk.CENTER))
        self._place_in_grid(0, 4, tk.Label(master, text="Average\nProgress", justify=tk.CENTER))
        self._place_in_grid(0, 5, tk.Label(master, text="Full\nLaps", justify=tk.CENTER))
        if show_laps:
            self._place_in_grid(0, 6, tk.Label(master, text="Best\nLap", justify=tk.CENTER))
            self._place_in_grid(0, 7, tk.Label(master, text="Average\nLap", justify=tk.CENTER))

        row = 1

        for model_name in sorted(model_names):
            log = model_logs[model_name]

            callback = lambda file_name=log.get_meta_file_name(): self._callback_open_file(file_name)

            log_meta = log.get_log_meta()

            progress_percent = self._get_progress_percent(log_meta)
            success_percent = self._get_success_percent(log_meta)

            self._place_in_grid(row, 0, tk.Button(master, text=log_meta.model_name, command=callback), "E")
            self._place_in_grid(row, 1, tk.Label(master, text=log_meta.race_type), "E")
            self._place_in_grid(row, 2, tk.Label(master, text=log_meta.job_type), "E")
            self._place_in_grid(row, 3, self._make_large_integer_label(master, log_meta.episode_stats.episode_count))

            self._place_in_grid(row, 4, self._make_percent_label(master, progress_percent, best_progress_percent))
            self._place_in_grid(row, 5, self._make_percent_label(master, success_percent, best_success_percent))
            if show_laps:
                self._place_in_grid(row, 6, self._make_lap_time_label(master, log_meta.episode_stats.best_steps,
                                                                      best_best_steps))
                self._place_in_grid(row, 7, self._make_lap_time_label(master, log_meta.episode_stats.average_steps,
                                                                      best_average_steps))

            row += 1

    @staticmethod
    def _get_progress_percent(log_meta):
        return log_meta.episode_stats.average_percent_complete

    @staticmethod
    def _get_success_percent(log_meta):
        return log_meta.episode_stats.success_count / log_meta.episode_stats.episode_count * 100

    @staticmethod
    def _make_percent_label(master, value, best_value):
        formatted_text = get_pretty_whole_percentage(value)
        if value >= 0.99 * best_value:
            return tk.Label(master, text=formatted_text, background="palegreen", justify=tk.CENTER)
        elif value >= 0.98 * best_value:
            return tk.Label(master, text=formatted_text, background="lightblue1", justify=tk.CENTER)
        else:
            return tk.Label(master, text=formatted_text, justify=tk.CENTER)

    @staticmethod
    def _make_lap_time_label(master, value, best_value):
        if best_value >= 0.99 * value:
            return tk.Label(master, text=value, background="palegreen", justify=tk.CENTER)
        elif best_value >= 0.98 * value:
            return tk.Label(master, text=value, background="lightblue1", justify=tk.CENTER)
        else:
            return tk.Label(master, text=value, justify=tk.CENTER)

    @staticmethod
    def _make_large_integer_label(master, value):
        return tk.Label(master, text=get_pretty_large_integer(value), justify=tk.CENTER)

    def buttonbox(self):
        box = tk.Frame(self)

        tk.Button(box, text="Cancel", width=10, command=self.cancel).pack()

        self.bind("<Return>", self.cancel)
        self.bind("<Escape>", self.cancel)

        box.pack(pady=5)

    def apply(self):
        pass

    def validate(self):
        return True

    @staticmethod
    def _place_in_grid(row, column, widget, sticky="NSEW"):
        widget.grid(row=row, column=column, padx=7, pady=3, sticky=sticky)

    def _callback_open_file(self, file_name):
        self.cancel()
        self.parent.callback_open_this_file(file_name)
