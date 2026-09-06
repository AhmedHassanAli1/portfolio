# Kopiera denna fil till config.py och fyll i egna värden.
# config.py checkas INTE in i git (se .gitignore) eftersom den innehåller
# nycklar/PIN-koder som delas mellan tracker och basstation.

# 32 bytes = AES-256. MÅSTE vara identisk på tracker och basstation.
SHARED_KEY = b"REPLACE_WITH_32_BYTE_RANDOM_KEY"

# 6-siffrig BLE-passkey/PIN-kod som används vid parkoppling.
BLE_PASSKEY = 123456
