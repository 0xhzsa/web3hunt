param(
  [Parameter(Mandatory=$true)][string]$Address,
  [string]$Rpc = "https://rpc.mainnet.chain.robinhood.com"
)

$ErrorActionPreference = "Stop"

Write-Output "== v4 hook probe =="
Write-Output "address : $Address"
Write-Output "rpc     : $Rpc"

$chainId = (& cast chain-id --rpc-url $Rpc 2>$null)
Write-Output "chainId : $chainId"

$code = (& cast code $Address --rpc-url $Rpc 2>$null)
if (-not $code -or $code -eq "0x") {
  Write-Output "code    : 0x (no contract — EOA or wrong chain)"
  exit 0
}
Write-Output ("code    : {0} bytes" -f (($code.Length - 2) / 2))

$addrInt = [System.Numerics.BigInteger]::Parse(($Address -replace '^0x',''), [System.Globalization.NumberStyles]::HexNumber)
$bits = $addrInt -band [System.Numerics.BigInteger]::Parse("3FFF", [System.Globalization.NumberStyles]::HexNumber)
$bitsHex = "0x" + $bits.ToString("x4").PadLeft(4, "0")

$names = @(
  @{ b = 0x2000; n = "BEFORE_INITIALIZE" },
  @{ b = 0x1000; n = "AFTER_INITIALIZE" },
  @{ b = 0x0800; n = "BEFORE_ADD_LIQUIDITY" },
  @{ b = 0x0400; n = "AFTER_ADD_LIQUIDITY" },
  @{ b = 0x0200; n = "BEFORE_REMOVE_LIQUIDITY" },
  @{ b = 0x0100; n = "AFTER_REMOVE_LIQUIDITY" },
  @{ b = 0x0080; n = "BEFORE_SWAP" },
  @{ b = 0x0040; n = "AFTER_SWAP" },
  @{ b = 0x0020; n = "BEFORE_DONATE" },
  @{ b = 0x0010; n = "AFTER_DONATE" },
  @{ b = 0x0008; n = "BEFORE_SWAP_RETURNS_DELTA" },
  @{ b = 0x0004; n = "AFTER_SWAP_RETURNS_DELTA" },
  @{ b = 0x0002; n = "AFTER_ADD_LIQUIDITY_RETURNS_DELTA" },
  @{ b = 0x0001; n = "AFTER_REMOVE_LIQUIDITY_RETURNS_DELTA" }
)

Write-Output "permBits: $bitsHex"
$active = @()
foreach ($f in $names) {
  if (($bits -band $f.b) -ne 0) { $active += $f.n }
}
if ($active.Count -eq 0) { Write-Output "flags   : (none)" } else { Write-Output ("flags   : " + ($active -join ", ")) }
