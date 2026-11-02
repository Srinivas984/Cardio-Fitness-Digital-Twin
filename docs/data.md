# Data and API reference

## Local CSV input

Place one Health Auto Export daily CSV named `HealthAutoExport-<anything>.csv` in `data/`. `app_final.py` selects the first matching file. Loading is cached; restart after changing input. If parsing fails or no file exists, the dashboard falls back to demo defaults.

`examples/HealthAutoExport-demo.csv` is generated synthetic data, not a user's health export.

The parser requires `Date/Time`, interpretable by Pandas. Supported columns include:

| Column | Meaning |
| --- | --- |
| `Heart Rate Variability (ms)` | Daily SDNN |
| `Resting Heart Rate (count/min)` | Resting HR |
| `Heart Rate [Avg] (count/min)` | Average HR |
| `Heart Rate [Min] (count/min)` | Minimum HR |
| `Heart Rate [Max] (count/min)` | Maximum HR |
| `Step Count (count)` | Daily steps |
| `Active Energy (kJ)` | Active energy in kilojoules |
| `Respiratory Rate (count/min)` | Breathing rate |
| `Blood Oxygen Saturation (%)` | Oxygen saturation |
| `Walking + Running Distance (km)` | Distance |

Include HRV and resting-HR columns for trend calculations. The parser also recognizes sleep and VO2-max fields; see its column mappings for exact names. Derived recovery, HR-recovery-rate, fatigue, and zone values include assumptions and demo values.

The alternative `app.py` dashboard optionally reads Apple Health XML at `data/export.xml`. The main dashboard does not provide a general XML upload interface.

## Local API

Start with `python healthkit_api_server.py`. The default address is `http://127.0.0.1:5000`. Incoming data is stored in memory and cleared on restart.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Server status |
| GET | `/api/metrics` | Current demo or uploaded metrics |
| GET | `/api/iphone` | Upload freshness/status |
| GET | `/api/heart_rate` | Demo heart rate |
| GET | `/api/hrv` | Demo HRV |
| POST | `/api/upload` | Submit heart rate, steps, and active energy |
| GET | `/api/risk/combined` | Experimental combined risk output |

Upload synthetic values:

```bash
curl -X POST http://127.0.0.1:5000/api/upload -H "Content-Type: application/json" -d '{"heart_rate":75,"steps":5000,"active_energy":250}'
```

PowerShell equivalent:

```powershell
$body = @{ heart_rate = 75; steps = 5000; active_energy = 250 } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:5000/api/upload -Method Post -ContentType 'application/json' -Body $body
```

All three fields are required. API active energy is in kcal, unlike the CSV's kJ field. Uploaded readings are used by `/api/metrics` for five minutes, then demo values resume. Estimated HRV is not measured HRV. Individual demo endpoints do not all switch to uploaded data.

The connector does not implement direct Apple Watch authentication, native HealthKit access, or iCloud sync. Supplying real readings requires a separate client or bridge. Loopback binding permits only clients on this computer. LAN/device use requires explicit network configuration and additional access controls; the launcher does not configure it.
