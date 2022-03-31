from xml.etree.ElementTree import XMLID
from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import xlsxwriter


def main():
    url = "https://humanservices.arkansas.gov/divisions-shared-services/provider-services-quality-assurance/consumer-long-term-care-information/long-term-care-facility-search/"

    html_content = requests.get(url).text
    # The results dict will store the page url as the key with the attributes held as a dict mapping attributes and values.
    results: defaultdict[dict[str, str]] = defaultdict(dict)

    soup = BeautifulSoup(html_content)
    table = soup.find("table", {"id": "table_1"})
    for i, x in enumerate(table.find_all("td")):
        has_link = x.find_all("a", href=True)
        if has_link:
            link_url = has_link[0].get("href")
            html = requests.get(link_url).text
            inner_soup = BeautifulSoup(html)
            for div in inner_soup.find_all("div", {"class": "elementor-text-editor"}):
                if len(div.text.split(":-")) == 2:
                    key, val = div.text.split(":-")
                results[str(link_url)][key] = val
        if i % 10 == 0:
            print(f"Finished adding {i} urls to spreadsheet.")

    print(results)

    workbook = xlsxwriter.Workbook("Arkansas.xlsx")
    worksheet = workbook.add_worksheet()
    row = 1
    first_row = True

    # Write out the xlsx.
    for key, attrs in results.items():
        worksheet.write(row, 0, key)
        for i, (attr, value) in enumerate(attrs.items(), start=1):
            if first_row:
                worksheet.write(0, i, attr)
            worksheet.write(row, i, value)
        first_row = False
        row += 1

    workbook.close()


if __name__ == "__main__":
    main()
