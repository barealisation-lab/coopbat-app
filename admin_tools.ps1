# ==========================
# Coop'Bat - Admin Tools (V3.1)
# ==========================
# Usage:
#   1) Lancer backend (dans un autre terminal)
#   2) Exécuter ce script:
#       powershell -ExecutionPolicy Bypass -File .\admin_tools.ps1
#
# Requiert:
#   - ADMIN_TOKEN défini (ou on le demande)
# ==========================

$baseUrl = "http://127.0.0.1:8000"

function Read-NonEmpty([string]$prompt) {
    while ($true) {
        $v = Read-Host $prompt
        if ($null -ne $v -and $v.Trim().Length -gt 0) { return $v.Trim() }
        Write-Host "Valeur obligatoire." -ForegroundColor Yellow
    }
}

function Get-AdminHeaders() {
    if (-not $env:ADMIN_TOKEN -or $env:ADMIN_TOKEN.Trim().Length -eq 0) {
        $env:ADMIN_TOKEN = Read-NonEmpty "Entrez ADMIN_TOKEN"
    }
    return @{ "X-ADMIN-TOKEN" = $env:ADMIN_TOKEN }
}

function Call-Get($path, $admin = $false) {
    $uri = "$baseUrl$path"
    if ($admin) {
        $headers = Get-AdminHeaders
        return Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
    } else {
        return Invoke-RestMethod -Method Get -Uri $uri
    }
}

function Call-Post($path, $bodyObj, $admin = $true) {
    $uri = "$baseUrl$path"
    $json = ($bodyObj | ConvertTo-Json -Depth 20)
    if ($admin) {
        $headers = Get-AdminHeaders
        return Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -ContentType "application/json" -Body $json
    } else {
        return Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body $json
    }
}

function Call-Put($path, $bodyObj, $admin = $true) {
    $uri = "$baseUrl$path"
    $json = ($bodyObj | ConvertTo-Json -Depth 20)
    $headers = Get-AdminHeaders
    return Invoke-RestMethod -Method Put -Uri $uri -Headers $headers -ContentType "application/json" -Body $json
}

function Call-Delete($path, $admin = $true) {
    $uri = "$baseUrl$path"
    $headers = Get-AdminHeaders
    return Invoke-RestMethod -Method Delete -Uri $uri -Headers $headers
}

function Show-Json($obj) {
    $obj | ConvertTo-Json -Depth 20
}

function Pause() {
    Read-Host "Appuyez sur Entrée pour continuer..."
}

# --------------------------
# Actions Catalogue
# --------------------------

function Add-WoodSpecies() {
    $name = Read-NonEmpty "Nom essence (ex: Douglas)"
    $note = Read-Host "Note (optionnel)"
    $body = @{ name = $name; note = $note }
    $res = Call-Post "/catalog/wood_species" $body $true
    Write-Host "✅ Essence créée: ID=$($res.id)" -ForegroundColor Green
}

function List-WoodSpecies() {
    $res = Call-Get "/catalog/wood_species" $false
    $res | Format-Table id, name, note -AutoSize
}

function Add-TimberSection() {
    $sec = Read-NonEmpty "Section (mm) (ex: 63x175)"
    $note = Read-Host "Note (optionnel)"
    $body = @{ section_mm = $sec; note = $note }
    $res = Call-Post "/catalog/timber_sections" $body $true
    Write-Host "✅ Section créée: ID=$($res.id)" -ForegroundColor Green
}

function List-TimberSections() {
    $res = Call-Get "/catalog/timber_sections" $false
    $res | Format-Table id, section_mm, note -AutoSize
}

function Add-CatalogItem() {
    $cat = Read-NonEmpty "Catégorie (ex: REF / COUVERTURE / ZINGUERIE / CHARPENTE)"
    $name = Read-NonEmpty "Nom item (ex: Liteaux)"
    $unit = Read-Host "Unité (ex: ml, m², u, m³) (optionnel)"
    $priceStr = Read-Host "Prix (optionnel, ex: 12.5) (laisser vide si non défini)"
    $note = Read-Host "Note (optionnel)"

    $price = $null
    if ($priceStr -and $priceStr.Trim().Length -gt 0) {
        try { $price = [double]($priceStr.Replace(",", ".")) } catch { $price = $null }
    }

    $body = @{
        category = $cat
        name     = $name
        unit     = $unit
        price    = $price
        note     = $note
    }
    $res = Call-Post "/catalog/items" $body $true
    Write-Host "✅ Item créé: ID=$($res.id)" -ForegroundColor Green
}

function List-CatalogByCategory() {
    $cat = Read-NonEmpty "Catégorie à lister (ex: REF)"
    $res = Call-Get "/catalog/items/$cat" $false
    if (-not $res) { Write-Host "(vide)"; return }
    $res | Format-Table id, category, name, unit, price, note -AutoSize
}

function Update-CatalogItem() {
    $id = Read-NonEmpty "ID item à modifier"
    $cat = Read-Host "Nouvelle catégorie (laisser vide si inchangé)"
    $name = Read-Host "Nouveau nom (laisser vide si inchangé)"
    $unit = Read-Host "Nouvelle unité (laisser vide si inchangé)"
    $priceStr = Read-Host "Nouveau prix (laisser vide si inchangé / mettre 0 si 0)"
    $note = Read-Host "Nouvelle note (laisser vide si inchangé)"

    $body = @{}
    if ($cat -and $cat.Trim().Length -gt 0) { $body.category = $cat.Trim() }
    if ($name -and $name.Trim().Length -gt 0) { $body.name = $name.Trim() }
    if ($unit -and $unit.Trim().Length -gt 0) { $body.unit = $unit.Trim() }
    if ($note -and $note.Trim().Length -gt 0) { $body.note = $note.Trim() }

    if ($priceStr -and $priceStr.Trim().Length -gt 0) {
        try { $body.price = [double]($priceStr.Replace(",", ".")) } catch {}
    }

    if ($body.Keys.Count -eq 0) {
        Write-Host "Rien à modifier." -ForegroundColor Yellow
        return
    }

    $res = Call-Put "/catalog/items/$id" $body $true
    Write-Host "✅ Item modifié: ID=$($res.id)" -ForegroundColor Green
}

function Delete-CatalogItem() {
    $id = Read-NonEmpty "ID item à supprimer"
    $confirm = Read-Host "Confirmer suppression (O/N)"
    if ($confirm.ToUpper() -ne "O") { Write-Host "Annulé."; return }
    $res = Call-Delete "/catalog/items/$id" $true
    Write-Host "✅ Item supprimé: ID=$($res.id)" -ForegroundColor Green
}

# --------------------------
# Actions Admin (demandes / archives)
# --------------------------

function List-AdvancedRequests() {
    $limit = Read-Host "Limit (défaut 50)"
    if (-not $limit -or $limit.Trim().Length -eq 0) { $limit = "50" }
    $res = Call-Get "/admin/requests/advanced?limit=$limit" $true
    $res | Format-Table id, user_id, contact_name, contact_commune, contact_email, created_at -AutoSize
}

function Read-AdvancedById() {
    $id = Read-NonEmpty "ID advanced à lire"
    $res = Call-Get "/admin/advanced/$id" $true
    Show-Json $res
}

function List-Archives() {
    $limit = Read-Host "Limit (défaut 50)"
    if (-not $limit -or $limit.Trim().Length -eq 0) { $limit = "50" }
    $res = Call-Get "/admin/archives?limit=$limit" $true
    Write-Host "Dossier: $($res.dir)"
    Write-Host "Fichiers:"
    $res.files | ForEach-Object { Write-Host " - $_" }
}

function Read-ArchiveFile() {
    $fn = Read-NonEmpty "Nom de fichier archive (ex: advanced_1_20260215_120000.json)"
    $res = Call-Get "/admin/archives/$fn" $true
    Show-Json $res
}

# --------------------------
# Seeding (optionnel)
# --------------------------

function Seed-Basics() {
    Write-Host "Ajout d'un seed minimal (essences/sections/items REF)..." -ForegroundColor Cyan

    # Essences courantes (charpente)
    $woods = @(
        "Sapin/Épicéa",
        "Douglas",
        "Pin sylvestre",
        "Mélèze",
        "Chêne",
        "Châtaignier",
        "Lamellé-collé (GL24/GL28)",
        "LVL",
        "OSB 3",
        "CTBX/Contreplaqué"
    )
    foreach ($w in $woods) {
        try {
            Call-Post "/catalog/wood_species" @{ name=$w; note="seed" } $true | Out-Null
        } catch {}
    }

    # Sections fréquentes (à compléter)
    $sections = @(
        "38x89","45x95","45x145","45x220",
        "63x75","63x100","63x125","63x150","63x175","63x200","63x225",
        "75x100","75x150","75x200",
        "100x100","100x200",
        "120x120","140x140","160x160",
        "200x200"
    )
    foreach ($s in $sections) {
        try {
            Call-Post "/catalog/timber_sections" @{ section_mm=$s; note="seed" } $true | Out-Null
        } catch {}
    }

    # Items REF / COUVERTURE / ZINGUERIE / CHARPENTE (prix null)
    $items = @(
        @{category="COUVERTURE"; name="Liteaux"; unit="ml"; note="seed"; price=$null},
        @{category="COUVERTURE"; name="Contre-liteaux"; unit="ml"; note="seed"; price=$null},
        @{category="COUVERTURE"; name="Écran sous-toiture"; unit="m²"; note="seed"; price=$null},
        @{category="COUVERTURE"; name="Tuiles mécaniques (selon modèle)"; unit="m²"; note="seed"; price=$null},
        @{category="COUVERTURE"; name="Ardoises (selon modèle)"; unit="m²"; note="seed"; price=$null},
        @{category="COUVERTURE"; name="Zinc couverture (joints debout)"; unit="m²"; note="seed"; price=$null},

        @{category="ZINGUERIE"; name="Gouttières (pose + fourniture)"; unit="ml"; note="seed"; price=$null},
        @{category="ZINGUERIE"; name="Habillage rives (frontons)"; unit="ml"; note="seed"; price=$null},
        @{category="ZINGUERIE"; name="Habillage mur"; unit="m²"; note="seed"; price=$null},
        @{category="ZINGUERIE"; name="Couverture zinc"; unit="m²"; note="seed"; price=$null},
        @{category="ZINGUERIE"; name="Tour de cheminée"; unit="u"; note="seed"; price=$null},

        @{category="CHARPENTE"; name="Bois de structure"; unit="m³"; note="seed"; price=$null},
        @{category="CHARPENTE"; name="Connecteurs (sabots/équerres)"; unit="u"; note="seed"; price=$null},
        @{category="CHARPENTE"; name="Contreventement (OSB/CTBX)"; unit="m²"; note="seed"; price=$null},
        @{category="CHARPENTE"; name="Traitement bois"; unit="m²"; note="seed"; price=$null}
    )

    foreach ($it in $items) {
        try { Call-Post "/catalog/items" $it $true | Out-Null } catch {}
    }

    Write-Host "✅ Seed terminé." -ForegroundColor Green
}

# --------------------------
# Menu loop
# --------------------------
while ($true) {
    Clear-Host
    Write-Host "========================================="
    Write-Host " Coop'Bat - Admin Tools (V3.1 + Token)"
    Write-Host " Base: $baseUrl"
    if ($env:ADMIN_TOKEN -and $env:ADMIN_TOKEN.Trim().Length -gt 0) {
        Write-Host " Token: (défini)" -ForegroundColor Green
    } else {
        Write-Host " Token: (non défini)" -ForegroundColor Yellow
    }
    Write-Host "========================================="
    Write-Host ""
    Write-Host "1) Catalogue - Lister essences"
    Write-Host "2) Catalogue - Ajouter essence"
    Write-Host "3) Catalogue - Lister sections"
    Write-Host "4) Catalogue - Ajouter section"
    Write-Host "5) Catalogue - Lister items par catégorie"
    Write-Host "6) Catalogue - Ajouter item"
    Write-Host "7) Catalogue - Modifier item"
    Write-Host "8) Catalogue - Supprimer item"
    Write-Host ""
    Write-Host "9) Admin - Lister demandes Advanced"
    Write-Host "10) Admin - Lire Advanced par ID"
    Write-Host "11) Admin - Lister fichiers archives"
    Write-Host "12) Admin - Lire une archive JSON"
    Write-Host ""
    Write-Host "13) Seed (essences/sections/items de base)"
    Write-Host ""
    Write-Host "0) Quitter"
    Write-Host ""

    $choice = Read-Host "Choix"

    try {
        switch ($choice) {
            "1" { List-WoodSpecies; Pause }
            "2" { Add-WoodSpecies; Pause }
            "3" { List-TimberSections; Pause }
            "4" { Add-TimberSection; Pause }
            "5" { List-CatalogByCategory; Pause }
            "6" { Add-CatalogItem; Pause }
            "7" { Update-CatalogItem; Pause }
            "8" { Delete-CatalogItem; Pause }

            "9" { List-AdvancedRequests; Pause }
            "10" { Read-AdvancedById; Pause }
            "11" { List-Archives; Pause }
            "12" { Read-ArchiveFile; Pause }

            "13" { Seed-Basics; Pause }

            "0" { break }
            default { Write-Host "Choix invalide." -ForegroundColor Yellow; Pause }
        }
    } catch {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        Pause
    }
}
