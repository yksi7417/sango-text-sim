<#
.SYNOPSIS
    Claude Code Autonomous Loop (Ralph-style)

.DESCRIPTION
    Runs Claude Code in a continuous loop for autonomous development.
    Each iteration spawns a fresh context to avoid context rot.
    The loop continues until all tasks are complete or max iterations reached.

.PARAMETER MaxIterations
    Maximum number of loop iterations (default: 100)

.PARAMETER Model
    Claude model to use: haiku, sonnet, opus (default: sonnet)

.PARAMETER DelaySeconds
    Delay between iterations in seconds (default: 5)

.PARAMETER LogFile
    Path to log file (default: .ai/loop.log)

.EXAMPLE
    .\.ai\loop.ps1
    .\.ai\loop.ps1 -MaxIterations 50 -Model opus
    .\.ai\loop.ps1 -DelaySeconds 10

.NOTES
    Based on Ralph methodology: https://ghuntley.com/ralph/
    Press Ctrl+C to stop the loop gracefully.
#>

param(
    [int]$MaxIterations = 100,
    [string]$Model = "sonnet",
    [int]$DelaySeconds = 5,
    [string]$LogFile = ".ai\loop.log"
)

# Configuration
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# ANSI Colors for terminal output
$Colors = @{
    Reset   = "`e[0m"
    Red     = "`e[31m"
    Green   = "`e[32m"
    Yellow  = "`e[33m"
    Blue    = "`e[34m"
    Magenta = "`e[35m"
    Cyan    = "`e[36m"
    Bold    = "`e[1m"
    Dim     = "`e[2m"
}

function Write-ColorLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoNewline
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO"    { $Colors.Cyan }
        "SUCCESS" { $Colors.Green }
        "WARNING" { $Colors.Yellow }
        "ERROR"   { $Colors.Red }
        "TASK"    { $Colors.Magenta }
        "METRIC"  { $Colors.Blue }
        default   { $Colors.Reset }
    }

    $logMessage = "[$timestamp] [$Level] $Message"
    $colorMessage = "$($Colors.Dim)[$timestamp]$($Colors.Reset) $color[$Level]$($Colors.Reset) $Message"

    # Write to console
    if ($NoNewline) {
        Write-Host $colorMessage -NoNewline
    } else {
        Write-Host $colorMessage
    }

    # Append to log file
    Add-Content -Path $LogFile -Value $logMessage
}

function Get-TaskSummary {
    $tasksFile = ".ai\tasks.json"
    if (-not (Test-Path $tasksFile)) {
        return @{ Total = 0; Pending = 0; Passed = 0 }
    }

    try {
        $tasks = Get-Content $tasksFile -Raw | ConvertFrom-Json
        $total = $tasks.tasks.Count
        $pending = ($tasks.tasks | Where-Object { $_.status -eq "pending" }).Count
        $passed = ($tasks.tasks | Where-Object { $_.status -eq "passed" }).Count
        return @{ Total = $total; Pending = $pending; Passed = $passed }
    } catch {
        return @{ Total = 0; Pending = 0; Passed = 0 }
    }
}

function Get-PromptContent {
    $claudeFile = ".ai\CLAUDE.md"
    $tasksFile = ".ai\tasks.json"
    $progressFile = ".ai\progress.txt"

    $prompt = @"
# Autonomous Development Session

Read and follow instructions in .ai/CLAUDE.md

## Current Task Status
$(if (Test-Path $tasksFile) { Get-Content $tasksFile -Raw } else { "No tasks.json found" })

## Recent Progress
$(if (Test-Path $progressFile) { Get-Content $progressFile -Tail 20 } else { "No progress.txt found" })

## Instructions
1. Read .ai/CLAUDE.md for full instructions
2. Select the highest priority pending task from tasks.json
3. Implement the task following all quality standards
4. Run tests: python -m pytest --no-cov -v
5. If tests pass, commit changes and update task status to "passed"
6. Log learnings to .ai/progress.txt
7. If ALL tasks are complete, output: <promise>COMPLETE</promise>

Begin autonomous development.
"@

    return $prompt
}

function Test-CompletionSignal {
    param([string]$Output)
    return $Output -match "<promise>COMPLETE</promise>"
}

function Update-ProgressLog {
    param(
        [int]$Iteration,
        [string]$Status,
        [string]$Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    $entry = "[$timestamp] [ITER-$Iteration] [$Status] $Message"
    Add-Content -Path ".ai\progress.txt" -Value $entry
}

function Show-Banner {
    $banner = @"
$($Colors.Cyan)
 ╔═══════════════════════════════════════════════════════════╗
 ║       Claude Code Autonomous Loop (Ralph-style)           ║
 ║                                                           ║
 ║  Each iteration spawns fresh context for clean execution  ║
 ║  Press Ctrl+C to stop gracefully                          ║
 ╚═══════════════════════════════════════════════════════════╝
$($Colors.Reset)
"@
    Write-Host $banner
}

function Show-IterationHeader {
    param([int]$Iteration, [int]$Max)

    $taskSummary = Get-TaskSummary
    $separator = "═" * 60

    Write-Host ""
    Write-Host "$($Colors.Bold)$($Colors.Blue)$separator$($Colors.Reset)"
    Write-Host "$($Colors.Bold)  ITERATION $Iteration / $Max$($Colors.Reset)"
    Write-Host "$($Colors.Dim)  Tasks: $($taskSummary.Passed)/$($taskSummary.Total) passed, $($taskSummary.Pending) pending$($Colors.Reset)"
    Write-Host "$($Colors.Dim)  Model: $Model | Time: $(Get-Date -Format 'HH:mm:ss')$($Colors.Reset)"
    Write-Host "$($Colors.Bold)$($Colors.Blue)$separator$($Colors.Reset)"
    Write-Host ""
}

# Main execution
Show-Banner

Write-ColorLog "Starting autonomous loop" -Level "INFO"
Write-ColorLog "Max iterations: $MaxIterations" -Level "INFO"
Write-ColorLog "Model: $Model" -Level "INFO"
Write-ColorLog "Log file: $LogFile" -Level "INFO"

# Ensure .ai directory exists
if (-not (Test-Path ".ai")) {
    New-Item -ItemType Directory -Path ".ai" -Force | Out-Null
}

# Initialize log file
if (-not (Test-Path $LogFile)) {
    $null = New-Item -ItemType File -Path $LogFile -Force
}

$iteration = 0
$startTime = Get-Date
$totalComplete = $false

try {
    while ($iteration -lt $MaxIterations -and -not $totalComplete) {
        $iteration++
        $iterationStart = Get-Date

        Show-IterationHeader -Iteration $iteration -Max $MaxIterations

        Write-ColorLog "Preparing prompt for iteration $iteration" -Level "TASK"

        # Get the prompt content
        $prompt = Get-PromptContent

        # Create a temporary file for the prompt
        $tempPromptFile = [System.IO.Path]::GetTempFileName()
        $prompt | Out-File -FilePath $tempPromptFile -Encoding UTF8

        Write-ColorLog "Spawning Claude Code with fresh context..." -Level "INFO"
        Update-ProgressLog -Iteration $iteration -Status "START" -Message "Beginning iteration"

        try {
            # Run Claude Code with the prompt
            # Using --print for non-interactive mode, piping the prompt
            $output = Get-Content $tempPromptFile | claude --model $Model --print --dangerously-skip-permissions 2>&1

            $exitCode = $LASTEXITCODE
            $iterationEnd = Get-Date
            $duration = ($iterationEnd - $iterationStart).TotalSeconds

            # Display output (Claude's thinking, tools, and responses)
            Write-Host ""
            Write-Host "$($Colors.Dim)--- Claude Output ---$($Colors.Reset)"
            Write-Host $output
            Write-Host "$($Colors.Dim)--- End Output ---$($Colors.Reset)"
            Write-Host ""

            # Check for completion signal
            if (Test-CompletionSignal -Output $output) {
                $totalComplete = $true
                Write-ColorLog "COMPLETE signal received! All tasks finished." -Level "SUCCESS"
                Update-ProgressLog -Iteration $iteration -Status "COMPLETE" -Message "All tasks completed successfully"
            } elseif ($exitCode -eq 0) {
                Write-ColorLog "Iteration $iteration completed in $([math]::Round($duration, 1))s" -Level "SUCCESS"
                Update-ProgressLog -Iteration $iteration -Status "SUCCESS" -Message "Completed in $([math]::Round($duration, 1))s"
            } else {
                Write-ColorLog "Iteration $iteration had issues (exit code: $exitCode)" -Level "WARNING"
                Update-ProgressLog -Iteration $iteration -Status "WARNING" -Message "Exit code: $exitCode"
            }


            # Show metrics
            Write-ColorLog "Duration: $([math]::Round($duration, 1))s" -Level "METRIC"

            # Auto-commit and push if there are changes
            Write-ColorLog "Checking for code changes to commit..." -Level "INFO"
            $status = git status --porcelain
            if ($status) {
                git add -A
                $commitMsg = "loop.ps1: auto-commit after iteration $iteration"
                git commit -m $commitMsg
                Write-ColorLog "Committed changes: $commitMsg" -Level "SUCCESS"
                git push
                Write-ColorLog "Pushed changes to remote." -Level "SUCCESS"
            } else {
                Write-ColorLog "No changes to commit." -Level "INFO"
            }

        } catch {
            Write-ColorLog "Error in iteration $iteration`: $_" -Level "ERROR"
            Update-ProgressLog -Iteration $iteration -Status "ERROR" -Message $_.ToString()
        } finally {
            # Clean up temp file
            if (Test-Path $tempPromptFile) {
                Remove-Item $tempPromptFile -Force
            }
        }

        # Delay before next iteration (unless complete)
        if (-not $totalComplete -and $iteration -lt $MaxIterations) {
            Write-ColorLog "Waiting $DelaySeconds seconds before next iteration..." -Level "INFO"
            Start-Sleep -Seconds $DelaySeconds
        }
    }
} finally {
    $endTime = Get-Date
    $totalDuration = ($endTime - $startTime).TotalMinutes

    Write-Host ""
    Write-Host "$($Colors.Bold)$($Colors.Cyan)═══════════════════════════════════════════════════════════$($Colors.Reset)"
    Write-Host "$($Colors.Bold)  LOOP SUMMARY$($Colors.Reset)"
    Write-Host "$($Colors.Cyan)═══════════════════════════════════════════════════════════$($Colors.Reset)"

    $taskSummary = Get-TaskSummary
    Write-ColorLog "Total iterations: $iteration" -Level "METRIC"
    Write-ColorLog "Total duration: $([math]::Round($totalDuration, 1)) minutes" -Level "METRIC"
    Write-ColorLog "Tasks completed: $($taskSummary.Passed)/$($taskSummary.Total)" -Level "METRIC"

    if ($totalComplete) {
        Write-ColorLog "Status: ALL TASKS COMPLETE" -Level "SUCCESS"
    } elseif ($iteration -ge $MaxIterations) {
        Write-ColorLog "Status: Max iterations reached" -Level "WARNING"
    } else {
        Write-ColorLog "Status: Loop interrupted" -Level "WARNING"
    }

    Write-Host "$($Colors.Cyan)═══════════════════════════════════════════════════════════$($Colors.Reset)"
}
