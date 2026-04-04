"""Maribox TUI theme — dark theme inspired by OpenCode's design system."""

# ── Color palette ──────────────────────────────────────────────────────────

COLORS = {
    # Base
    "background": "#0d0f14",
    "background_secondary": "#141720",
    "background_darker": "#090a0e",
    "surface": "#1a1e28",
    "panel": "#1e2233",

    # Text
    "text": "#c8cdd8",
    "text_muted": "#5c6370",
    "text_emphasized": "#e8ecf2",
    "text_secondary": "#8b92a0",

    # Accent
    "primary": "#6c8aff",
    "primary_dim": "#3a4f99",
    "secondary": "#9b7aff",
    "accent": "#ff7a6c",

    # Status
    "success": "#7aff8c",
    "warning": "#ffc46c",
    "error": "#ff6c7a",
    "info": "#6cc8ff",

    # Diff
    "added": "#3d5a3d",
    "added_text": "#7aff8c",
    "removed": "#5a3d3d",
    "removed_text": "#ff6c7a",

    # Borders
    "border": "#2a2f3d",
    "border_focused": "#6c8aff",
    "border_dim": "#1a1e28",

    # Message roles
    "user_border": "#6c8aff",
    "assistant_border": "#9b7aff",
    "tool_border": "#5c6370",

    # Markdown
    "heading": "#6c8aff",
    "link": "#6cc8ff",
    "code_bg": "#141720",
    "code_text": "#ff7a6c",
    "blockquote": "#5c6370",
}

# ── App-level CSS ──────────────────────────────────────────────────────────

APP_CSS = """
/* ── Base ─────────────────────────────────────────────────────────── */
Screen {
    background: $background;
    color: $text;
}

/* ── Header / Title bar ──────────────────────────────────────────── */
#title-bar {
    background: $background-secondary;
    height: 1;
    padding: 0 2;
    dock: top;
}

#title-bar .title {
    color: $primary;
    text-style: bold;
}

#title-bar .subtitle {
    color: $text-muted;
    margin-left: 2;
}

/* ── Status bar (bottom) ─────────────────────────────────────────── */
#status-bar {
    background: $background-secondary;
    height: 1;
    padding: 0 2;
    dock: bottom;
}

#status-bar .help-hint {
    color: $text-muted;
    text-style: bold;
}

#status-bar .info-message {
    color: $info;
    margin-left: 2;
}

#status-bar .model-name {
    color: $text-secondary;
    dock: right;
}

#status-bar .token-usage {
    color: $text-muted;
    dock: right;
    margin-right: 2;
}

/* ── Chat layout ─────────────────────────────────────────────────── */
#chat-layout {
    layout: vertical;
    height: 1fr;
}

/* ── Main content area (messages + sidebar) ──────────────────────── */
#main-area {
    layout: horizontal;
    height: 1fr;
}

/* ── Messages list ───────────────────────────────────────────────── */
#messages-panel {
    width: 1fr;
    height: 1fr;
    overflow-y: auto;
    padding: 1 2;
}

#messages-panel:focus {
    border: none;
}

/* ── Welcome screen ──────────────────────────────────────────────── */
#welcome-screen {
    padding: 4 6;
    height: auto;
    margin: 2 4;
}

#welcome-screen .logo {
    color: $primary;
    text-style: bold;
    margin-bottom: 1;
}

#welcome-screen .version {
    color: $text-muted;
    margin-bottom: 2;
}

#welcome-screen .cwd-info {
    color: $text-secondary;
    margin-bottom: 2;
}

#welcome-screen .provider-info {
    color: $text-secondary;
}

#welcome-screen .help-keys {
    color: $text-muted;
    margin-top: 2;
}

/* ── Message items ───────────────────────────────────────────────── */
.message-item {
    margin: 0 0 1 0;
    padding: 1 2;
    height: auto;
}

.user-message {
    border-left: outer $primary;
    padding-left: 1;
}

.assistant-message {
    border-left: outer $secondary;
    padding-left: 1;
}

.tool-message {
    border-left: outer $text-muted;
    padding-left: 1;
    color: $text-muted;
}

.message-role {
    text-style: bold;
    margin-bottom: 1;
}

.message-role.user {
    color: $primary;
}

.message-role.assistant {
    color: $secondary;
}

.message-role.tool {
    color: $text-muted;
}

.message-content {
    color: $text;
}

.message-meta {
    color: $text-muted;
    text-style: italic;
    margin-top: 1;
}

/* ── Sidebar ─────────────────────────────────────────────────────── */
#sidebar {
    width: 32;
    height: 1fr;
    background: $background-secondary;
    border-left: solid $border;
    padding: 1 1;
    display: none;
}

#sidebar.visible {
    display: block;
}

#sidebar .sidebar-title {
    color: $primary;
    text-style: bold;
    margin-bottom: 1;
}

#sidebar .section-label {
    color: $text-secondary;
    text-style: bold;
    margin-top: 1;
    margin-bottom: 0;
}

#sidebar .sidebar-item {
    color: $text;
    padding: 0 1;
}

#sidebar .sidebar-item.dim {
    color: $text-muted;
}

/* ── Input area ──────────────────────────────────────────────────── */
#input-area {
    height: auto;
    max-height: 12;
    min-height: 5;
    background: $background-secondary;
    border-top: solid $border;
    padding: 1 2;
}

#input-area:focus-within {
    border-top: solid $primary;
}

#input-prompt {
    color: $primary;
    text-style: bold;
    margin-right: 1;
}

#message-input {
    height: auto;
    max-height: 8;
    min-height: 3;
    background: $background-secondary;
    border: none;
    padding: 0;
}

#message-input:focus {
    border: none;
}

#input-hint {
    color: $text-muted;
    dock: bottom;
    height: 1;
    padding: 0 2;
}

/* ── Spinner ─────────────────────────────────────────────────────── */
#thinking-indicator {
    color: $secondary;
    padding: 1 2;
    display: none;
}

#thinking-indicator.visible {
    display: block;
}

/* ── Session list (sidebar mode) ─────────────────────────────────── */
.session-item {
    padding: 0 1;
    margin: 0;
    height: 1;
}

.session-item:hover {
    background: $surface;
}

.session-item.active {
    background: $primary-dim;
    color: $text-emphasized;
}

.session-item .session-id {
    color: $primary;
    margin-right: 1;
}

.session-item .session-name {
    color: $text;
}

.session-item .session-status {
    dock: right;
}

.session-item .session-status.running {
    color: $success;
}

.session-item .session-status.idle {
    color: $warning;
}

.session-item .session-status.stopped {
    color: $text-muted;
}

.session-item .session-status.error {
    color: $error;
}

/* ── Help overlay ────────────────────────────────────────────────── */
HelpScreen {
    align: center middle;
}

#help-container {
    background: $surface;
    border: thick $primary;
    padding: 1 3;
    width: 72;
    height: auto;
    max-height: 28;
}

#help-container .help-title {
    color: $primary;
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

#help-container .key-section {
    margin-bottom: 1;
}

#help-container .key-section .section-label {
    color: $secondary;
    text-style: bold;
}

#help-container .key-row {
    color: $text;
}

#help-container .key-row .key {
    color: $primary;
    text-style: bold;
    min-width: 16;
}

#help-container .key-row .desc {
    color: $text-muted;
}

/* ── Session switcher ────────────────────────────────────────────── */
SessionSwitcher {
    align: center middle;
}

#session-switcher-container {
    background: $surface;
    border: thick $primary;
    padding: 1 2;
    width: 60;
    height: auto;
    max-height: 20;
}

#session-switcher-container .switcher-title {
    color: $primary;
    text-style: bold;
    margin-bottom: 1;
}

/* ── Command palette ─────────────────────────────────────────────── */
CommandPalette {
    align: center middle;
}

#command-palette-container {
    background: $surface;
    border: thick $primary;
    padding: 1 2;
    width: 60;
    height: auto;
    max-height: 20;
}

#command-palette-container .palette-title {
    color: $primary;
    text-style: bold;
    margin-bottom: 1;
}

#command-filter {
    margin-bottom: 1;
}

/* ── Model selector ──────────────────────────────────────────────── */
ModelSelector {
    align: center middle;
}

#model-selector-container {
    background: $surface;
    border: thick $primary;
    padding: 1 2;
    width: 60;
    height: auto;
    max-height: 16;
}

#model-selector-container .selector-title {
    color: $primary;
    text-style: bold;
    margin-bottom: 1;
}
"""
