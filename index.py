import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

# ---------------- CONFIG ----------------
IPINFO_BASE_URL = "https://ipinfo.io"

# Country flag emojis
def get_flag_emoji(country_code):
    if not country_code:
        return "🌍"
    try:
        return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)
    except:
        return "🌍"

# ---------------- HELPER FUNCTIONS ----------------
def validate_ip(ip):
    """Validate IPv4 and IPv6 addresses"""
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return True
    elif re.match(ipv6_pattern, ip):
        return True
    return False

def get_ip_info(ip_address):
    """Fetch IP information from ipinfo.io"""
    try:
        url = f"{IPINFO_BASE_URL}/{ip_address}/geo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Remove readme if present
            if "readme" in data:
                del data["readme"]
            
            # Add enhanced information
            if "country" in data:
                data["country_flag"] = get_flag_emoji(data["country"])
                data["country_name"] = get_country_name(data["country"])
            
            if "loc" in data:
                lat, lon = data["loc"].split(",")
                data["latitude"] = lat.strip()
                data["longitude"] = lon.strip()
                data["google_maps"] = f"https://www.google.com/maps?q={lat},{lon}"
            
            # Add timestamp
            data["checked_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            data["checked_timestamp"] = int(datetime.utcnow().timestamp())
            
            # Add developer info
            data["api_info"] = {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers",
                "version": "2.0.0"
            }
            
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"Failed to fetch IP info: {response.status_code}"}
            
    except requests.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def get_country_name(country_code):
    """Get full country name from code"""
    countries = {
        "IN": "India", "US": "United States", "GB": "United Kingdom",
        "CA": "Canada", "AU": "Australia", "DE": "Germany",
        "FR": "France", "JP": "Japan", "CN": "China",
        "BR": "Brazil", "RU": "Russia", "ZA": "South Africa",
        "AE": "United Arab Emirates", "SG": "Singapore", "NZ": "New Zealand",
        "PK": "Pakistan", "BD": "Bangladesh", "NP": "Nepal", "LK": "Sri Lanka",
        "IT": "Italy", "ES": "Spain", "MX": "Mexico", "KR": "South Korea",
        "ID": "Indonesia", "TR": "Turkey", "SA": "Saudi Arabia",
        "NG": "Nigeria", "EG": "Egypt", "VN": "Vietnam", "TH": "Thailand",
        "MY": "Malaysia", "PH": "Philippines", "IR": "Iran", "IQ": "Iraq",
    }
    return countries.get(country_code, country_code)

def batch_lookup(ips):
    """Perform batch lookup for multiple IPs"""
    results = []
    for ip in ips:
        ip = ip.strip()
        if validate_ip(ip):
            info = get_ip_info(ip)
            if info["success"]:
                results.append(info["data"])
            else:
                results.append({"ip": ip, "error": info["error"]})
        else:
            results.append({"ip": ip, "error": "Invalid IP address"})
    return results

# ---------------- HTML TEMPLATE ----------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IP Information API - Nexxon Hackers</title>
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<script>tailwind.config={theme:{extend:{colors:{primary:'#3b82f6',secondary:'#1e40af'},borderRadius:{'none':'0px','sm':'4px',DEFAULT:'8px','md':'12px','lg':'16px','xl':'20px','2xl':'24px','3xl':'32px','full':'9999px','button':'8px'}}}}</script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.6.0/remixicon.min.css" rel="stylesheet">
<style>
.loading-spinner {
    border: 2px solid #f3f3f3;
    border-top: 2px solid #3b82f6;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
    display: inline-block;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.json-viewer {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.5;
}
.json-key { color: #9cdcfe; }
.json-string { color: #ce9178; }
.json-number { color: #b5cea8; }
.json-boolean { color: #569cd6; }
.json-null { color: #569cd6; }
</style>
</head>
<body class="bg-gray-50 min-h-screen">
<main class="pt-8 pb-12 px-4 max-w-4xl mx-auto">
    
    <!-- Header -->
    <header class="text-center py-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary to-secondary rounded-2xl mb-4">
            <i class="ri-earth-line text-white ri-2x"></i>
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">IP Information API</h1>
        <p class="text-lg text-gray-600 mb-2">Advanced IP Geolocation & Intelligence Service</p>
        <p class="text-sm text-gray-500">Precise Location Data • Real-time Intelligence • Batch Support</p>
    </header>

    <!-- Live Test Section -->
    <section class="mb-8 bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <i class="ri-flask-line text-primary mr-2"></i>
            Live API Test
        </h2>
        <div class="flex flex-col sm:flex-row gap-3 mb-4">
            <input type="text" id="ipInput" placeholder="Enter IP address (e.g., 8.8.8.8)" 
                   class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none">
            <button id="testBtn" class="bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-secondary transition flex items-center justify-center gap-2">
                <i class="ri-search-line"></i>
                <span>Lookup IP</span>
            </button>
        </div>
        <div class="flex gap-2 mb-4">
            <button onclick="document.getElementById('ipInput').value='8.8.8.8'; document.getElementById('testBtn').click()" 
                    class="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-gray-700 transition">
                Try 8.8.8.8
            </button>
            <button onclick="document.getElementById('ipInput').value='1.1.1.1'; document.getElementById('testBtn').click()" 
                    class="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-gray-700 transition">
                Try 1.1.1.1
            </button>
            <button onclick="document.getElementById('ipInput').value='208.67.222.222'; document.getElementById('testBtn').click()" 
                    class="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-gray-700 transition">
                Try OpenDNS
            </button>
        </div>
        <div id="responseContainer" class="hidden">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Response:</span>
                <button id="copyBtn" class="text-xs text-primary hover:text-secondary flex items-center gap-1">
                    <i class="ri-file-copy-line"></i> Copy
                </button>
            </div>
            <pre id="responseDisplay" class="json-viewer"></pre>
        </div>
        <div id="loadingIndicator" class="hidden text-center py-8">
            <div class="loading-spinner"></div>
            <span class="ml-2 text-gray-500">Fetching IP information...</span>
        </div>
        <div id="errorDisplay" class="hidden bg-red-50 border border-red-200 rounded-lg p-4 text-red-700"></div>
    </section>

    <!-- Features Grid -->
    <section class="mb-8">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
                <div class="flex items-center">
                    <div class="w-10 h-10 flex items-center justify-center bg-blue-100 rounded-xl mr-3">
                        <i class="ri-map-pin-line text-blue-600 ri-lg"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Precise Location</h4>
                        <p class="text-xs text-gray-600">City, Region & Coordinates</p>
                    </div>
                </div>
            </div>
            <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-5 border border-green-100">
                <div class="flex items-center">
                    <div class="w-10 h-10 flex items-center justify-center bg-green-100 rounded-xl mr-3">
                        <i class="ri-map-2-line text-green-600 ri-lg"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Google Maps</h4>
                        <p class="text-xs text-gray-600">Direct Map Integration</p>
                    </div>
                </div>
            </div>
            <div class="bg-gradient-to-r from-purple-50 to-violet-50 rounded-xl p-5 border border-purple-100">
                <div class="flex items-center">
                    <div class="w-10 h-10 flex items-center justify-center bg-purple-100 rounded-xl mr-3">
                        <i class="ri-stack-line text-purple-600 ri-lg"></i>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900">Batch Support</h4>
                        <p class="text-xs text-gray-600">Multiple IPs at Once</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- API Endpoints -->
    <section class="mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4">API Endpoints</h2>
        <div class="space-y-4">
            
            <!-- Single IP -->
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-gray-900">Single IP Lookup</h3>
                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">GET</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-3 mb-3">
                    <code class="text-green-400 text-sm">/ip-info/ip?ip={IP_ADDRESS}</code>
                </div>
                <div class="bg-blue-50 rounded-lg p-3 border border-blue-200">
                    <p class="text-xs font-medium text-blue-900 mb-1">Example:</p>
                    <code class="text-xs text-blue-700">curl "https://api.example.com/ip-info/ip?ip=8.8.8.8"</code>
                </div>
            </div>

            <!-- Batch IP (Comma) -->
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-gray-900">Batch IP Lookup (Comma)</h3>
                    <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">GET</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-3 mb-3">
                    <code class="text-green-400 text-sm">/ip-info/ip?ip={IP1},{IP2},{IP3}</code>
                </div>
                <div class="bg-blue-50 rounded-lg p-3 border border-blue-200">
                    <p class="text-xs font-medium text-blue-900 mb-1">Example:</p>
                    <code class="text-xs text-blue-700">curl "https://api.example.com/ip-info/ip?ip=8.8.8.8,1.1.1.1"</code>
                </div>
            </div>

            <!-- Batch IP (POST) -->
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="font-semibold text-gray-900">Batch IP Lookup (POST)</h3>
                    <span class="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">POST</span>
                </div>
                <div class="bg-gray-900 rounded-lg p-3 mb-3">
                    <code class="text-green-400 text-sm">/ip-info/batch</code>
                </div>
                <div class="bg-blue-50 rounded-lg p-3 border border-blue-200">
                    <p class="text-xs font-medium text-blue-900 mb-1">Request Body:</p>
                    <code class="text-xs text-blue-700">{"ips": ["8.8.8.8", "1.1.1.1", "208.67.222.222"]}</code>
                </div>
            </div>

        </div>
    </section>

    <!-- Sample Response -->
    <section class="mb-8 bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
        <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <i class="ri-code-line text-primary mr-2"></i>
            Sample Response
        </h2>
        <pre class="json-viewer text-xs">{
  "success": true,
  "data": {
    "ip": "8.8.8.8",
    "city": "Mountain View",
    "region": "California",
    "country": "US",
    "country_flag": "🇺🇸",
    "country_name": "United States",
    "loc": "37.4056,-122.0775",
    "latitude": "37.4056",
    "longitude": "-122.0775",
    "google_maps": "https://www.google.com/maps?q=37.4056,-122.0775",
    "org": "AS15169 Google LLC",
    "postal": "94043",
    "timezone": "America/Los_Angeles",
    "checked_at": "2024-01-15 10:30:45 UTC",
    "checked_timestamp": 1705315245,
    "api_info": {
      "developed_by": "Creator Shyamchand & Ayan",
      "organization": "CEO & Founder Of - Nexxon Hackers",
      "version": "2.0.0"
    }
  }
}</pre>
    </section>

    <!-- Developer Credit -->
    <div class="text-center py-6">
        <div class="inline-block bg-gradient-to-r from-primary to-secondary text-white px-6 py-3 rounded-full">
            <p class="font-medium">Developed by Creator Shyamchand & Ayan</p>
            <p class="text-sm opacity-90">CEO & Founder Of - Nexxon Hackers</p>
        </div>
    </div>

</main>

<script>
function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, function (match) {
        var cls = 'json-number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'json-key';
                match = match.slice(0, -1) + '</span>:';
                return '<span class="' + cls + '">' + match;
            } else {
                cls = 'json-string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'json-boolean';
        } else if (/null/.test(match)) {
            cls = 'json-null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

document.getElementById('testBtn').addEventListener('click', async function() {
    const ipInput = document.getElementById('ipInput');
    const ip = ipInput.value.trim();
    
    if (!ip) {
        alert('Please enter an IP address');
        return;
    }
    
    const responseContainer = document.getElementById('responseContainer');
    const responseDisplay = document.getElementById('responseDisplay');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorDisplay = document.getElementById('errorDisplay');
    
    responseContainer.classList.add('hidden');
    errorDisplay.classList.add('hidden');
    loadingIndicator.classList.remove('hidden');
    
    try {
        const response = await fetch('/ip-info/ip?ip=' + encodeURIComponent(ip));
        const data = await response.json();
        
        loadingIndicator.classList.add('hidden');
        
        const jsonStr = JSON.stringify(data, null, 2);
        responseDisplay.innerHTML = syntaxHighlight(jsonStr);
        responseContainer.classList.remove('hidden');
        
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        errorDisplay.textContent = 'Error: ' + error.message;
        errorDisplay.classList.remove('hidden');
    }
});

document.getElementById('copyBtn').addEventListener('click', function() {
    const responseDisplay = document.getElementById('responseDisplay');
    const text = responseDisplay.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyBtn');
        btn.innerHTML = '<i class="ri-check-line"></i> Copied!';
        setTimeout(() => {
            btn.innerHTML = '<i class="ri-file-copy-line"></i> Copy';
        }, 2000);
    });
});

// Enter key support
document.getElementById('ipInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('testBtn').click();
    }
});
</script>
</body>
</html>
'''

# ---------------- FLASK ROUTES ----------------
@app.route('/')
def home():
    """Home page with API documentation"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/ip-info/ip', methods=['GET'])
def ip_lookup():
    """Single IP lookup endpoint"""
    ip_param = request.args.get('ip')
    
    if not ip_param:
        return jsonify({
            "success": False,
            "error": "Missing 'ip' parameter",
            "usage": {
                "endpoint": "/ip-info/ip?ip=IP_ADDRESS",
                "example": "/ip-info/ip?ip=8.8.8.8"
            },
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 400
    
    # Handle multiple IPs separated by comma
    if ',' in ip_param:
        ips = [ip.strip() for ip in ip_param.split(',')]
        results = batch_lookup(ips)
        
        return jsonify({
            "success": True,
            "batch_mode": True,
            "total": len(results),
            "results": results,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
    
    # Single IP lookup
    if not validate_ip(ip_param):
        return jsonify({
            "success": False,
            "error": "Invalid IP address format",
            "provided_ip": ip_param,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 400
    
    result = get_ip_info(ip_param)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify({
            "success": False,
            "error": result["error"],
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 500

@app.route('/ip-info/batch', methods=['POST'])
def batch_ip_lookup():
    """Batch IP lookup endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'ips' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'ips' array in request body",
                "example": {"ips": ["8.8.8.8", "1.1.1.1"]},
                "api_info": {
                    "developed_by": "Creator Shyamchand & Ayan",
                    "organization": "CEO & Founder Of - Nexxon Hackers"
                }
            }), 400
        
        ips = data['ips']
        if not isinstance(ips, list):
            return jsonify({
                "success": False,
                "error": "'ips' must be an array",
                "api_info": {
                    "developed_by": "Creator Shyamchand & Ayan",
                    "organization": "CEO & Founder Of - Nexxon Hackers"
                }
            }), 400
        
        results = batch_lookup(ips)
        
        return jsonify({
            "success": True,
            "total_requested": len(ips),
            "total_processed": len(results),
            "results": results,
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "api_info": {
                "developed_by": "Creator Shyamchand & Ayan",
                "organization": "CEO & Founder Of - Nexxon Hackers"
            }
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": {
            "home": "/",
            "single_ip": "/ip-info/ip?ip=IP_ADDRESS",
            "batch_ip": "/ip-info/batch (POST)"
        },
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "api_info": {
            "developed_by": "Creator Shyamchand & Ayan",
            "organization": "CEO & Founder Of - Nexxon Hackers"
        }
    }), 500

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
