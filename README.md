# MIP0505
python class for Midi Ingenierie MIP0505 stepper motor driver

<img src="https://www.midi-ingenierie.com/wp-content/uploads/2021/02/cropped-logo_midi_ingenierie2021.png" alt="Logo Midi" style="width:25%;">

MIP0505 class is a wrapper of python minimalmodbus module customized for easy implementation with MIP0505 drivers

![France](https://raw.githubusercontent.com/stevenrskelton/flag-icon/master/png/16/country-4x3/fr.png "France") Some comments are in french. Translation will be done later.

*The provided code is for informational purposes only. We are not liable for any malfunctions or issues resulting from its use.*

## Additional resources

[Midi Ingenierie](https://www.midi-ingenierie.com)

[Minimalmodbus](https://minimalmodbus.readthedocs.io)

## Typical usage

```python
import MIP0505

mip = MIP0505(portCOM='COM2',modbusAddress=1)

# --- Example reading registers ---
alim = mip.read('SUPPLY_VOLTAGE')
print(f"Supply voltage: {alim/100}V")
stat = mip.read('STATUS_MOTOR')
print(f"Status Register: 0x{stat:08x}")

# --- Example writing registers ---
mip.write('PROFILE_VELOCITY',2400)
mip.write('TARGET_POS_ABS',-290579)

```
