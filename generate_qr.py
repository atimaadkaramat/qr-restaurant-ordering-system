import qrcode # type: ignore
import os

BASE_URL = "http://127.0.0.1:5000"

output_folder = "static/qr"

os.makedirs(output_folder, exist_ok=True)

for table_number in range(1, 11):

    url = f"{BASE_URL}/table/{table_number}"

    qr = qrcode.make(url)

    qr.save(f"{output_folder}/table_{table_number}.png")

    print(f"Generated QR for Table {table_number}")

print("All QR codes generated successfully!")