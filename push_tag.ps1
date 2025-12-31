# Git Tag 推送脚本
# 功能：读取 version 文件，如果版本比 Git 最新 tag 新，则创建并推送新 tag
#
# 使用方法：
#   .\push_tag.ps1                                    # 正常使用，会询问是否提交和推送代码
#   .\push_tag.ps1 -CommitMessage "更新版本到 v0.8.7"  # 自动提交（如果提供提交信息）
#   .\push_tag.ps1 -Force                            # 强制模式，即使版本相同或更旧也会创建 tag
#   .\push_tag.ps1 -CommitMessage "更新" -Force      # 组合使用

param(
    [switch]$Force,  # 强制推送，即使版本相同或更旧
    [string]$CommitMessage = ""  # 提交信息，如果提供则自动提交而不询问
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($message) {
    Write-ColorOutput Green $message
}

function Write-Warning($message) {
    Write-ColorOutput Yellow $message
}

function Write-Error($message) {
    Write-ColorOutput Red $message
}

function Write-Info($message) {
    Write-Output $message
}

# 读取 version 文件
function Get-VersionFromFile {
    $versionFile = Join-Path $PSScriptRoot "version"
    
    if (-not (Test-Path $versionFile)) {
        throw "version 文件不存在: $versionFile"
    }
    
    $versionContent = Get-Content $versionFile -Raw -Encoding UTF8
    $versionContent = $versionContent.Trim()
    
    if ([string]::IsNullOrWhiteSpace($versionContent)) {
        throw "version 文件为空"
    }
    
    return $versionContent
}

# 获取 Git 最新 tag
function Get-LatestGitTag {
    try {
        # 获取所有 tag，按版本排序，取最新的
        $tags = git tag -l "v*" | ForEach-Object {
            # 移除 'v' 前缀，转换为 Version 对象用于排序
            $versionStr = $_ -replace '^v', ''
            try {
                [PSCustomObject]@{
                    Tag = $_
                    Version = [version]$versionStr
                }
            } catch {
                # 如果无法解析为版本号，跳过
                $null
            }
        } | Where-Object { $null -ne $_ } | Sort-Object -Property Version -Descending
        
        if ($tags.Count -eq 0) {
            return $null
        }
        
        return $tags[0].Tag
    } catch {
        Write-Warning "获取 Git tag 时出错: $_"
        return $null
    }
}

# 比较版本号（返回：-1 表示 version1 < version2，0 表示相等，1 表示 version1 > version2）
function Compare-Version($version1, $version2) {
    # 移除 'v' 前缀
    $v1 = $version1 -replace '^v', ''
    $v2 = $version2 -replace '^v', ''
    
    try {
        $ver1 = [version]$v1
        $ver2 = [version]$v2
        
        if ($ver1 -lt $ver2) {
            return -1
        } elseif ($ver1 -eq $ver2) {
            return 0
        } else {
            return 1
        }
    } catch {
        # 如果无法解析为版本号，使用字符串比较
        Write-Warning "无法解析版本号，使用字符串比较: $version1 vs $version2"
        if ($v1 -lt $v2) {
            return -1
        } elseif ($v1 -eq $v2) {
            return 0
        } else {
            return 1
        }
    }
}

# 处理代码提交和推送
function Process-CommitAndPush {
    param(
        [string]$CommitMessage
    )
    
    # 检查工作区状态
    $status = git status --porcelain
    $hasChanges = $status -ne $null -and $status.Count -gt 0
    
    if ($hasChanges) {
        Write-Warning "检测到未提交的更改："
        Write-Info $status
        Write-Info ""
        
        $shouldCommit = $false
        $finalCommitMessage = ""
        
        # 如果通过参数提供了提交信息，自动提交
        if (-not [string]::IsNullOrWhiteSpace($CommitMessage)) {
            $shouldCommit = $true
            $finalCommitMessage = $CommitMessage
            Write-Info "使用命令行参数提供的提交信息: $finalCommitMessage"
        } else {
            # 否则询问用户
            $response = Read-Host "是否要提交这些更改？(y/n)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                $shouldCommit = $true
                $inputMessage = Read-Host "请输入提交信息（留空使用默认信息）"
                if ([string]::IsNullOrWhiteSpace($inputMessage)) {
                    $fileVersion = Get-VersionFromFile
                    $finalCommitMessage = "Update version to $fileVersion"
                } else {
                    $finalCommitMessage = $inputMessage
                }
            }
        }
        
        if ($shouldCommit) {
            try {
                Write-Info "添加所有更改到暂存区..."
                git add -A
                Write-Info "提交更改..."
                git commit -m $finalCommitMessage
                if ($LASTEXITCODE -ne 0) {
                    throw "提交失败"
                }
                Write-Success "提交成功"
            } catch {
                Write-Error "错误: 提交失败: $_"
                exit 1
            }
        } else {
            Write-Warning "跳过提交，继续执行"
        }
    }
    
    # 检查是否有未推送的提交
    try {
        git fetch origin 2>$null | Out-Null
        $localBranch = git rev-parse --abbrev-ref HEAD
        $remoteBranch = "origin/$localBranch"
        $localCommit = git rev-parse HEAD
        $remoteCommit = git rev-parse $remoteBranch 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $localCommit -ne $remoteCommit) {
            Write-Info ""
            Write-Warning "检测到本地有未推送的提交"
            $response = Read-Host "是否要推送代码到远程仓库？(y/n)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                try {
                    Write-Info "推送代码到远程仓库..."
                    git push origin $localBranch
                    if ($LASTEXITCODE -ne 0) {
                        throw "推送代码失败"
                    }
                    Write-Success "代码推送成功"
                } catch {
                    Write-Error "错误: 推送代码失败: $_"
                    exit 1
                }
            } else {
                Write-Warning "跳过代码推送，继续执行"
            }
        }
    } catch {
        Write-Warning "无法检查远程分支状态，继续执行..."
    }
}

# 主函数
function Main {
    param(
        [string]$CommitMessage,
        [switch]$Force
    )
    
    Write-Info "=== Git Tag 推送脚本 ===" -ForegroundColor Cyan
    Write-Info ""
    
    # 检查是否在 Git 仓库中
    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        if (-not $gitRoot) {
            throw "当前目录不是 Git 仓库"
        }
        Write-Info "Git 仓库: $gitRoot"
    } catch {
        Write-Error "错误: 当前目录不是 Git 仓库或 Git 未初始化"
        exit 1
    }
    
    # 先处理代码提交和推送（如果有 CommitMessage 参数或需要交互）
    Process-CommitAndPush -CommitMessage $CommitMessage
    
    # 读取 version 文件
    try {
        $fileVersion = Get-VersionFromFile
        Write-Info "version 文件中的版本: $fileVersion"
    } catch {
        Write-Error "错误: $_"
        exit 1
    }
    
    # 获取最新 Git tag
    $latestTag = Get-LatestGitTag
    
    if ($null -eq $latestTag) {
        Write-Warning "未找到 Git tag，将创建第一个 tag: $fileVersion"
        $shouldCreate = $true
    } else {
        Write-Info "Git 最新 tag: $latestTag"
        
        # 比较版本号
        $comparison = Compare-Version $fileVersion $latestTag
        
        if ($comparison -gt 0) {
            # version 文件中的版本更新
            Write-Success "version 文件中的版本 ($fileVersion) 比 Git tag ($latestTag) 新"
            $shouldCreate = $true
        } elseif ($comparison -eq 0) {
            # 版本相同
            Write-Info "version 文件中的版本 ($fileVersion) 与 Git tag ($latestTag) 相同"
            if ($Force) {
                Write-Warning "使用 -Force 参数，将重新创建 tag"
                $shouldCreate = $true
            } elseif (-not [string]::IsNullOrWhiteSpace($CommitMessage)) {
                # 如果提供了 CommitMessage，说明用户只想提交代码，不创建 tag
                Write-Info "已处理代码提交，无需创建 tag（版本相同）"
                $shouldCreate = $false
            } else {
                Write-Info "无需操作。如需强制推送，请使用 -Force 参数。"
                exit 0
            }
        } else {
            # version 文件中的版本更旧
            Write-Warning "警告: version 文件中的版本 ($fileVersion) 比 Git tag ($latestTag) 旧"
            if ($Force) {
                Write-Warning "使用 -Force 参数，将创建较旧的 tag"
                $shouldCreate = $true
            } else {
                Write-Error "错误: 版本号不能回退。如需强制推送，请使用 -Force 参数。"
                exit 1
            }
        }
    }
    
    # 创建并推送 tag
    if ($shouldCreate) {
        Write-Info ""
        Write-Info "准备创建并推送 tag: $fileVersion"
        
        # 检查 tag 是否已存在（本地）
        $tagExists = git tag -l $fileVersion
        if ($tagExists) {
            Write-Warning "Tag $fileVersion 已存在于本地"
            if ($Force) {
                Write-Warning "使用 -Force 参数，将删除并重新创建 tag"
                git tag -d $fileVersion
            } else {
                Write-Error "错误: Tag 已存在。如需覆盖，请使用 -Force 参数。"
                exit 1
            }
        }
        
        # 创建 tag
        try {
            Write-Info "创建 tag: $fileVersion"
            git tag $fileVersion
            if ($LASTEXITCODE -ne 0) {
                throw "创建 tag 失败"
            }
            Write-Success "Tag 创建成功"
        } catch {
            Write-Error "错误: 创建 tag 失败: $_"
            exit 1
        }
        
        # 推送 tag
        try {
            Write-Info "推送 tag 到远程仓库..."
            git push origin $fileVersion
            if ($LASTEXITCODE -ne 0) {
                throw "推送 tag 失败"
            }
            Write-Success "Tag 推送成功: $fileVersion"
            Write-Info ""
            Write-Success "完成！GitHub Actions 将自动触发构建。"
        } catch {
            Write-Error "错误: 推送 tag 失败: $_"
            Write-Info "提示: 请检查网络连接和 Git 远程仓库配置"
            exit 1
        }
    }
}

# 运行主函数
try {
    Main -CommitMessage $CommitMessage -Force:$Force
} catch {
    Write-Error "发生未预期的错误: $_"
    exit 1
}

