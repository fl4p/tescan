import json
import socket

from flask import Response

from tescan.can import CANMonitor
from tescan.obd import ObdSocket
from tescan.record import Recorder


# Device specific information


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
        "ID252BMS_powerAvailable", # 594
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
        "ID261_12vBattStatus": {"v12vBattCurrent261", "v12vBattVoltage261", },
        "ID292BMS_SOC": {"BattBeginningOfLifeEnergy292", "SOCUI292"},
        "ID2C4PCS_logging": {"PCS_5VNMax10s", "PCS_chgOutputV", "PCS_dcdc12vSupportLifetimekWh",
                             "PCS_dcdcMaxLvOutputCurrent",
                             "PCS_chgPhALifetimekWh", "PCS_chgPhBLifetimekWh", "PCS_chgPhCLifetimekWh", },
        "ID2B4PCS_dcdcRailStatus": {"PCS_dcdcHvBusVolt", "PCS_dcdcLvBusVolt", "PCS_dcdcLvOutputCurrent"},
        "ID33AUI_rangeSOC": {"UI_Range", "UI_SOC", "UI_ratedWHpM", },
        "ID352BMS_energyStatus": {"BMS_nominalEnergyRemaining", "BMS_nominalFullPackEnergy"},
        "ID3D2TotalChargeDischarge": {"TotalChargeKWh3D2", "TotalDischargeKWh3D2"},
        "ID3F2BMSCounters": {"BMStotalACcharge3F2", "BMStotalDCcharge3F2", "BMStotalDriveDischarge3F2",
                             "BMStotalRegenCharge3F2"},

        "ID264ChargeLineStatus": {"ChargeLinePower264", "ChargeLineCurrentLimit264", "ChargeLineVoltage264",
                                  "ChargeLineCurrent264"},

        "ID252BMS_powerAvailable": {"BMS_maxDischargePower","BMS_maxRegenPower", },

        # "ID2F1VCFRONT_eFuseDebugStatus": "todo", # TODO

        # ID2E5FrontInverterPower TODO
    }

    rec = Recorder(mon, record_fields)
    rec.start()

    print('starting webserver...')
    app.run(host='0.0.0.0')


main()
