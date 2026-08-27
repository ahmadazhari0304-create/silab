# Simple PowerShell Web Server for SILAB (mocking app.py)
$port = 5000
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$baseDir = Get-Location

# Seed files if they don't exist
$labsFile = Join-Path $baseDir "labs.json"
if (-not (Test-Path $labsFile)) {
    $defaultLabs = @(
        [PSCustomObject]@{ id = 1; nama_lab = "Lab Ward" },
        [PSCustomObject]@{ id = 2; nama_lab = "Lab Emergency" },
        [PSCustomObject]@{ id = 3; nama_lab = "Lab Keluarga" },
        [PSCustomObject]@{ id = 4; nama_lab = "Lab Gerontik" },
        [PSCustomObject]@{ id = 5; nama_lab = "Lab Mikrobiologi Gd.G" },
        [PSCustomObject]@{ id = 6; nama_lab = "Lab Histologi Gd.G" },
        [PSCustomObject]@{ id = 7; nama_lab = "Lab Anatomi" },
        [PSCustomObject]@{ id = 8; nama_lab = "Lab Promkes" }
    )
    $defaultLabs | ConvertTo-Json -Depth 5 | Out-File $labsFile -Encoding utf8
}

$bookingsFile = Join-Path $baseDir "bookings.json"
if (-not (Test-Path $bookingsFile)) {
    $defaultBookings = @(
        [PSCustomObject]@{
            id = 1
            nama_lab = "Lab Medikal Bedah"
            tanggal = "2026-06-08"
            start_time = "08:00"
            end_time = "10:30"
            kelas = "Tingkat 2B"
            prodi = "D3 Keperawatan"
            tujuan = "Praktikum Perawatan Luka"
        },
        [PSCustomObject]@{
            id = 2
            nama_lab = "Lab Keperawatan Anak"
            tanggal = "2026-06-09"
            start_time = "13:00"
            end_time = "15:00"
            kelas = "Tingkat 1A"
            prodi = "S1 Keperawatan"
            tujuan = "Praktikum OGT Bayi"
        }
    )
    $defaultBookings | ConvertTo-Json -Depth 5 | Out-File $bookingsFile -Encoding utf8
}

$bhpFile = Join-Path $baseDir "bhp.json"
if (-not (Test-Path $bhpFile)) {
    $defaultBhp = @(
        [PSCustomObject]@{
            id = 1
            nama_barang = "Handscoon"
            praktikum = "Praktikum Perawatan Luka"
            jumlah = 24
            tanggal = "2026-06-08"
            prodi = "D3"
        },
        [PSCustomObject]@{
            id = 2
            nama_barang = "Masker"
            praktikum = "Praktikum OGT Bayi"
            jumlah = 15
            tanggal = "2026-06-09"
            prodi = "S1"
        }
    )
    $defaultBhp | ConvertTo-Json -Depth 5 | Out-File $bhpFile -Encoding utf8
}

try {
    $listener.Start()
    Write-Host "PowerShell SILAB API Server started on http://localhost:$port/"
    Write-Host "Press Ctrl+C to stop."
    
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $url = $request.Url.LocalPath
        $method = $request.HttpMethod
        
        # Add CORS Headers
        $response.AddHeader("Access-Control-Allow-Origin", "*")
        $response.AddHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        $response.AddHeader("Access-Control-Allow-Headers", "Content-Type")
        
        if ($method -eq "OPTIONS") {
            $response.StatusCode = 200
            $response.Close()
            continue
        }
        
        Write-Host "$method $url"
        
        # Router
        if ($url -eq "/" -and $method -eq "GET") {
            $indexPath = Join-Path $baseDir "templates\index.html"
            if (Test-Path $indexPath) {
                $response.ContentType = "text/html; charset=utf-8"
                $bytes = [System.IO.File]::ReadAllBytes($indexPath)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $response.StatusCode = 404
                $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 Index Not Found")
                $response.OutputStream.Write($errBytes, 0, $errBytes.Length)
            }
        }
        elseif ($url -eq "/api/labs" -and $method -eq "GET") {
            $response.ContentType = "application/json; charset=utf-8"
            $bytes = [System.IO.File]::ReadAllBytes($labsFile)
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        elseif ($url -eq "/api/bookings" -and $method -eq "GET") {
            $response.ContentType = "application/json; charset=utf-8"
            $rawContent = Get-Content $bookingsFile -Raw
            $bookings = @()
            if ($rawContent.Trim()) {
                $parsed = ConvertFrom-Json $rawContent
                if ($null -ne $parsed) {
                    $bookings = @($parsed) | Where-Object { $null -ne $_ }
                }
            }
            
            # Sort by tanggal and start_time
            if ($bookings.Count -gt 0) {
                $sorted = $bookings | Sort-Object tanggal, start_time
                $json = $sorted | ConvertTo-Json -Depth 5
                if ($null -eq $json) { $json = "[]" }
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
            } else {
                $bytes = [System.Text.Encoding]::UTF8.GetBytes("[]")
            }
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        elseif ($url -eq "/api/book" -and $method -eq "POST") {
            $reader = New-Object System.IO.StreamReader($request.InputStream, [System.Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Close()
            
            $data = ConvertFrom-Json $body
            $response.ContentType = "application/json; charset=utf-8"
            
            if ($null -eq $data -or $null -eq $data.nama_lab -or $null -eq $data.tanggal -or $null -eq $data.start_time -or $null -eq $data.end_time -or $null -eq $data.kelas -or $null -eq $data.prodi -or $null -eq $data.tujuan) {
                $response.StatusCode = 400
                $resJson = @{ status = "error"; message = "Semua field peminjaman wajib diisi!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                # Overlap check
                $rawContent = Get-Content $bookingsFile -Raw
                $bookings = @()
                if ($rawContent.Trim()) {
                    $bookings = @(ConvertFrom-Json $rawContent)
                }
                $overlap = $false
                if ($bookings.Count -gt 0) {
                    foreach ($b in $bookings) {
                        if ($b.nama_lab -eq $data.nama_lab -and $b.tanggal -eq $data.tanggal) {
                            # Overlap condition: b.start_time < data.end_time AND b.end_time > data.start_time
                            if ($b.start_time -lt $data.end_time -and $b.end_time -gt $data.start_time) {
                                $overlap = $true
                                break
                            }
                        }
                    }
                }
                
                if ($overlap) {
                    $response.StatusCode = 400
                    $resJson = @{ status = "error"; message = "Maaf, Jadwal $($data.nama_lab) di jam tersebut sudah bentrok!" } | ConvertTo-Json
                    $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                    $response.ContentLength64 = $bytes.Length
                    $response.OutputStream.Write($bytes, 0, $bytes.Length)
                } else {
                    $newId = 1
                    if ($bookings) {
                        foreach ($b in $bookings) {
                            $bIdVal = 0
                            if ($b.id -and [int]::TryParse($b.id, [ref]$bIdVal)) {
                                if ($bIdVal -ge $newId) { $newId = $bIdVal + 1 }
                            }
                        }
                    }
                    $newBooking = [PSCustomObject]@{
                        id = $newId
                        nama_lab = $data.nama_lab
                        tanggal = $data.tanggal
                        start_time = $data.start_time
                        end_time = $data.end_time
                        kelas = $data.kelas
                        prodi = $data.prodi
                        tujuan = $data.tujuan
                    }
                    $bookingsList = @()
                    if ($bookings) {
                        foreach ($b in $bookings) { $bookingsList += $b }
                    }
                    $bookingsList += $newBooking
                    $json = $bookingsList | ConvertTo-Json -Depth 5
                    [System.IO.File]::WriteAllText($bookingsFile, $json, [System.Text.Encoding]::UTF8)
                    
                    $resJson = @{ status = "success"; message = "Peminjaman berhasil dicatat!" } | ConvertTo-Json
                    $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                    $response.ContentLength64 = $bytes.Length
                    $response.OutputStream.Write($bytes, 0, $bytes.Length)
                }
            }
        }
        elseif ($url -eq "/api/bhp" -and $method -eq "GET") {
            $response.ContentType = "application/json; charset=utf-8"
            $rawContent = Get-Content $bhpFile -Raw
            $bhp = @()
            if ($rawContent.Trim()) {
                $parsed = ConvertFrom-Json $rawContent
                if ($null -ne $parsed) {
                    $bhp = @($parsed) | Where-Object { $null -ne $_ }
                }
            }
            
            # Sort by id descending
            if ($bhp.Count -gt 0) {
                $sorted = $bhp | Sort-Object id -Descending
                $json = $sorted | ConvertTo-Json -Depth 5
                if ($null -eq $json) { $json = "[]" }
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
            } else {
                $bytes = [System.Text.Encoding]::UTF8.GetBytes("[]")
            }
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        elseif ($url -eq "/api/bhp" -and $method -eq "POST") {
            $reader = New-Object System.IO.StreamReader($request.InputStream, [System.Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd()
            $reader.Close()
            
            $data = ConvertFrom-Json $body
            $response.ContentType = "application/json; charset=utf-8"
            
            if ($null -eq $data -or $null -eq $data.nama_barang -or $null -eq $data.praktikum -or $null -eq $data.jumlah -or $null -eq $data.tanggal -or $null -eq $data.prodi) {
                $response.StatusCode = 400
                $resJson = @{ status = "error"; message = "Semua field pemakaian BHP wajib diisi!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $jumlah_int = $null
                $isNum = [int]::TryParse($data.jumlah, [ref]$jumlah_int)
                if (-not $isNum -or $jumlah_int -le 0) {
                    $response.StatusCode = 400
                    $resJson = @{ status = "error"; message = "Jumlah barang harus berupa angka positif!" } | ConvertTo-Json
                    $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                    $response.ContentLength64 = $bytes.Length
                    $response.OutputStream.Write($bytes, 0, $bytes.Length)
                } else {
                    $rawContent = Get-Content $bhpFile -Raw
                    $bhp = @()
                    if ($rawContent.Trim()) {
                        $bhp = @(ConvertFrom-Json $rawContent)
                    }
                    $newId = 1
                    if ($bhp) {
                        foreach ($item in $bhp) {
                            $itemIdVal = 0
                            if ($item.id -and [int]::TryParse($item.id, [ref]$itemIdVal)) {
                                if ($itemIdVal -ge $newId) { $newId = $itemIdVal + 1 }
                            }
                        }
                    }
                    $newBhpItem = [PSCustomObject]@{
                        id = $newId
                        nama_barang = $data.nama_barang
                        praktikum = $data.praktikum
                        jumlah = $jumlah_int
                        tanggal = $data.tanggal
                        prodi = $data.prodi
                    }
                    $bhpList = @()
                    if ($bhp) {
                        foreach ($x in $bhp) { $bhpList += $x }
                    }
                    $bhpList += $newBhpItem
                    $json = $bhpList | ConvertTo-Json -Depth 5
                    [System.IO.File]::WriteAllText($bhpFile, $json, [System.Text.Encoding]::UTF8)
                    
                    $resJson = @{ status = "success"; message = "Pemakaian BHP berhasil dicatat!" } | ConvertTo-Json
                    $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                    $response.ContentLength64 = $bytes.Length
                    $response.OutputStream.Write($bytes, 0, $bytes.Length)
                }
            }
        }
        elseif ($url -match "^/api/bookings/(\d+)$" -and $method -eq "DELETE") {
            $bookingId = [int]$Matches[1]
            $response.ContentType = "application/json; charset=utf-8"
            
            $rawContent = Get-Content $bookingsFile -Raw
            $bookings = @()
            if ($rawContent.Trim()) {
                $bookings = @(ConvertFrom-Json $rawContent)
            }
            $found = $false
            $newBookingsList = @()
            
            if ($bookings) {
                foreach ($b in $bookings) {
                    if ($b.id -eq $bookingId) {
                        $found = $true
                    } else {
                        $newBookingsList += $b
                    }
                }
            }
            
            if (-not $found) {
                $response.StatusCode = 404
                $resJson = @{ status = "error"; message = "Jadwal tidak ditemukan!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $json = "[]"
                if ($newBookingsList) {
                    $json = $newBookingsList | ConvertTo-Json -Depth 5
                }
                [System.IO.File]::WriteAllText($bookingsFile, $json, [System.Text.Encoding]::UTF8)
                $resJson = @{ status = "success"; message = "Jadwal peminjaman berhasil dihapus!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            }
        }
        elseif ($url -match "^/api/bhp/(\d+)$" -and $method -eq "DELETE") {
            $bhpId = [int]$Matches[1]
            $response.ContentType = "application/json; charset=utf-8"
            
            $rawContent = Get-Content $bhpFile -Raw
            $bhpList = @()
            if ($rawContent.Trim()) {
                $bhpList = @(ConvertFrom-Json $rawContent)
            }
            $found = $false
            $newBhpList = @()
            
            if ($bhpList) {
                foreach ($item in $bhpList) {
                    if ($item.id -eq $bhpId) {
                        $found = $true
                    } else {
                        $newBhpList += $item
                    }
                }
            }
            
            if (-not $found) {
                $response.StatusCode = 404
                $resJson = @{ status = "error"; message = "Data BHP tidak ditemukan!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $json = "[]"
                if ($newBhpList) {
                    $json = $newBhpList | ConvertTo-Json -Depth 5
                }
                [System.IO.File]::WriteAllText($bhpFile, $json, [System.Text.Encoding]::UTF8)
                $resJson = @{ status = "success"; message = "Data pemakaian BHP berhasil dihapus!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            }
        }
        elseif ($url -eq "/api/sops" -and $method -eq "GET") {
            $response.ContentType = "application/json; charset=utf-8"
            $sopsFile = Join-Path $baseDir "sops.json"
            if (-not (Test-Path $sopsFile)) {
                "[]" | Out-File $sopsFile -Encoding utf8
            }
            $bytes = [System.IO.File]::ReadAllBytes($sopsFile)
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        elseif ($url -eq "/api/sops" -and $method -eq "POST") {
            $contentType = $request.ContentType
            if ($contentType -match "multipart/form-data") {
                $inputStream = $request.InputStream
                $memStream = New-Object System.IO.MemoryStream
                $inputStream.CopyTo($memStream)
                $rawBytes = $memStream.ToArray()
                $memStream.Close()
                
                $rawString = [System.Text.Encoding]::UTF8.GetString($rawBytes)
                
                $title = ""
                if ($rawString -match 'name="title"\r?\n\r?\n([^\r\n]+)') {
                    $title = $Matches[1]
                }
                if ($title -eq "" -and $rawString -match 'name="title"\n\n([^\n]+)') {
                    $title = $Matches[1]
                }
                
                $category = ""
                if ($rawString -match 'name="category"\r?\n\r?\n([^\r\n]+)') {
                    $category = $Matches[1]
                }
                if ($category -eq "" -and $rawString -match 'name="category"\n\n([^\n]+)') {
                    $category = $Matches[1]
                }
                
                $filename = "uploaded.pdf"
                if ($rawString -match 'filename="([^"]+)"') {
                    $filename = $Matches[1]
                }
                
                $boundary = $contentType.Split(";").Where({$_ -match "boundary="}).Split("=")[1].Trim()
                $fileHeaderIndex = $rawString.IndexOf('filename="')
                if ($fileHeaderIndex -gt -1) {
                    $startOfFileContent = $rawString.IndexOf("`r`n`r`n", $fileHeaderIndex) + 4
                    if ($startOfFileContent -lt 4) {
                        $startOfFileContent = $rawString.IndexOf("`n`n", $fileHeaderIndex) + 2
                    }
                    
                    $endBoundary = "`r`n--" + $boundary
                    $endOfFileContent = $rawString.IndexOf($endBoundary, $startOfFileContent)
                    if ($endOfFileContent -eq -1) {
                        $endBoundary = "`n--" + $boundary
                        $endOfFileContent = $rawString.IndexOf($endBoundary, $startOfFileContent)
                    }
                    
                    if ($startOfFileContent -gt 1 -and $endOfFileContent -gt $startOfFileContent) {
                        $fileBytes = New-Object byte[] ($endOfFileContent - $startOfFileContent)
                        [Array]::Copy($rawBytes, $startOfFileContent, $fileBytes, 0, $fileBytes.Length)
                        
                        $uploadsDir = Join-Path $baseDir "uploads\sops"
                        if (-not (Test-Path $uploadsDir)) {
                            New-Item -ItemType Directory -Path $uploadsDir -Force | Out-Null
                        }
                        
                        # Ensure filename uniqueness
                        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($filename)
                        $extension = [System.IO.Path]::GetExtension($filename)
                        $counter = 1
                        $uniqueFilename = $filename
                        while (Test-Path (Join-Path $uploadsDir $uniqueFilename)) {
                            $uniqueFilename = "$baseName`_$counter$extension"
                            $counter++
                        }
                        
                        $targetPath = Join-Path $uploadsDir $uniqueFilename
                        [System.IO.File]::WriteAllBytes($targetPath, $fileBytes)
                        
                        $sopsFile = Join-Path $baseDir "sops.json"
                        $sops = @()
                        if (Test-Path $sopsFile) {
                            $rawSops = Get-Content $sopsFile -Raw
                            if ($rawSops.Trim()) {
                                $parsedSops = ConvertFrom-Json $rawSops
                                if ($null -ne $parsedSops) {
                                    $sops = @($parsedSops) | Where-Object { $null -ne $_ }
                                }
                            }
                        }
                        
                        $newId = 1
                        if ($sops) {
                            foreach ($s in $sops) {
                                $sIdVal = 0
                                if ($s.id -and [int]::TryParse($s.id, [ref]$sIdVal)) {
                                    if ($sIdVal -ge $newId) { $newId = $sIdVal + 1 }
                                }
                            }
                        }
                        
                        $newSop = [PSCustomObject]@{
                            id = $newId
                            title = $title
                            category = $category
                            filename = $uniqueFilename
                        }
                        
                        $sopsList = @()
                        if ($sops) {
                            foreach ($s in $sops) { $sopsList += $s }
                        }
                        $sopsList += $newSop
                        $json = $sopsList | ConvertTo-Json -Depth 5
                        [System.IO.File]::WriteAllText($sopsFile, $json, [System.Text.Encoding]::UTF8)
                        
                        $response.ContentType = "application/json; charset=utf-8"
                        $resJson = @{ status = "success"; message = "SOP berhasil diupload!" } | ConvertTo-Json
                        $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                        $response.ContentLength64 = $bytes.Length
                        $response.OutputStream.Write($bytes, 0, $bytes.Length)
                    } else {
                        $response.StatusCode = 400
                        $resJson = @{ status = "error"; message = "Gagal memproses file upload!" } | ConvertTo-Json
                        $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                        $response.ContentLength64 = $bytes.Length
                        $response.OutputStream.Write($bytes, 0, $bytes.Length)
                    }
                }
            }
        }
        elseif ($url -match "^/api/sops/(\d+)$" -and $method -eq "DELETE") {
            $sopId = [int]$Matches[1]
            $response.ContentType = "application/json; charset=utf-8"
            
            $sopsFile = Join-Path $baseDir "sops.json"
            $sops = @()
            if (Test-Path $sopsFile) {
                $rawSops = Get-Content $sopsFile -Raw
                if ($rawSops.Trim()) {
                    $parsedSops = ConvertFrom-Json $rawSops
                    if ($null -ne $parsedSops) {
                        $sops = @($parsedSops) | Where-Object { $null -ne $_ }
                    }
                }
            }
            
            $found = $false
            $newSopsList = @()
            $filenameToDelete = ""
            
            if ($sops) {
                foreach ($s in $sops) {
                    if ($s.id -eq $sopId) {
                        $found = $true
                        $filenameToDelete = $s.filename
                    } else {
                        $newSopsList += $s
                    }
                }
            }
            
            if (-not $found) {
                $response.StatusCode = 404
                $resJson = @{ status = "error"; message = "SOP tidak ditemukan!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                if ($filenameToDelete) {
                    $filePath = Join-Path $baseDir "uploads\sops\$filenameToDelete"
                    if (Test-Path $filePath) {
                        Remove-Item $filePath -Force | Out-Null
                    }
                }
                
                $json = "[]"
                if ($newSopsList) {
                    $json = $newSopsList | ConvertTo-Json -Depth 5
                }
                [System.IO.File]::WriteAllText($sopsFile, $json, [System.Text.Encoding]::UTF8)
                $resJson = @{ status = "success"; message = "SOP berhasil dihapus!" } | ConvertTo-Json
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($resJson)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            }
        }
        elseif ($url -match "^/uploads/sops/(.+)$" -and $method -eq "GET") {
            $filename = $Matches[1]
            $filePath = Join-Path $baseDir "uploads\sops\$filename"
            if (Test-Path $filePath) {
                $response.ContentType = "application/pdf"
                $bytes = [System.IO.File]::ReadAllBytes($filePath)
                $response.ContentLength64 = $bytes.Length
                $response.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $response.StatusCode = 404
                $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 SOP File Not Found")
                $response.ContentLength64 = $errBytes.Length
                $response.OutputStream.Write($errBytes, 0, $errBytes.Length)
            }
        }
        else {
            $response.StatusCode = 404
            $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
            $response.ContentLength64 = $errBytes.Length
            $response.OutputStream.Write($errBytes, 0, $errBytes.Length)
        }
        $response.Close()
    }
} catch {
    Write-Error $_
} finally {
    $listener.Stop()
}
