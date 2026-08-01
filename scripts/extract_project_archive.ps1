# Project archive extraction is distributed under MPL-2.0; see THIRD_PARTY_NOTICES.md.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateNotNullOrEmpty()]
    [string]$ArchivePath,

    [Parameter(Mandatory = $true, Position = 1)]
    [ValidateNotNullOrEmpty()]
    [string]$DestinationRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ArchiveKind {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    $lowerName = $FileName.ToLowerInvariant()

    if ($lowerName.EndsWith('.tar.gz') -or $lowerName.EndsWith('.tgz')) {
        return 'tar'
    }

    switch ([System.IO.Path]::GetExtension($lowerName)) {
        '.zip' { return 'zip' }
        '.7z'  { return '7zip' }
        '.rar' { return '7zip' }
        '.tar' { return 'tar' }
        default {
            throw "不支持的压缩格式：$FileName。支持 .zip、.7z、.rar、.tar、.tar.gz 和 .tgz。"
        }
    }
}

function Get-ArchiveBaseName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
    if ($FileName.ToLowerInvariant().EndsWith('.tar.gz')) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($baseName)
    }

    foreach ($invalidChar in [System.IO.Path]::GetInvalidFileNameChars()) {
        $baseName = $baseName.Replace([string]$invalidChar, '_')
    }

    $baseName = $baseName.Trim()
    if ([string]::IsNullOrWhiteSpace($baseName)) {
        return 'archive'
    }

    return $baseName
}

function Resolve-SevenZip {
    foreach ($commandName in @('7z', '7zz')) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            return $command.Source
        }
    }

    $candidates = @(
        'D:\Tools\7-Zip\7z.exe',
        'D:\Tools\7zip\7z.exe'
    )

    if ($env:ProgramFiles) {
        $candidates += Join-Path $env:ProgramFiles '7-Zip\7z.exe'
    }
    if (${env:ProgramFiles(x86)}) {
        $candidates += Join-Path ${env:ProgramFiles(x86)} '7-Zip\7z.exe'
    }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    throw '解压 .7z 或 .rar 需要 7-Zip。请将 7z.exe 安装到 D:\Tools\7-Zip，或加入 PATH。'
}

function New-ExtractionDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RootPath,

        [Parameter(Mandatory = $true)]
        [string]$BaseName
    )

    $root = New-Item -ItemType Directory -Path $RootPath -Force
    $candidate = Join-Path $root.FullName $BaseName

    if (Test-Path -LiteralPath $candidate) {
        $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $candidate = Join-Path $root.FullName "$BaseName-$timestamp"
        $counter = 2

        while (Test-Path -LiteralPath $candidate) {
            $candidate = Join-Path $root.FullName "$BaseName-$timestamp-$counter"
            $counter++
        }
    }

    return (New-Item -ItemType Directory -Path $candidate).FullName
}

$resolvedArchive = Resolve-Path -LiteralPath $ArchivePath
if (-not (Test-Path -LiteralPath $resolvedArchive.Path -PathType Leaf)) {
    throw "压缩包路径不是文件：$($resolvedArchive.Path)"
}

$archiveFile = Get-Item -LiteralPath $resolvedArchive.Path
$archiveKind = Get-ArchiveKind -FileName $archiveFile.Name
$archiveBaseName = Get-ArchiveBaseName -FileName $archiveFile.Name

$sevenZipPath = $null
$tarPath = $null
if ($archiveKind -eq '7zip') {
    $sevenZipPath = Resolve-SevenZip
}
elseif ($archiveKind -eq 'tar') {
    $tarCommand = Get-Command tar -ErrorAction SilentlyContinue
    if ($null -eq $tarCommand) {
        throw '解压 tar 归档需要 tar.exe，但当前环境中未找到。'
    }
    $tarPath = $tarCommand.Source
}

$destinationPath = New-ExtractionDirectory `
    -RootPath $DestinationRoot `
    -BaseName $archiveBaseName

try {
    switch ($archiveKind) {
        'zip' {
            Expand-Archive `
                -LiteralPath $archiveFile.FullName `
                -DestinationPath $destinationPath `
                -Force
        }
        '7zip' {
            & $sevenZipPath x $archiveFile.FullName "-o$destinationPath" -y |
                Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "7-Zip 解压失败，退出码：$LASTEXITCODE"
            }
        }
        'tar' {
            & $tarPath -xf $archiveFile.FullName -C $destinationPath |
                Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "tar 解压失败，退出码：$LASTEXITCODE"
            }
        }
    }

    $extractedItems = @(Get-ChildItem -LiteralPath $destinationPath -Force)
    if ($extractedItems.Count -eq 0) {
        throw '解压命令已完成，但目标目录中没有生成任何内容。'
    }
}
catch {
    throw "压缩包解压失败。已保留目标目录用于排查：$destinationPath`n$($_.Exception.Message)"
}

$projectRoot = $destinationPath
if ($extractedItems.Count -eq 1 -and $extractedItems[0].PSIsContainer) {
    $projectRoot = $extractedItems[0].FullName
}

Write-Output $projectRoot
