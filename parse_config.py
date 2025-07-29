import re

def parse_saved_requests(text) -> dict:
    result = {}
    current_section = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        section_match = re.match(r"\[\[([^\]]+)\]\]", line)
        if section_match:
            current_section = section_match.group(1)
            result[current_section] = []
            continue


        if "request:" in line and current_section:
            parts = line.split(" ")
            method = parts[1]
            url = parts[2]
            result[current_section].append({"method": method, "url": url})

    return result


# Example usage:
text = """
[[pokemon]]
request: GET https://pokeapi.co/api/v2/pokemon/ditto
request: GET https://pokeapi.co/api/v2/pokemon/pikachu
request: GET https://pokeapi.co/api/v2/pokemon/charmander

[[personal]]
request: POST http://localhost:8000/items
"""

# parsed = parse_saved_requests(text)
# print(parsed)

# for k,v in parsed.items():
#         for x in v:
#             print(x.get("url"))