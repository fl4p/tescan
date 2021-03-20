import atexit
import json
import signal
import socket

from flask import Response

from tescan.can import CANMonitor
from tescan.obd import ObdSocket
from tescan.record import Recorder
# Device specific information
from tescan.util import exit_process


def main():
    m5stick_addr = '00:04:3E:96:97:47'
    port = 1  # This needs to match M5Stick setting

    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((m5stick_addr, port))

    obd = ObdSocket(s)
    mon = CANMonitor(obd, dbc='dbc/Model3CAN.dbc')

    mon.monitor(monitor_ids=(
        "ID132HVBattAmpVolt",  # 306
        "ID352BMS_energyStatus",
        "ID292BMS_SOC",  # SoC
        "ID33AUI_rangeSOC",
        "ID3F2BMSCounters",  # charging counters
        "ID3D2TotalChargeDischarge",

        "ID257UIspeed",  # driving speed
        "ID3B6odometer",

        "ID261_12vBattStatus",  # 609
        "ID2B4PCS_dcdcRailStatus",  # 12V dcdc
        "ID2C4PCS_logging",  # 708, lot of signals, PCS_dcdc12vSupportLifetimekWh

        # "ID224PCSDCDCstatus", #548 no numbers
        532,
        # "ID21DCP_evseStatus", # no numbers
        "ID264ChargeLineStatus",
        "ID29DCP_dcChargeStatus",
        # "ID287PTCcabinHeatSensorStatus", # not interessting
        # "ID2B3VCRIGHT_logging1Hz" # hvac stuff, temps, not interessted atm

        # "ID2F1VCFRONT_eFuseDebugStatus", # pump & air comp no usable numbers

        "ID405VIN",  # 1029
        "ID252BMS_powerAvailable",  # 594

        "ID108DIR_torque",
        "ID186DIF_torque",
        "ID111RCM_inertial2",
        # "ID3F3UI_odo", # no data
        "ID267DI_vehicleEstimates",
        "ID287PTCcabinHeatSensorStatus",
        "ID334UI_powertrainControl",
        "ID3BBUI_power",
        "ID336MaxPowerRating",
        "ID268SystemPower",
        "ID321VCFRONT_sensors",
        "ID3D8Elevation",
        "ID2A8CMPD_state",
        "ID528UnixTime",
        "ID2E1VCFRONT_status",

        "ID383VCRIGHT_thsStatus",
        "ID263VCRIGHT_logging10Hz",
        "ID20CVCRIGHT_hvacRequest"
    ))

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return Response(json.dumps(mon.signal_values, sort_keys=True, indent=4), mimetype='application/json')

        # return jsonify(mon.signal_values)

    record_fields = {
        # TODO declare data type (int, float), eps, sampling interval
        "ID132HVBattAmpVolt": {"BattVoltage132", "ChargeHoursRemaining132", "RawBattCurrent132",
                               "SmoothBattCurrent132"},
        "ID214FastChargeVA": {"FC_dcCurrent", "FC_dcVoltage"},

        "ID261_12vBattStatus": {"v12vBattCurrent261", "v12vBattVoltage261", },  # falsy data

        "ID292BMS_SOC": {"BattBeginningOfLifeEnergy292", "SOCUI292", "SOCave292", "BMS_battTempPct"},

        "ID2C4PCS_logging": {"PCS_5VNMax10s", "PCS_chgOutputV", "PCS_dcdc12vSupportLifetimekWh",
                             "PCS_dcdcMaxLvOutputCurrent",
                             "PCS_chgPhALifetimekWh", "PCS_chgPhBLifetimekWh", "PCS_chgPhCLifetimekWh", },

        # DCDC stuff
        "ID2B4PCS_dcdcRailStatus": {"PCS_dcdcHvBusVolt", "PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"},

        "ID33AUI_rangeSOC": {"UI_Range", "UI_SOC", "UI_ratedWHpM", },
        "ID352BMS_energyStatus": {"BMS_nominalEnergyRemaining", "BMS_nominalFullPackEnergy"},
        "ID3D2TotalChargeDischarge": {"TotalChargeKWh3D2", "TotalDischargeKWh3D2"},
        "ID3F2BMSCounters": {"BMStotalACcharge3F2", "BMStotalDCcharge3F2", "BMStotalDriveDischarge3F2",
                             "BMStotalRegenCharge3F2"},

        "ID264ChargeLineStatus": {"ChargeLinePower264", "ChargeLineCurrentLimit264", "ChargeLineVoltage264",
                                  "ChargeLineCurrent264"},

        "ID252BMS_powerAvailable": {"BMS_maxDischargePower", "BMS_maxRegenPower", },

        "ID108DIR_torque": {"DIR_axleSpeed", "DIR_torqueActual"},
        "ID186DIF_torque": {"DIF_axleSpeed", "DIF_torqueActual"},
        "ID111RCM_inertial2": {"RCM_lateralAccel", "RCM_longitudinalAccel", "RCM_verticalAccel"},

        "ID29DCP_dcChargeStatus": {"CP_evseOutputDcCurrent", "CP_evseOutputDcVoltage"},
        # "ID3F3UI_odo": {"UI_odometer"},
        "ID267DI_vehicleEstimates": {"DI_mass"},

        "ID287PTCcabinHeatSensorStatus": {"PTC_leftCurrentHV", "PTC_rightCurrentHV", "PTC_voltageHV"},

        "ID334UI_powertrainControl": {"UI_systemPowerLimit", "UI_systemTorqueLimit"},

        "ID321VCFRONT_sensors": {"VCFRONT_tempAmbient", "VCFRONT_tempAmbientFiltered"},

        "ID3D8Elevation": {"Elevation3D8"},
        # "ID2F1VCFRONT_eFuseDebugStatus": "todo", # TODO

        # ID2E5FrontInverterPower TODO

        "ID383VCRIGHT_thsStatus": {"VCRIGHT_estimatedThsSolarLoad", "VCRIGHT_thsHumidity",
                                   "VCRIGHT_thsSolarLoadInfrared", "VCRIGHT_thsTemperature",
                                   "VCRIGHT_thsSolarLoadVisible"},

        "ID263VCRIGHT_logging10Hz": {"VCRIGHT_hvacCabinHumidityLevel", },
        "ID243VCRIGHT_hvacStatus": {"VCRIGHT_hvacCabinTempEst", "VCRIGHT_hvacMassflowRefrigSystem",
                                    "VCRIGHT_hvacQdotLeft", "VCRIGHT_hvacQdotRight"},
        "ID20CVCRIGHT_hvacRequest": {"VCRIGHT_wattsDemandEvap", "VCRIGHT_tempAmbientRaw", "VCRIGHT_tempEvaporator",
                                     "VCRIGHT_tempEvaporatorTarget"},
    }

    def on_timeout():
        try:
            rec.flush()
        except:
            pass
        print('Exiting process!')
        exit_process()

    def on_exit(*args, **kwargs):
        print('exit signal handler...')
        rec.flush()
        exit_process()

    atexit.register(on_exit)
    # noinspection PyTypeChecker
    signal.signal(signal.SIGTERM, on_exit)
    # noinspection PyTypeChecker
    signal.signal(signal.SIGINT, on_exit)

    rec = Recorder(mon, record_fields, on_timeout=on_timeout)
    rec.start()

    print('starting webserver...')
    app.run(host='0.0.0.0')


main()
