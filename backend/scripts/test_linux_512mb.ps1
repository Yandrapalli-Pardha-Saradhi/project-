param(
    [int]$Port = 18001,
    [string]$Image = "temple-heritage-api:onnx",
    [string]$Container = "temple-heritage-512mb-check"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repoRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI is unavailable. Install and start Docker Desktop, enable its Linux container engine, then rerun this script."
}

& docker build --file backend/Dockerfile --tag $Image backend
if ($LASTEXITCODE -ne 0) { throw "Docker image build failed ($LASTEXITCODE)." }

$existing = & docker ps --all --quiet --filter "name=^/${Container}$"
if ($existing) {
    & docker rm --force $Container | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not remove the previous test container." }
}
$publish = "${Port}:10000"
$startupTimer = [System.Diagnostics.Stopwatch]::StartNew()
$runArgs = @(
    "run", "--detach", "--name", $Container,
    "--memory=512m", "--memory-swap=512m",
    "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=384m",
    "--publish", $publish,
    "--env", "LLM_API_KEY=",
    "--env", "LLM_MODEL=",
    "--env", "WEB_SEARCH_ENABLED=false",
    $Image
)
& docker @runArgs
if ($LASTEXITCODE -ne 0) { throw "Docker container failed to start ($LASTEXITCODE)." }

function Get-CgroupSnapshot([string]$Stage) {
    Write-Host "--- cgroup stage: $Stage ---"
    try {
        & docker exec $Container sh -c 'printf "process: "; grep VmRSS /proc/1/status || true; for f in /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.peak /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.swap.current /sys/fs/cgroup/memory.swap.max /sys/fs/cgroup/memory.events; do if [ -r "$f" ]; then echo "$f"; cat "$f"; fi; done'
    } catch {
        Write-Host "Container is no longer running; current cgroup files cannot be read."
    }
}

$healthy = $false
for ($i = 0; $i -lt 120; $i++) {
    $state = (& docker inspect --format '{{.State.Status}}' $Container 2>$null)
    if ($state -ne "running") { break }
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2
        $healthy = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $healthy) {
    Write-Host "Container state / OOM status:"
    & docker inspect --format 'state={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' $Container
    Get-CgroupSnapshot "startup failure"
    & docker logs $Container
    throw "Container did not become healthy within 120 seconds."
}
$startupTimer.Stop()
Write-Host "Startup to healthy endpoint: $([math]::Round($startupTimer.Elapsed.TotalSeconds, 2)) seconds"

Write-Host "Health response:"
$health | ConvertTo-Json -Depth 5
Get-CgroupSnapshot "startup, Chroma validation and ONNX warmup"

$payload = @{ question = "What architectural features are documented for Brihadeeswarar Temple?"; language = "en" } | ConvertTo-Json -Compress
try {
    $first = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/chat" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 120
} catch {
    Write-Host "First retrieval/chat request failed: $_"
    & docker inspect --format 'state={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' $Container
    Get-CgroupSnapshot "first retrieval/chat request failure"
    & docker logs $Container
    throw
}
Write-Host "Retrieval smoke request: HTTP 200; citations=$($first.citations.Count); insufficient=$($first.insufficient_evidence); generation_disabled=$($first.generation_disabled)"
Get-CgroupSnapshot "after first retrieval/chat request"

try {
    $second = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/chat" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 120
} catch {
    Write-Host "Repeated chat request failed: $_"
    & docker inspect --format 'state={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' $Container
    Get-CgroupSnapshot "repeated chat request failure"
    & docker logs $Container
    throw
}
Write-Host "Repeated chat request: HTTP 200; citations=$($second.citations.Count); generation_disabled=$($second.generation_disabled)"
Get-CgroupSnapshot "after repeated chat request"

Write-Host "Container state / OOM status:"
& docker inspect --format 'state={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}} memory={{.HostConfig.Memory}} memorySwap={{.HostConfig.MemorySwap}}' $Container
Write-Host "Application memory-stage logs:"
& docker logs $Container 2>&1 | Select-String "MEMORY_STAGE"
Write-Host "Complete logs: docker logs $Container"
Write-Host "Container left running for inspection; stop it with: docker rm -f $Container"
