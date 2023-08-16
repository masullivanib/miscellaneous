import re
import requests
import time

domain = 'https://www.interactivebrokers.com'
# 100 results per page baked in
path_mask = '/en/index.php?f=2222&exch={}&showcategories={}&p=&ptab=&cc=&limit=100&page={}'
url_mask = domain + path_mask

exch = 'island'
sec_type = 'STK'
print(f"Exchange: {exch}, SecType: {sec_type}")

print(f"Requesting page 1 of unknown number...")
p1_response = requests.get(url_mask.format(exch, sec_type, 1))
print(f"Response: status {p1_response.status_code} {p1_response.reason}")
p1_content = p1_response.content.decode("utf-8")

max_page_path = path_mask.format(exch, sec_type, '(\d*)')
max_page_path = max_page_path.replace('.', '\.').replace('?', '\?')
max_page_pattern = re.compile(f"<ul class='pagination'>[\s\S]*<li><a href.*{max_page_path}[\s\S]*<\/ul>")
max_page = int(max_page_pattern.findall(p1_content)[0])
print(f"Total number of pages for {exch}/{sec_type}: {max_page}")

conid_pattern = re.compile(r"<tr>\s*<td>([A-Z\s]+)<\/td>\s*<td><a.*conid=(\d+).*>(.*)<\/a><\/td>")

# yields list of tuples in form (symbol, conid, instrument/business name)
instruments = conid_pattern.findall(p1_content)
print(f"Page 1, found {len(instruments)} instruments: {instruments[0][0]} through {instruments[-1][0]}")

for page in range(2, max_page+1):
    time.sleep(1)
    print(f"Requesting page {page} of {max_page}...")
    page_response = requests.get(url_mask.format(exch, sec_type, page))
    print(f"Response: status {page_response.status_code} {page_response.reason}")
    page_content = page_response.content.decode("utf-8")
    page_matches = conid_pattern.findall(page_content)
    print(f"Page {page}, found {len(page_matches)} instruments: {page_matches[0][0]} through {page_matches[-1][0]}")
    instruments.extend(page_matches)
    
for m in instruments:
    print(f"Symbol={m[0]:<12} Name={m[2]:<40} Conid={m[1]}")
print(f"Exchange={exch} SecType={sec_type} NumPages={max_page} NumInstruments={len(instruments)}")