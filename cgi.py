import sys, types

if 'cgi' not in sys.modules:
    cgi = types.ModuleType('cgi')

    def escape(s, quote=False):
        if not isinstance(s, str):
            s = str(s)
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if quote:
            s = s.replace('"', "&quot;")
        return s

    def parse_header(line):
        parts = line.split(';')
        key = parts[0].strip().lower()
        pdict = {}
        for item in parts[1:]:
            if '=' in item:
                k, v = item.split('=', 1)
                pdict[k.strip().lower()] = v.strip().strip('"')
        return key, pdict

    cgi.escape = escape
    cgi.parse_header = parse_header
    sys.modules['cgi'] = cgi

# -------------------------------------------------------------------