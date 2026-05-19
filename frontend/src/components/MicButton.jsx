import { useRef, useState } from "react";
import { transcribeAudio } from "../api/apiClient";

/**
 * Push-to-talk mic button.
 *
 * Click once to start recording, click again to stop.
 * On stop, uploads the audio blob to /transcribe-audio and hands the
 * transcript text back via onTranscript(text).
 *
 * States:
 *   idle         - mic icon
 *   recording    - red pulsing icon
 *   transcribing - spinner
 */
export default function MicButton({ onTranscript, disabled }) {
  const [state, setState] = useState("idle");
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        // Stop the mic stream so the browser tab indicator clears.
        stream.getTracks().forEach((t) => t.stop());

        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setState("transcribing");

        try {
          const transcript = await transcribeAudio(blob);
          onTranscript(transcript);
        } catch (err) {
          console.error("Transcription failed:", err);
          alert("Could not transcribe audio. Please try again.");
        } finally {
          setState("idle");
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setState("recording");
    } catch (err) {
      console.error("Mic access denied:", err);
      alert("Microphone access denied. Please allow microphone access in your browser settings.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
  };

  const handleClick = () => {
    if (state === "idle") startRecording();
    else if (state === "recording") stopRecording();
  };

  const isBusy = state === "transcribing";

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || isBusy}
      title={
        state === "idle"
          ? "Record voice"
          : state === "recording"
            ? "Stop recording"
            : "Transcribing..."
      }
      className={`
        flex items-center justify-center w-10 h-10 rounded-full transition-all
        disabled:opacity-40 disabled:cursor-not-allowed
        ${state === "recording"
          ? "bg-red-500 text-white animate-pulse-mic"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-brand-600 border border-slate-200"}
      `}
    >
      {state === "transcribing" ? (
        <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.25" />
          <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        </svg>
      ) : state === "recording" ? (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      ) : (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="2" width="6" height="12" rx="3" />
          <path d="M5 10v2a7 7 0 0 0 14 0v-2" />
          <line x1="12" y1="19" x2="12" y2="22" />
          <line x1="8" y1="22" x2="16" y2="22" />
        </svg>
      )}
    </button>
  );
}
