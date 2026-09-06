#!/usr/bin/env python3

import spidev
import RPi.GPIO as GPIO
import time
import threading

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from datetime import datetime
from gi.repository import GLib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# =========================
# DEL 0: AES-CBC
# =========================

# Delad AES-256-nyckel samt BLE-passkey laddas från config.py,
# som INTE checkas in i git (se .gitignore).
# Skapa din egen config.py lokalt utifrån config_example.py innan drift.
from config import SHARED_KEY, BLE_PASSKEY

BLE_DEVICE_NAME = "LoRa-BLE-Secure"


def pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        raise ValueError("Empty decrypted data")

    pad_len = data[-1]

    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding length")

    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding bytes")

    return data[:-pad_len]


def decrypt_lora_payload(packet: bytes) -> str:
    """
    Format:
    [16 byte IV] + [ciphertext]
    """
    if len(packet) < 32:
        raise ValueError("Packet too short")

    iv = packet[:16]
    ciphertext = packet[16:]

    if len(ciphertext) % 16 != 0:
        raise ValueError("Ciphertext length is not a multiple of 16")

    cipher = Cipher(algorithms.AES(SHARED_KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    plaintext = pkcs7_unpad(padded_plaintext)

    return plaintext.decode("utf-8")


# =========================
# DEL 1: LoRa-konfiguration
# =========================

CS = 8
BUSY = 24
DIO1 = 25
RESET = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(CS, GPIO.OUT)
GPIO.setup(BUSY, GPIO.IN)
GPIO.setup(DIO1, GPIO.IN)
GPIO.setup(RESET, GPIO.OUT)

GPIO.output(CS, 1)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000
spi.mode = 0

latest_lora_message = "waiting for encrypted lora data"
latest_lock = threading.Lock()


def set_latest_message(msg):
    global latest_lora_message
    with latest_lock:
        latest_lora_message = msg


def get_latest_message():
    with latest_lock:
        return latest_lora_message


def wait_busy(timeout=2.0):
    start = time.time()
    while GPIO.input(BUSY):
        if time.time() - start > timeout:
            print("BUSY timeout")
            return False
    return True


def write_cmd(opcode, data=None):
    if data is None:
        data = []
    if not wait_busy():
        return False

    GPIO.output(CS, 0)
    spi.xfer2([opcode] + data)
    GPIO.output(CS, 1)

    return wait_busy()


def read_cmd(opcode, length):
    if not wait_busy():
        return [0] * length

    GPIO.output(CS, 0)
    resp = spi.xfer2([opcode, 0x00] + [0x00] * length)
    GPIO.output(CS, 1)

    wait_busy()
    return resp[2:]


def read_buffer(offset, length):
    if not wait_busy():
        return []

    GPIO.output(CS, 0)
    resp = spi.xfer2([0x1E, offset, 0x00] + [0x00] * length)
    GPIO.output(CS, 1)

    wait_busy()
    return resp[3:]


def reset_radio():
    GPIO.output(RESET, 1)
    time.sleep(0.01)
    GPIO.output(RESET, 0)
    time.sleep(0.01)
    GPIO.output(RESET, 1)
    time.sleep(0.05)


def set_standby():
    write_cmd(0x80, [0x00])


def set_packet_type():
    write_cmd(0x8A, [0x01])  # LoRa


def set_dio2_as_rf_switch():
    write_cmd(0x9D, [0x01])


def set_dio3_as_tcxo():
    write_cmd(0x97, [0x02, 0x00, 0x02, 0x80])


def set_frequency():
    freq = 0x36400000  # 868 MHz
    write_cmd(0x86, list(freq.to_bytes(4, "big")))


def set_modulation():
    # SF7, BW125, CR4/5, LDRO off
    write_cmd(0x8B, [0x07, 0x04, 0x01, 0x00])


def set_packet():
    preamble = 8
    write_cmd(0x8C, [
        (preamble >> 8) & 0xFF,
        preamble & 0xFF,
        0x00,   # explicit header
        64,     # max payload
        0x01,   # CRC on
        0x00    # standard IQ
    ])


def set_buffer_base():
    write_cmd(0x8F, [0x00, 0x00])


def set_dio_irq_params():
    write_cmd(0x08, [
        0x02, 0x42,
        0x02, 0x42,
        0x00, 0x00,
        0x00, 0x00
    ])


def clear_irq():
    write_cmd(0x02, [0xFF, 0xFF])


def get_irq():
    return read_cmd(0x12, 2)


def get_rx_buffer_status():
    return read_cmd(0x13, 2)


def get_packet_status():
    return read_cmd(0x14, 3)


def set_rx():
    write_cmd(0x82, [0xFF, 0xFF, 0xFF])  # Continuous RX


def get_payload():
    status = get_rx_buffer_status()
    length = status[0]
    offset = status[1]

    print("RX buffer status:", status)
    print("Length:", length, "Offset:", offset)

    if length == 0:
        return []

    payload = read_buffer(offset, length)
    print("RAW payload:", payload)
    return payload


def lora_loop():
    print("Receiver poll test start")

    reset_radio()
    set_standby()
    set_packet_type()
    set_dio2_as_rf_switch()
    set_dio3_as_tcxo()
    time.sleep(0.05)
    set_frequency()
    set_modulation()
    set_packet()
    set_buffer_base()
    set_dio_irq_params()
    clear_irq()
    set_rx()

    print("Polling IRQ while listening...")

    while True:
        irq = get_irq()
        irq_value = (irq[0] << 8) | irq[1]
        dio1_state = GPIO.input(DIO1)

        if irq_value != 0 or dio1_state != 0:
            print("DIO1:", dio1_state, "IRQ:", hex(irq_value))

            if irq_value & 0x0002:
                print("RxDone detected")
                payload = get_payload()
                pkt = get_packet_status()
                print("Packet status:", pkt)

                try:
                    text = decrypt_lora_payload(bytes(payload)).strip()
                except Exception as e:
                    text = ""
                    print("Decrypt error:", e)

                print("Decoded:", repr(text))

                if text:
                    set_latest_message(text)
                    print("Latest BLE value updated:", repr(text))

                    with open("lora_log.txt", "a", encoding="utf-8") as f:
                        f.write(f"{datetime.now()} | RX | {text}\n")

            elif irq_value & 0x0040:
                print("CRC error")

            elif irq_value & 0x0200:
                print("RX timeout")

            else:
                print("Other IRQ")

            clear_irq()
            set_rx()

        time.sleep(0.2)


# =========================
# DEL 2: BLE-server + PIN/passkey
# =========================

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
AGENT_MANAGER_IFACE = "org.bluez.AgentManager1"
ADAPTER_IFACE = "org.bluez.Adapter1"
DEVICE_IFACE = "org.bluez.Device1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
AGENT_IFACE = "org.bluez.Agent1"

mainloop = None


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class Rejected(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"


class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = "/"
        self.services = []
        super().__init__(bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for chrc in service.characteristics:
                response[chrc.get_path()] = chrc.get_properties()
        return response


class Service(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/service"

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        super().__init__(bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": dbus.Array(
                    [chrc.get_path() for chrc in self.characteristics],
                    signature="o"
                ),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)


class Characteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + "/char" + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        super().__init__(bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": dbus.Array(self.flags, signature="s"),
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        msg = get_latest_message()
        print("ReadValue called, returning:", repr(msg))
        value = msg.encode("utf-8")
        return [dbus.Byte(b) for b in value]


class TestService(Service):
    TEST_SVC_UUID = "12345678-1234-5678-1234-56789abcdef0"

    def __init__(self, bus, index):
        super().__init__(bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))


class TestCharacteristic(Characteristic):
    TEST_CHRC_UUID = "12345678-1234-5678-1234-56789abcdef1"

    def __init__(self, bus, index, service):
        # Endast läsning efter krypterad + autentiserad pairing/bonding
        super().__init__(
            bus,
            index,
            self.TEST_CHRC_UUID,
            ["encrypt-authenticated-read"],
            service
        )


class Advertisement(dbus.service.Object):
    PATH_BASE = "/org/bluez/example/advertisement"

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = []
        self.local_name = None
        self.include_tx_power = False
        super().__init__(bus, self.path)

    def get_properties(self):
        properties = {
            LE_ADVERTISEMENT_IFACE: {
                "Type": self.ad_type,
            }
        }

        if self.service_uuids:
            properties[LE_ADVERTISEMENT_IFACE]["ServiceUUIDs"] = dbus.Array(
                self.service_uuids, signature="s"
            )

        if self.local_name:
            properties[LE_ADVERTISEMENT_IFACE]["LocalName"] = dbus.String(self.local_name)

        if self.include_tx_power:
            properties[LE_ADVERTISEMENT_IFACE]["Includes"] = dbus.Array(
                ["tx-power"], signature="s"
            )

        return properties

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        print("Advertisement released")


class TestAdvertisement(Advertisement):
    def __init__(self, bus, index):
        super().__init__(bus, index, "peripheral")
        self.service_uuids = ["12345678-1234-5678-1234-56789abcdef0"]
        self.local_name = BLE_DEVICE_NAME
        self.include_tx_power = True


class Agent(dbus.service.Object):
    """
    BlueZ Agent för pairing / passkey-hantering
    """
    AGENT_PATH = "/test/agent"

    def __init__(self, bus):
        super().__init__(bus, self.AGENT_PATH)
        self.bus = bus

    def get_path(self):
        return dbus.ObjectPath(self.AGENT_PATH)

    @dbus.service.method(AGENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        print("Agent released")

    @dbus.service.method(AGENT_IFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print(f"RequestPinCode for {device}, returning fixed PIN")
        return str(BLE_PASSKEY)

    @dbus.service.method(AGENT_IFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print(f"RequestPasskey for {device}, returning fixed passkey {BLE_PASSKEY:06d}")
        return dbus.UInt32(BLE_PASSKEY)

    @dbus.service.method(AGENT_IFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print(f"DisplayPasskey device={device}, passkey={int(passkey):06d}, entered={entered}")

    @dbus.service.method(AGENT_IFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print(f"DisplayPinCode device={device}, pincode={pincode}")

    @dbus.service.method(AGENT_IFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        # Här godkänner vi pairing-försök som når confirmation-steg
        print(f"RequestConfirmation device={device}, passkey={int(passkey):06d} -> accepted")

    @dbus.service.method(AGENT_IFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"RequestAuthorization for {device} -> accepted")

    @dbus.service.method(AGENT_IFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"AuthorizeService device={device}, uuid={uuid} -> accepted")

    @dbus.service.method(AGENT_IFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Agent request canceled")


def find_adapter(bus):
    remote_om = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/"),
        DBUS_OM_IFACE
    )
    objects = remote_om.GetManagedObjects()

    for path, ifaces in objects.items():
        if GATT_MANAGER_IFACE in ifaces and LE_ADVERTISING_MANAGER_IFACE in ifaces:
            return path
    return None


def configure_adapter(bus, adapter_path):
    props = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
        DBUS_PROP_IFACE
    )

    print("Konfigurerar adapter...")

    props.Set(ADAPTER_IFACE, "Powered", dbus.Boolean(1))
    props.Set(ADAPTER_IFACE, "Alias", dbus.String(BLE_DEVICE_NAME))
    props.Set(ADAPTER_IFACE, "Pairable", dbus.Boolean(1))
    props.Set(ADAPTER_IFACE, "PairableTimeout", dbus.UInt32(0))
    props.Set(ADAPTER_IFACE, "Discoverable", dbus.Boolean(1))
    props.Set(ADAPTER_IFACE, "DiscoverableTimeout", dbus.UInt32(0))

    print("Adapter powered, pairable och discoverable")


def register_agent(bus, agent):
    agent_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez"),
        AGENT_MANAGER_IFACE
    )

    try:
        agent_manager.RegisterAgent(agent.get_path(), "KeyboardDisplay")
        print("Agent registered")
    except dbus.exceptions.DBusException as e:
        if "AlreadyExists" in str(e):
            print("Agent already registered, fortsätter")
        else:
            raise

    try:
        agent_manager.RequestDefaultAgent(agent.get_path())
        print("Agent set as default")
    except dbus.exceptions.DBusException as e:
        print("Kunde inte sätta default agent:", str(e))


def register_app_cb():
    print("GATT app registrerad")


def register_app_error_cb(error):
    print("Fel vid registrering av GATT app:", str(error))
    mainloop.quit()


def register_ad_cb():
    print("Advertisement registrerad")
    print("BLE bridge körs säkert")
    print(f"Namn: {BLE_DEVICE_NAME}")
    print(f"Passkey/PIN: {BLE_PASSKEY:06d}")
    print("Karakteristiken kräver autentiserad krypterad läsning")
    print("Para telefonen först, sedan läs karakteristiken")


def register_ad_error_cb(error):
    print("Fel vid registrering av advertisement:", str(error))
    mainloop.quit()


def main():
    global mainloop

    lora_thread = threading.Thread(target=lora_loop, daemon=True)
    lora_thread.start()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    adapter = find_adapter(bus)
    if not adapter:
        print("Ingen BLE-adapter hittades")
        return

    configure_adapter(bus, adapter)

    agent = Agent(bus)
    register_agent(bus, agent)

    service_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        GATT_MANAGER_IFACE
    )

    ad_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter),
        LE_ADVERTISING_MANAGER_IFACE
    )

    app = Application(bus)
    app.add_service(TestService(bus, 0))
    adv = TestAdvertisement(bus, 0)

    mainloop = GLib.MainLoop()

    service_manager.RegisterApplication(
        app.get_path(), {},
        reply_handler=register_app_cb,
        error_handler=register_app_error_cb
    )

    ad_manager.RegisterAdvertisement(
        adv.get_path(), {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb
    )

    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        try:
            agent_manager = dbus.Interface(
                bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez"),
                AGENT_MANAGER_IFACE
            )
            agent_manager.UnregisterAgent(agent.get_path())
        except Exception:
            pass

        spi.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()