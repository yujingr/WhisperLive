import tkinter as tk
from tkinter import ttk, filedialog
import threading
import os
from whisper_live.client import TranscriptionClient


class WhisperLiveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhisperLive Client")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.client = None
        self.create_widgets()

    def create_widgets(self):
        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")

        # Connection settings
        ttk.Label(settings_frame, text="Server Connection", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(10, 5), padx=10)

        ttk.Label(settings_frame, text="Host:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(settings_frame, textvariable=self.host_var, width=30).grid(
            row=1, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(settings_frame, text="Port:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        self.port_var = tk.IntVar(value=9090)
        ttk.Entry(settings_frame, textvariable=self.port_var, width=10).grid(
            row=2, column=1, sticky="w", padx=10, pady=5)

        # Transcription settings
        ttk.Label(settings_frame, text="Transcription Settings", font=("Arial", 14, "bold")).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(20, 5), padx=10)

        ttk.Label(settings_frame, text="Language:").grid(
            row=4, column=0, sticky="w", padx=10, pady=5)
        self.lang_var = tk.StringVar(value="en")
        ttk.Entry(settings_frame, textvariable=self.lang_var, width=10).grid(
            row=4, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(settings_frame, text="Model:").grid(
            row=5, column=0, sticky="w", padx=10, pady=5)
        self.model_var = tk.StringVar(value="small")
        model_combo = ttk.Combobox(
            settings_frame, textvariable=self.model_var, width=20)
        model_combo['values'] = (
            'tiny', 'base', 'small', 'medium', 'large', 'small.en', 'medium.en')
        model_combo.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        self.translate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Translate to English", variable=self.translate_var).grid(
            row=6, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        self.vad_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Use Voice Activity Detection", variable=self.vad_var).grid(
            row=7, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Recording settings
        ttk.Label(settings_frame, text="Recording Settings", font=("Arial", 14, "bold")).grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(20, 5), padx=10)

        self.save_recording_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Save Recording", variable=self.save_recording_var).grid(
            row=9, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        ttk.Label(settings_frame, text="Output Recording:").grid(
            row=10, column=0, sticky="w", padx=10, pady=5)
        self.output_recording_var = tk.StringVar(
            value="./output_recording.wav")
        output_recording_frame = ttk.Frame(settings_frame)
        output_recording_frame.grid(
            row=10, column=1, sticky="w", padx=10, pady=5)
        ttk.Entry(output_recording_frame,
                  textvariable=self.output_recording_var, width=30).pack(side=tk.LEFT)
        ttk.Button(output_recording_frame, text="Browse",
                   command=self.browse_output_recording).pack(side=tk.LEFT, padx=5)

        ttk.Label(settings_frame, text="Output Transcription:").grid(
            row=11, column=0, sticky="w", padx=10, pady=5)
        self.output_transcription_var = tk.StringVar(value="./output.srt")
        output_transcription_frame = ttk.Frame(settings_frame)
        output_transcription_frame.grid(
            row=11, column=1, sticky="w", padx=10, pady=5)
        ttk.Entry(output_transcription_frame,
                  textvariable=self.output_transcription_var, width=30).pack(side=tk.LEFT)
        ttk.Button(output_transcription_frame, text="Browse",
                   command=self.browse_output_transcription).pack(side=tk.LEFT, padx=5)

        # Control buttons
        control_frame = ttk.Frame(settings_frame)
        control_frame.grid(row=12, column=0, columnspan=2, pady=20)

        self.connect_button = ttk.Button(
            control_frame, text="Connect Microphone", command=self.start_transcription)
        self.connect_button.pack(side=tk.LEFT, padx=10)

        self.file_button = ttk.Button(
            control_frame, text="Transcribe File", command=self.transcribe_file)
        self.file_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(
            control_frame, text="Stop", command=self.stop_transcription, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Transcription output tab
        self.output_frame = ttk.Frame(notebook)
        notebook.add(self.output_frame, text="Transcription Output")

        self.output_text = tk.Text(
            self.output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(expand=True, fill="both", padx=10, pady=10)

        # Add scrollbar to text widget
        scrollbar = ttk.Scrollbar(
            self.output_text, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_output_recording(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if filename:
            self.output_recording_var.set(filename)

    def browse_output_transcription(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".srt",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if filename:
            self.output_transcription_var.set(filename)

    def transcribe_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg"),
                       ("All files", "*.*")]
        )
        if not filename:
            return

        self.start_transcription(audio_file=filename)

    def start_transcription(self, audio_file=None):
        # Disable buttons
        self.connect_button.config(state=tk.DISABLED)
        self.file_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Clear output
        self.output_text.delete(1.0, tk.END)

        # Update status
        self.status_var.set("Connecting to server...")

        # Switch to output tab
        notebook = self.output_text.master.master
        notebook.select(1)  # Select the output tab (index 1)

        # Create and start client in a separate thread
        self.transcription_thread = threading.Thread(
            target=self._run_transcription, args=(audio_file,))
        self.transcription_thread.daemon = True
        self.transcription_thread.start()

        # Start monitoring the transcription output
        self.root.after(100, self.update_transcription_output)

    def _run_transcription(self, audio_file=None):
        try:
            # Create client
            self.client = TranscriptionClient(
                host=self.host_var.get(),
                port=self.port_var.get(),
                lang=self.lang_var.get(),
                translate=self.translate_var.get(),
                model=self.model_var.get(),
                use_vad=self.vad_var.get(),
                save_output_recording=self.save_recording_var.get(),
                output_recording_filename=self.output_recording_var.get(),
                output_transcription_path=self.output_transcription_var.get(),
                log_transcription=False,  # We'll handle this ourselves
            )

            # Update status to show connection is successful
            self.status_var.set("Connected to server")

            # Start transcription
            if audio_file:
                self.client(audio_file)
            else:
                self.client()

            # Update status when done
            self.status_var.set("Transcription completed")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            # Re-enable buttons
            self.root.after(0, self._reset_buttons)

    def _reset_buttons(self):
        self.connect_button.config(state=tk.NORMAL)
        self.file_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_transcription_output(self):
        """Update the transcription output text periodically"""
        updated = False

        if self.client and hasattr(self.client, 'client'):
            # Display completed segments from transcript
            if hasattr(self.client.client, 'transcript') and self.client.client.transcript:
                self.output_text.delete(1.0, tk.END)
                for segment in self.client.client.transcript:
                    if 'text' in segment:
                        # Format: [00:00:00 -> 00:00:00] Text
                        start = self.format_time(
                            float(segment.get('start', 0)))
                        end = self.format_time(float(segment.get('end', 0)))
                        text = segment['text'].strip()
                        self.output_text.insert(
                            tk.END, f"[{start} -> {end}] {text}\n\n")
                        updated = True

            # Display the last segment (which might not be completed yet)
            if hasattr(self.client.client, 'last_segment') and self.client.client.last_segment:
                if not updated:
                    self.output_text.delete(1.0, tk.END)
                if 'text' in self.client.client.last_segment:
                    start = self.format_time(
                        float(self.client.client.last_segment.get('start', 0)))
                    text = self.client.client.last_segment['text'].strip()
                    self.output_text.insert(tk.END, f"[Current] {text}\n")
                    updated = True

            # Display the last received segment if nothing else is available
            if not updated and hasattr(self.client.client, 'last_received_segment') and self.client.client.last_received_segment:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(
                    tk.END, f"[Live] {self.client.client.last_received_segment}\n")
                updated = True

            # Scroll to the end of the text widget
            if updated:
                self.output_text.see(tk.END)

        # Schedule next update if client is still active
        active = self.client and hasattr(self.client, 'client') and hasattr(
            self.client.client, 'recording') and self.client.client.recording
        if active:
            self.root.after(300, self.update_transcription_output)
        else:
            # One final update after recording stops
            self.root.after(1000, self.update_transcription_output_once)

    def update_transcription_output_once(self):
        """One final update after recording stops"""
        self.update_transcription_output()

    def format_time(self, seconds):
        """Format seconds to HH:MM:SS"""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

    def stop_transcription(self):
        """Stop the transcription"""
        if self.client:
            # Stop recording in all clients
            if hasattr(self.client, 'client'):
                self.client.client.recording = False

            self.status_var.set("Transcription stopped")
            self._reset_buttons()


if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperLiveGUI(root)
    root.mainloop()
