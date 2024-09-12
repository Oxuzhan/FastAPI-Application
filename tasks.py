
from celery import group
from celery1 import fetch_data  # Celery görevlerini aktarma

# Şirket ID'leri listesi
ids = [
    "8483fc50-b82d-5ffa-5f92-6c72ac4bdaff",
    "5d6ed201-f032-68af-b422-7e7c68129485",
    "852741cb-f453-48ad-b13b-e74781d7084d",
    "b462608d-8bf4-93f1-4f68-e41ee10f0df2",
    "315e1e59-3784-ab73-9c4a-447d2616ae82",
    "8a2b18d2-4cfb-ac17-08b2-07b01d092e2a",
    "6c3fdb81-9b38-726d-1ed5-f46c563aa5f4",
    "ab47d80c-7971-c8e6-b620-7483498d0c5b",
    "0d2b82ad-bd6f-9f54-c76a-448a455af317",
    "75d88e2b-258a-b0c8-e980-38855b56a2bc",
    "68255d6d-1614-4c7c-1a0b-3d3998c1d2c2",
    "7ca7dc60-4543-ea08-2062-5525859c42d3",
    "acc1d0fc-3798-4578-8981-524fe10361de",
    "ba08a876-9044-e504-c63e-a18974a8f942",
    "f82127e6-3f7d-1ed0-4906-a61daf4135b0",
    "95acbd57-b0f8-eeb6-c8f4-c71224afbe4f",
    "148130a7-ee8d-47d1-9f3d-40a42bcf7e5e",
    "cd83a724-0a0a-da6e-f066-7dbaf992a19d",
    "767f11a2-9dc4-4162-858a-509813260702",
    "03099c0f-ed6a-d0ea-bf12-1347b36ed611",
    "7a1dde00-5809-1010-15a7-8d65012685ec",
    "0d5171b3-68b3-37c3-cb50-8cd8ccb8930b",
    "f695d0c6-9dea-237d-111d-fa9b35a19904",
    "2532e7d9-ca3b-4060-b992-a1da84404023",
    "4e9ec4dc-7f7d-4cef-9266-a4bef754996e"
]

# Görevleri gruplayarak paralel çalıştırma
job = group(fetch_data.s(company_id) for company_id in ids)
result = job.apply_async()

result.join()  # Tüm görevlerin tamamlanmasını sağlama

print("Tüm görevler tamamlandı.")
