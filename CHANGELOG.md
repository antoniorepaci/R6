# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.1.0] - 2026-06-03

### Added
- **Paste button** to the right of the URL field for quickly pasting a link from the clipboard.
- **Context menu** (right-click) on the URL field with a localised "Paste / Incolla" entry (English & Italian).
- **Automatic JS runtime detection** (Node.js / Deno): if found in the system PATH, it is passed automatically to yt-dlp, eliminating the related deprecation warning.

### Fixed
- `ffmpeg.exe` not found on other devices: corrected the frozen-mode path (PyInstaller) that was incorrectly going one directory above `_MEIPASS`.
- Double `ERROR: ERROR:` prefix in the log: both the logger and `_on_download_error` now strip the prefix already included by yt-dlp in the exception message.
- JavaScript runtime warning suppressed in the app log (handled internally via auto-detection).

### Build
- Added `main.spec` for PyInstaller builds: automatically bundles `ffmpeg.exe`, images and `settings.json`.
- Added `build.ps1` as a quick build script (`.\build.ps1`).

---

## [1.0.0] - 2026-06-02

### Changed
- `settings.json` is now stored in `C:\ProgramData\R6\settings.json` instead of the app/executable directory.
  This location is shared between all users on the same machine and does not require administrator privileges.
  The folder is created automatically on first run.

