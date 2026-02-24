# MCP Server ADS Demo
# Records an interactive Claude Code session showcasing ADS tools
#
# Prerequisites:
#   - VHS installed (https://github.com/charmbracelet/vhs)
#   - Claude CLI installed with mcp-server-ads configured
#   - ADS_API_TOKEN set in environment
#   - MCP tool permissions pre-allowed in Claude settings
#
# Run: vhs demos/demo.tape

Output demos/demo.gif
Set FontSize 14
Set Width 1200
Set Height 800
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 20

# Unset CLAUDECODE to avoid nested session detection (hidden from recording)
Hide
Type "unset CLAUDECODE"
Enter
Sleep 0.5s
Ctrl+L
Sleep 0.5s
Show

# Start Claude Code interactive mode
Type "claude"
Enter
Sleep 5s

# Prompt 1: Search for classic papers
Type "Find the most cited papers on the accelerating expansion of the universe"
Enter
Sleep 30s

# Prompt 2: Citation metrics (context carries over)
Type "Show citation metrics for the top result"
Enter
Sleep 30s

# Prompt 3: Bridge to current research
Type "What 2024 papers cite the Riess 1998 discovery? Any connection to DESI?"
Enter
Sleep 30s

Sleep 5s
