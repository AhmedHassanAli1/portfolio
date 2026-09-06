from machine import Pin, SPI, UART
import time
import os
import cryptolib

# =========================
# DEL 0: AES-CBC
# =========================

# Delad AES-256-nyckel mellan tracker och basstation.
# Nyckeln laddas från config.py, som INTE checkas in i git (se .gitignore).
# Skapa din egen config.py lokalt utifrån config_example.py innan drift.
from config import SHARED_KEY

def pkcs7_pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def encrypt_payload(text: str) -> bytes:
    """
    Format:
    [16 byte IV] + [ciphertext]
    """
    iv = os.urandom(16)
    aes = cryptolib.aes(SHARED_KEY, 2, iv)   # 2 = CBC
    padded = pkcs7_pad(text.encode("utf-8"))
    ciphertext = aes.encrypt(padded)
    return iv + ciphertext


# =========================
# DEL 1: LoRa / SX1262
# =========================

spi = SPI(0,
          baudrate=100000,
          polarity=0,
          phase=0,
          sck=Pin(18),
          mosi=Pin(19),
          miso=Pin(16))

cs = Pin(17, Pin.OUT, value=1)
busy = Pin(21, Pin.IN)
dio1 = Pin(20, Pin.IN)
reset = Pin(22, Pin.OUT, value=1)

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


def hw_reset():
    reset.value(1)
    time.sleep_ms(10)
    reset.value(0)
    time.sleep_us(200)
    reset.value(1)
    time.sleep_ms(20)


def wait_busy(timeout_ms=2000):
    start = time.ticks_ms()
    while busy.value():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            raise RuntimeError("BUSY timeout")


def write_cmd(opcode, data=b""):
    wait_busy()
    cs.value(0)
    spi.write(bytes([opcode]))
    if data:
        spi.write(data)
    cs.value(1)
    wait_busy()


def read_cmd(opcode, length):
    wait_busy()
    cs.value(0)
    spi.write(bytes([opcode, 0x00]))
    data = spi.read(length, 0x00)
    cs.value(1)
    wait_busy()
    return data


def write_buffer(offset, payload):
    wait_busy()
    cs.value(0)
    spi.write(bytes([0x0E, offset]))
    spi.write(payload)
    cs.value(1)
    wait_busy()


def get_status():
    wait_busy()
    cs.value(0)
    spi.write(b'\xC0\x00')
    data = spi.read(1, 0x00)
    cs.value(1)
    return data[0]


def get_irq_status():
    data = read_cmd(0x12, 2)
    return (data[0] << 8) | data[1]


def set_standby():
    write_cmd(0x80, b'\x00')


def set_packet_type_lora():
    write_cmd(0x8A, b'\x01')


def set_rf_frequency_868():
    freq = 0x36400000
    write_cmd(0x86, freq.to_bytes(4, 'big'))


def set_pa_config():
    write_cmd(0x95, bytes([0x04, 0x07, 0x00, 0x01]))


def set_tx_params():
    write_cmd(0x8E, bytes([14, 0x04]))


def set_modulation_params():
    write_cmd(0x8B, bytes([0x07, 0x04, 0x01, 0x00]))


def set_packet_params(payload_len):
    preamble = 8
    write_cmd(0x8C, bytes([
        (preamble >> 8) & 0xFF,
        preamble & 0xFF,
        0x00,        # explicit header
        payload_len,
        0x01,        # CRC on
        0x00         # standard IQ
    ]))


def set_buffer_base():
    write_cmd(0x8F, b'\x00\x00')


def clear_irq():
    write_cmd(0x02, b'\xFF\xFF')


def set_dio1_irq():
    # TX done on DIO1
    write_cmd(0x08, b'\x00\x01\x00\x01\x00\x00\x00\x00')


def tx_start():
    write_cmd(0x83, b'\x00\x00\x00')


def wait_tx_done(timeout_ms=3000):
    start = time.ticks_ms()
    while True:
        irq = get_irq_status()
        if irq & 0x0001:   # TxDone
            return irq
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            raise RuntimeError("TX timeout")
        time.sleep_ms(10)


def set_dio2_as_rf_switch():
    write_cmd(0x9D, b'\x01')


def radio_init():
    hw_reset()
    print("Status after reset:", hex(get_status()))
    set_standby()
    print("Standby OK:", hex(get_status()))
    set_packet_type_lora()
    print("Packet type OK")
    set_dio2_as_rf_switch()
    print("DIO2 RF switch OK")
    set_rf_frequency_868()
    print("Frequency OK")
    set_pa_config()
    print("PA config OK")
    set_tx_params()
    print("TX params OK")
    set_modulation_params()
    print("Modulation params OK")
    set_buffer_base()
    print("Buffer base OK")
    set_dio1_irq()
    print("DIO1 IRQ OK")


def send_packet(text):
    payload = encrypt_payload(text)

    if len(payload) > 64:
        raise ValueError("Encrypted payload too long for current LoRa packet size")

    set_packet_params(len(payload))
    write_buffer(0x00, payload)
    clear_irq()
    tx_start()
    irq = wait_tx_done()

    print("TX done, IRQ:", hex(irq))
    print("Encrypted payload length:", len(payload))
    clear_irq()


# =========================
# DEL 2: GPS helpers
# =========================

def convert_to_decimal(raw, direction, is_lon=False):
    if not raw or not direction:
        return None
    try:
        deg_len = 3 if is_lon else 2
        degrees = int(raw[:deg_len])
        minutes = float(raw[deg_len:])
        decimal = degrees + minutes / 60
        if direction in ("S", "W"):
            decimal = -decimal
        return decimal
    except:
        return None


def read_gps_position():
    while uart.any():
        line = uart.readline()
        if not line:
            continue

        try:
            data = line.decode("utf-8").strip()
        except:
            continue

        if "RMC" not in data:
            continue

        parts = data.split(",")

        if len(parts) <= 6:
            continue

        status = parts[2]
        if status != "A":
            return None

        lat_raw = parts[3]
        lat_dir = parts[4]
        lon_raw = parts[5]
        lon_dir = parts[6]

        lat = convert_to_decimal(lat_raw, lat_dir, False)
        lon = convert_to_decimal(lon_raw, lon_dir, True)

        if lat is not None and lon is not None:
            return (lat, lon)

    return None


# =========================
# DEL 3: Main
# =========================

print("SX1262 TX init...")
radio_init()

last_sent = 0
send_interval_ms = 5000

while True:
    try:
        pos = read_gps_position()
        now = time.ticks_ms()

        if pos and time.ticks_diff(now, last_sent) >= send_interval_ms:
            lat, lon = pos

            # Kort format så det säkert får plats efter kryptering
            message = "{:.6f},{:.6f}".format(lat, lon)

            print("Sending GPS:", message)
            send_packet(message)
            last_sent = now

        time.sleep_ms(200)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(1)