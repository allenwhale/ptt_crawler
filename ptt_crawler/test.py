def remove_email_protection(soup):
    email_tags = soup.find_all('a', class_="__cf_email__")
    for tag in email_tags:
	data = tag['data-cfemail']
	r = int('0x%s'%data[0:2], 16)
	d = ''
	for i in range(2, len(data), 2):
	    c = hex(int('0x%s'%data[i:i+2], 16) ^ r)[2:4]
	    d += '%'
	    d += c
	new_tag = soup.new_tag("email")
	new_tag.string = urllib.parse.unquote(d)
	tag.replace_with(new_tag)
    for tag in soup.find_all("email"):
	tag.unwrap()
    return soup
